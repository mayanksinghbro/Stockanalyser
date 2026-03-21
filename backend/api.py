from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import yfinance as yf
import pandas as pd
import uvicorn
import os
import datetime

from engine.antigravity import calculate_technical_indicators, detect_gravity
from engine.models import get_predictions
from engine.xai import generate_shap_stubs
from engine.nse_symbols import search_symbols, get_symbol_list

app = FastAPI(title="NSE Antigravity Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/search")
def search_nse(q: str = "", limit: int = 10):
    """
    Autocomplete search for NSE stock symbols and company names.
    Returns up to `limit` matching results.
    """
    results = search_symbols(q, limit=limit)
    return {"results": results}


@app.get("/api/symbols")
def list_symbols():
    """Returns the full cached NSE symbol list (refreshes every 24h)."""
    return {"symbols": get_symbol_list()}


@app.get("/api/analyze")
async def analyze_stock(ticker: str):
    """
    Analyzes an NSE stock using the Antigravity Engine.
    Assumes ticker is passed in (e.g., RELIANCE.NS, TCS.NS).
    If no .NS is appended, we try appending it automatically.
    """
    if not ticker.endswith(".NS") and not ticker.endswith(".BO") and not ticker.endswith(".BO"):
        ticker = f"{ticker.upper()}.NS"
    else:
        ticker = ticker.upper()

    try:
        # 1. Fetch data
        print(f"Fetching data for {ticker}...")
        stock = yf.Ticker(ticker)
        
        # Get 1 year of daily historical data
        hist_df = stock.history(period="1y")
        if hist_df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

        # Drop timezone aware to simplify
        if hist_df.index.tz is not None:
            hist_df.index = hist_df.index.tz_localize(None)

        # 2. Process Technicals
        df = calculate_technical_indicators(hist_df)
        
        # 3. Detect Gravity
        gravity_data = detect_gravity(df)
        
        # 4. Generate Predictions
        prediction_data = get_predictions(df)
        
        # 5. XAI Explainability Stubs
        xai_data = generate_shap_stubs(prediction_data["model"], {})
        
        # Current data
        current_price = float(df['Close'].iloc[-1])
        vol_avg = float(df['Volume'].mean())
        
        # Make a cleaned chart data array for the last 90 days for the frontend
        chart_data = df.tail(90).reset_index()
        chart_json = chart_data[['Date', 'Close', 'SMA_20', 'BB_upper', 'BB_lower']].to_dict(orient="records")
        for c in chart_json:
            c['Date'] = c['Date'].isoformat()
            c['SMA_20'] = None if pd.isna(c['SMA_20']) else c['SMA_20']
            c['BB_upper'] = None if pd.isna(c['BB_upper']) else c['BB_upper']
            c['BB_lower'] = None if pd.isna(c['BB_lower']) else c['BB_lower']

        return {
            "ticker": ticker,
            "company_name": stock.info.get('shortName', ticker),
            "current_price": current_price,
            "avg_volume": vol_avg,
            "gravity": gravity_data,
            "prediction": prediction_data,
            "xai_insights": xai_data,
            "chart_data": chart_json,
            "analyzed_at": datetime.datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
