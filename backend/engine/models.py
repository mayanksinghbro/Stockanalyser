import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import prophet conditionally or use a stub if not installed yet for quick proto
try:
    from prophet import Prophet
except ImportError:
    Prophet = None

def run_regression_stub(df: pd.DataFrame, days_ahead=5):
    """
    A simple linear regression / mock prediction fallback 
    if heavy ML like Prophet/LSTM isn't loaded.
    """
    if len(df) < 20:
        return 0, 0
    
    recent_trend = df['Close'].pct_change(periods=5).mean()
    last_price = df['Close'].iloc[-1]
    
    # Predict T+5
    predicted_future = last_price * (1 + (recent_trend * days_ahead))
    change_pct = ((predicted_future - last_price) / last_price) * 100
    return predicted_future, change_pct

def run_prophet_model(df: pd.DataFrame, days_ahead=5):
    """
    Use Facebook Prophet for time series forecasting.
    """
    if Prophet is None:
        return run_regression_stub(df, days_ahead)
        
    pr_df = df.reset_index()[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
    
    # Remove timezone info for Prophet if present
    if pr_df['ds'].dt.tz is not None:
        pr_df['ds'] = pr_df['ds'].dt.tz_localize(None)

    m = Prophet(daily_seasonality=False, yearly_seasonality=True)
    m.fit(pr_df)
    
    future = m.make_future_dataframe(periods=days_ahead)
    # Filter out weekends (crude approximation for trading days)
    future = future[future['ds'].dt.dayofweek < 5]
    
    forecast = m.predict(future)
    predicted_price = forecast['yhat'].iloc[-1]
    last_price = df['Close'].iloc[-1]
    
    change_pct = ((predicted_price - last_price) / last_price) * 100
    
    return predicted_price, change_pct

def get_predictions(df: pd.DataFrame):
    """Aggregator for ML predictions."""
    try:
        p_price, p_change = run_prophet_model(df)
        return {
            "model": "Prophet",
            "predicted_price": p_price,
            "change_pct": p_change
        }
    except Exception as e:
        print(f"Prophet error: {e}")
        p_price, p_change = run_regression_stub(df)
        return {
            "model": "Linear Regression (Fallback)",
            "predicted_price": p_price,
            "change_pct": p_change
        }
