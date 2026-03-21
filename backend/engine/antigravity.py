import pandas as pd
import numpy as np

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate moving averages, RSI, and Bollinger Bands used by the Engine."""
    # Ensure dataframe is sorted by Date
    df = df.copy()
    
    # 1. Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # 2. Bollinger Bands
    df['std_20'] = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['SMA_20'] + (df['std_20'] * 2)
    df['BB_lower'] = df['SMA_20'] - (df['std_20'] * 2)
    
    # 3. RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 4. Momentum (ROC - Rate of Change 10 period)
    df['ROC_10'] = df['Close'].pct_change(periods=10) * 100

    return df

def detect_gravity(df: pd.DataFrame) -> dict:
    """
    Antigravity Detection Engine.
    Evaluates MA divergence, volatility, and momentum to output a Gravity Status.
    
    Returns:
        dict with status ('Stable Gravity', 'Low Gravity', 'Antigravity Detected')
        and supporting metrics.
    """
    if df.empty or len(df) < 50:
        return {"status": "Insufficient Data", "reason": "Need 50+ days."}
        
    latest = df.iloc[-1]
    
    # Extract latest metrics
    close = latest['Close']
    sma20 = latest['SMA_20']
    bb_upper = latest['BB_upper']
    rsi = latest['RSI']
    roc = latest['ROC_10']

    # Divergence and Edge-riding logic
    # Antigravity happens when stock breaks upper BB wildly with high RSI and strong ROC
    is_above_upper_bb = close > bb_upper
    is_high_momentum = roc > 10.0  # 10% jump in 10 days
    is_overbought_rsi = rsi > 70
    
    # Low Gravity: approaching breakout, high momentum but not necessarily shattering the band
    is_approaching_upper_bb = close > sma20 and close > (bb_upper * 0.98)
    
    if is_above_upper_bb and is_high_momentum and is_overbought_rsi:
        status = "Antigravity Detected"
        msg = f"Stock is accelerating parabolically above bounds (RSI: {rsi:.1f}, ROC: {roc:.1f}%)."
    elif is_approaching_upper_bb and rsi > 60:
        status = "Low Gravity"
        msg = f"Stock is lifting off moving averages. Preparing for potential breakout."
    else:
        status = "Stable Gravity"
        msg = "Stock is constrained by normal market forces and moving averages."
        
    return {
        "status": status,
        "metrics": {
            "rsi": rsi,
            "roc_10": roc,
            "distance_to_sma20_pct": ((close - sma20)/sma20) * 100
        },
        "explanation": msg
    }
