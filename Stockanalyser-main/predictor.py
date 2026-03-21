"""
predictor.py — ML models for stock price prediction.

Models:
  1. RandomForestRegressor  — ensemble baseline (fast, interpretable)
  2. LSTM Neural Network     — sequential model for time-series (optional, needs torch)

Both take sentiment + technical features as input → predict next-day closing price.
"""

import warnings
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler

import config
from utils import logger

warnings.filterwarnings("ignore", category=UserWarning)


# ═══════════════════════════════════════════════════════════════
# RandomForest Model
# ═══════════════════════════════════════════════════════════════

FEATURE_COLS = [
    "Close", "Volume", "sma_5", "sma_10",
    "daily_return", "volatility", "price_range",
    "volume_sma5", "rsi_14", "sentiment_score",
]


def train_random_forest(df: pd.DataFrame) -> Dict:
    """
    Train a RandomForestRegressor to predict next-day closing price.

    Args:
        df: Feature DataFrame from financial_data.prepare_features()

    Returns:
        Dict with: model, prediction, current_price, metrics, feature_importance
    """
    logger.info("Training RandomForest model...")

    # Select available features
    available = [c for c in FEATURE_COLS if c in df.columns]
    if len(available) < 3:
        logger.error("Not enough features for training")
        return {}

    X = df[available].values
    y = df["next_close"].values

    # Train/test split (time-series — NO shuffle)
    split_idx = int(len(X) * (1 - config.TEST_SIZE))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    if len(X_train) < 5 or len(X_test) < 2:
        logger.warning("Insufficient data for reliable train/test split. Using all data for training.")
        X_train, y_train = X, y
        X_test, y_test = X[-3:], y[-3:]

    # Train
    model = RandomForestRegressor(
        n_estimators=config.RF_N_ESTIMATORS,
        max_depth=config.RF_MAX_DEPTH,
        random_state=config.RF_RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Feature importance
    importance = dict(zip(available, model.feature_importances_))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

    # Predict next-day close using latest data point
    latest_features = X[-1:].copy()
    predicted_price = float(model.predict(latest_features)[0])
    current_price = float(df["Close"].iloc[-1])

    logger.info(f"  MAE: ${mae:.2f} | RMSE: ${rmse:.2f}")
    logger.info(f"  Prediction: ${predicted_price:.2f} (Current: ${current_price:.2f})")

    return {
        "model_name": "RandomForest",
        "model": model,
        "predicted_price": predicted_price,
        "current_price": current_price,
        "change_pct": ((predicted_price - current_price) / current_price) * 100,
        "metrics": {"mae": round(mae, 4), "rmse": round(rmse, 4)},
        "feature_importance": importance,
        "train_size": len(X_train),
        "test_size": len(X_test),
    }


# ═══════════════════════════════════════════════════════════════
# LSTM Model
# ═══════════════════════════════════════════════════════════════

def train_lstm(df: pd.DataFrame) -> Dict:
    """
    Train an LSTM neural network for next-day price prediction.

    Uses a sliding window of LSTM_LOOKBACK days as input sequences.

    Args:
        df: Feature DataFrame from financial_data.prepare_features()

    Returns:
        Dict with: model, prediction, current_price, metrics
    """
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError:
        logger.warning("PyTorch not installed — skipping LSTM model")
        return {}

    logger.info("Training LSTM model...")

    # Select features
    available = [c for c in FEATURE_COLS if c in df.columns]
    data = df[available + ["next_close"]].values.astype(np.float32)

    # Scale data
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    X_scaled = scaler_X.fit_transform(data[:, :-1])
    y_scaled = scaler_y.fit_transform(data[:, -1:])

    # Create sequences
    lookback = config.LSTM_LOOKBACK
    X_seq, y_seq = [], []
    for i in range(lookback, len(X_scaled)):
        X_seq.append(X_scaled[i - lookback : i])
        y_seq.append(y_scaled[i])

    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)

    if len(X_seq) < 5:
        logger.warning("Not enough sequential data for LSTM training")
        return {}

    # Split
    split_idx = int(len(X_seq) * (1 - config.TEST_SIZE))
    X_train = torch.FloatTensor(X_seq[:split_idx])
    y_train = torch.FloatTensor(y_seq[:split_idx])
    X_test = torch.FloatTensor(X_seq[split_idx:])
    y_test_np = y_seq[split_idx:]

    # Define LSTM
    class StockLSTM(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
            self.fc = nn.Sequential(
                nn.Linear(hidden_size, 32),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(32, 1),
            )

        def forward(self, x):
            lstm_out, _ = self.lstm(x)
            return self.fc(lstm_out[:, -1, :])

    input_size = X_train.shape[2]
    model = StockLSTM(input_size, config.LSTM_HIDDEN_SIZE, config.LSTM_NUM_LAYERS)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LSTM_LEARNING_RATE)

    # Train
    dataset = TensorDataset(X_train, y_train)
    loader = DataLoader(dataset, batch_size=config.LSTM_BATCH_SIZE, shuffle=False)

    model.train()
    for epoch in range(config.LSTM_EPOCHS):
        epoch_loss = 0.0
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            avg_loss = epoch_loss / len(loader)
            logger.info(f"  Epoch {epoch + 1}/{config.LSTM_EPOCHS} — Loss: {avg_loss:.6f}")

    # Evaluate
    model.eval()
    with torch.no_grad():
        y_pred_scaled = model(X_test).numpy()

    y_pred = scaler_y.inverse_transform(y_pred_scaled)
    y_actual = scaler_y.inverse_transform(y_test_np)

    mae = mean_absolute_error(y_actual, y_pred)
    rmse = np.sqrt(mean_squared_error(y_actual, y_pred))

    # Predict next day
    latest_seq = torch.FloatTensor(X_scaled[-lookback:].reshape(1, lookback, -1))
    with torch.no_grad():
        next_pred_scaled = model(latest_seq).numpy()
    predicted_price = float(scaler_y.inverse_transform(next_pred_scaled)[0, 0])
    current_price = float(df["Close"].iloc[-1])

    logger.info(f"  MAE: ${mae:.2f} | RMSE: ${rmse:.2f}")
    logger.info(f"  Prediction: ${predicted_price:.2f} (Current: ${current_price:.2f})")

    return {
        "model_name": "LSTM",
        "model": model,
        "predicted_price": predicted_price,
        "current_price": current_price,
        "change_pct": ((predicted_price - current_price) / current_price) * 100,
        "metrics": {"mae": round(mae, 4), "rmse": round(rmse, 4)},
        "feature_importance": {},
        "train_size": len(X_train),
        "test_size": len(X_test),
    }


