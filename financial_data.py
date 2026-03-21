"""
financial_data.py — Pull historical price data and compute technical indicators.

Uses yfinance for OHLCV data and adds derived features for model input.
"""

from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import yfinance as yf

import config
from utils import logger


def fetch_price_data(
    ticker: str,
    lookback_days: Optional[int] = None,
) -> pd.DataFrame:
    """
    Download historical OHLCV data for the given ticker.

    Args:
        ticker: Stock symbol (e.g., "AAPL")
        lookback_days: Number of calendar days to look back (default from config)

    Returns:
        DataFrame with columns: [Open, High, Low, Close, Volume, date]
    """
    if lookback_days is None:
        lookback_days = config.LOOKBACK_DAYS

    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days + 15)  # buffer for weekends/holidays

    logger.info(f"Fetching {ticker} price data ({lookback_days}-day window)...")

    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)

    if df.empty:
        logger.error(f"No price data returned for {ticker}")
        return pd.DataFrame()

    # Keep only needed columns and reset index
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = df.index.tz_localize(None)  # Remove timezone for easier merging
    df = df.reset_index()
    df = df.rename(columns={"Date": "date"})
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()

    # Trim to exact lookback window (trading days)
    df = df.tail(lookback_days).reset_index(drop=True)

    logger.info(f"  Retrieved {len(df)} trading days ({df['date'].iloc[0].date()} → {df['date'].iloc[-1].date()})")
    return df


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute technical features from OHLCV data.

    Added columns:
        - sma_5:       5-day Simple Moving Average
        - sma_10:      10-day Simple Moving Average
        - daily_return: Day-over-day percentage change
        - volatility:  5-day rolling standard deviation of returns
        - price_range: (High - Low) / Close — intraday range
        - volume_sma5: 5-day rolling mean of volume
        - rsi_14:      14-period Relative Strength Index
    """
    df = df.copy()

    # Moving Averages
    df["sma_5"] = df["Close"].rolling(window=5).mean()
    df["sma_10"] = df["Close"].rolling(window=10).mean()

    # Daily Return
    df["daily_return"] = df["Close"].pct_change()

    # Volatility (rolling std of returns)
    df["volatility"] = df["daily_return"].rolling(window=5).std()

    # Price Range (intraday)
    df["price_range"] = (df["High"] - df["Low"]) / df["Close"]

    # Volume Moving Average
    df["volume_sma5"] = df["Volume"].rolling(window=5).mean()

    # RSI (14-period)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi_14"] = 100 - (100 / (1 + rs))

    logger.info(f"  Added 7 technical indicators")
    return df


def prepare_features(
    price_df: pd.DataFrame,
    sentiment_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge price data with daily sentiment and prepare the final feature set.

    Args:
        price_df: OHLCV + indicators from add_technical_indicators()
        sentiment_df: Daily sentiment from sentiment_analyzer.analyze_sentiment()

    Returns:
        Merged DataFrame with target column 'next_close' (next day's close).
    """
    df = price_df.copy()

    # Add technical indicators if not already present
    if "sma_5" not in df.columns:
        df = add_technical_indicators(df)

    # Merge sentiment (left join — keep all price days, fill missing sentiment with 0)
    if not sentiment_df.empty and "date" in sentiment_df.columns:
        sentiment_df = sentiment_df.copy()
        sentiment_df["date"] = pd.to_datetime(sentiment_df["date"]).dt.normalize()
        df = df.merge(sentiment_df[["date", "sentiment_score"]], on="date", how="left")
    else:
        df["sentiment_score"] = 0.0

    df["sentiment_score"] = df["sentiment_score"].fillna(0.0)

    # Target: next day's closing price
    df["next_close"] = df["Close"].shift(-1)

    # Drop rows with NaN (from rolling calculations and target shift)
    df = df.dropna().reset_index(drop=True)

    logger.info(f"  Final feature set: {len(df)} samples × {len(df.columns)} columns")
    return df


def get_current_price(ticker: str) -> float:
    """Get the most recent closing price."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d")
    if hist.empty:
        logger.warning(f"Could not fetch current price for {ticker}")
        return 0.0
    return float(hist["Close"].iloc[-1])


# ─── Quick Test ───────────────────────────────────────────────
if __name__ == "__main__":
    df = fetch_price_data("AAPL")
    df = add_technical_indicators(df)
    print("\nPrice Data (last 5 rows):")
    print(df.tail().to_string(index=False))
    print(f"\nCurrent AAPL Price: ${get_current_price('AAPL'):.2f}")
