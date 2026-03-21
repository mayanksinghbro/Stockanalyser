# 📈 AI Stock Price Predictor

A Python-based stock predictor that combines **web-scraped news sentiment** with **historical price data** and **machine learning** to predict the next day's closing price.

## Architecture

```
News Headlines (RSS)  ─→  Sentiment Analysis (VADER / FinBERT)  ─┐
                                                                   ├──→  ML Prediction  ──→  Upside / Downside %
Historical Prices (yfinance)  ─→  Technical Indicators  ──────────┘
```

## Components

| Module | Purpose |
|---|---|
| `data_collector.py` | Scrapes Google/Yahoo News RSS feeds for stock headlines |
| `sentiment_analyzer.py` | VADER (fast) or FinBERT (accurate) sentiment scoring |
| `financial_data.py` | yfinance OHLCV data + 7 technical indicators |
| `predictor.py` | RandomForest + LSTM models with ensemble averaging |
| `main.py` | CLI orchestrator with formatted output |
| `config.py` | All tunable parameters in one place |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run with default ticker (AAPL)
python main.py

# 3. Run with a specific ticker
python main.py --ticker MSFT

# 4. Use FinBERT for better sentiment analysis (requires GPU for speed)
python main.py --ticker TSLA --finbert

# 5. Fast mode — skip LSTM, use RandomForest only
python main.py --ticker GOOGL --no-lstm
```

## Features Used by the Model

**Technical Indicators:**
- 5-day & 10-day Simple Moving Averages (SMA)
- Daily returns & 5-day rolling volatility
- Intraday price range
- Volume moving average
- 14-period RSI

**Sentiment:**
- Compound sentiment score from news headlines (daily aggregate)

## Configuration

Edit `config.py` to tune:
- Default ticker and lookback period
- RSS feed sources
- VADER vs FinBERT toggle
- RandomForest hyperparameters (estimators, depth)
- LSTM hyperparameters (layers, hidden size, epochs, learning rate)

## Sample Output

```
══════════════════════════════════════════════════════════════
║                   STOCK PREDICTOR — AAPL                  ║
══════════════════════════════════════════════════════════════

── 5 · Prediction Results ─────────────────────────────────

  RandomForest
    Predicted Close:  $198.45
    Signal:           ▲ UPSIDE  +1.23%
    MAE:  $2.15   RMSE: $3.02

  LSTM
    Predicted Close:  $197.80
    Signal:           ▲ UPSIDE  +0.90%
    MAE:  $2.50   RMSE: $3.45

  Ensemble (RF:50% + LSTM:50%)
    Predicted Close:  $198.13
    Signal:           ▲ UPSIDE  +1.07%
```

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. It is not financial advice. Past performance does not guarantee future results. Always do your own research before making investment decisions.