# ═══════════════════════════════════════════════════════════════
# Ensemble
# ═══════════════════════════════════════════════════════════════

def ensemble_predict(rf_result: Dict, lstm_result: Dict, weights: Tuple[float, float] = (0.5, 0.5)) -> Dict:
    """
    Combine RandomForest and LSTM predictions via weighted average.
    
    Falls back to single model if one is unavailable.
    """
    if rf_result and lstm_result:
        w_rf, w_lstm = weights
        predicted = w_rf * rf_result["predicted_price"] + w_lstm * lstm_result["predicted_price"]
        current = rf_result["current_price"]
        return {
            "model_name": f"Ensemble (RF:{w_rf:.0%} + LSTM:{w_lstm:.0%})",
            "predicted_price": predicted,
            "current_price": current,
            "change_pct": ((predicted - current) / current) * 100,
            "metrics": {
                "rf_mae": rf_result["metrics"]["mae"],
                "lstm_mae": lstm_result["metrics"]["mae"],
            },
        }
    elif rf_result:
        return rf_result
    elif lstm_result:
        return lstm_result
    else:
        return {}


# ─── Quick Test ───────────────────────────────────────────────
if __name__ == "__main__":
    from financial_data import fetch_price_data, prepare_features
    from sentiment_analyzer import analyze_sentiment

    # Generate dummy sentiment
    price_df = fetch_price_data("AAPL")
    dummy_sentiment = pd.DataFrame({
        "date": price_df["date"],
        "sentiment_score": np.random.uniform(-0.5, 0.5, len(price_df)),
    })
    features = prepare_features(price_df, dummy_sentiment)

    rf = train_random_forest(features)
    if rf:
        print(f"\nRandomForest → ${rf['predicted_price']:.2f} ({rf['change_pct']:+.2f}%)")

    lstm = train_lstm(features)
    if lstm:
        print(f"LSTM         → ${lstm['predicted_price']:.2f} ({lstm['change_pct']:+.2f}%)")
