from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pandas as pd
from typing import Optional

# Import functions from existing pipeline
from data_collector import scrape_news
from sentiment_analyzer import analyze_sentiment, get_overall_sentiment
from financial_data import fetch_price_data, add_technical_indicators, prepare_features
from predictor import train_random_forest, train_lstm, ensemble_predict
import config

app = FastAPI(title="Stock Predictor API")

# Add CORS middleware to allow the Vite frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/api/predict")
async def predict_stock(ticker: str, use_finbert: bool = False, skip_lstm: bool = False):
    """
    Run the prediction pipeline for a given ticker and return JSON results.
    """
    ticker = ticker.upper()
    try:
        # 1. Collect News
        articles = scrape_news(ticker)

        if articles:
            daily_sentiment = analyze_sentiment(articles, use_finbert=use_finbert)
            overall_sentiment = get_overall_sentiment(articles, use_finbert=use_finbert)
            
            # Format articles for JSON output (limit to 5)
            formatted_articles = []
            for a in articles[:5]:
                formatted_articles.append({
                    "title": a["title"],
                    "source": a["source"],
                    "published": a["published"].isoformat() if a.get("published") else None
                })
        else:
            daily_sentiment = pd.DataFrame(columns=["date", "sentiment_score"])
            overall_sentiment = 0.0
            formatted_articles = []

        # 2. Financial Data
        price_df = fetch_price_data(ticker)
        if price_df.empty:
            raise HTTPException(status_code=404, detail=f"Could not fetch price data for {ticker}")

        price_df = add_technical_indicators(price_df)
        current_price = float(price_df["Close"].iloc[-1])
        high_52 = float(price_df["Close"].max())
        low_52 = float(price_df["Close"].min())
        avg_volume = float(price_df["Volume"].mean())

        # 3. Model Training
        features_df = prepare_features(price_df, daily_sentiment)

        if features_df.empty or len(features_df) < 10:
            raise HTTPException(status_code=400, detail="Not enough data to train models.")

        # RandomForest
        rf_result = train_random_forest(features_df)

        # LSTM
        lstm_result = {}
        if not skip_lstm:
            lstm_result = train_lstm(features_df)

        # Ensemble
        ensemble = ensemble_predict(rf_result, lstm_result)

        # Fix types for JSON serialization (numpy floats to native python floats)
        def clean_result(res):
            if not res: return None
            return {
                "model_name": res["model_name"],
                "predicted_price": float(res["predicted_price"]),
                "change_pct": float(res["change_pct"]),
                "metrics": {k: float(v) for k, v in res.get("metrics", {}).items()}
            }

        return {
            "ticker": ticker,
            "currentPrice": current_price,
            "high52": high_52,
            "low52": low_52,
            "avgVolume": avg_volume,
            "sentiment": overall_sentiment,
            "articles": formatted_articles,
            "rf": clean_result(rf_result),
            "lstm": clean_result(lstm_result),
            "ensemble": clean_result(ensemble)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
