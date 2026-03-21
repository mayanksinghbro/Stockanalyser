"""
main.py — CLI orchestrator for the Stock Price Predictor.

Pipeline:
  1. Scrape news headlines for the given ticker
  2. Analyze sentiment (VADER or FinBERT)
  3. Fetch historical price data (yfinance)
  4. Merge features and train prediction models
  5. Output formatted prediction with upside/downside estimate
"""

import argparse
import sys

import pandas as pd

import config
from data_collector import scrape_news
from financial_data import fetch_price_data, add_technical_indicators, prepare_features
from predictor import train_random_forest, train_lstm, ensemble_predict
from sentiment_analyzer import analyze_sentiment, get_overall_sentiment
from utils import (
    logger, bold, cyan, green, red, yellow, dim,
    format_price, format_percent,
    print_header, print_section, print_kv, print_divider,
)


def run_pipeline(ticker: str, use_finbert: bool = False, skip_lstm: bool = False):
    """Execute the full prediction pipeline."""

    print_header(f"STOCK PREDICTOR — {ticker.upper()}")

    # ── Step 1: Collect News ──────────────────────────────────
    print_section("1 · News Collection")
    articles = scrape_news(ticker)

    if articles:
        print_kv("Headlines found", str(len(articles)))
        print()
        for i, article in enumerate(articles[:5], 1):
            date_str = article["published"].strftime("%m/%d") if article["published"] else "N/A"
            source = article["source"]
            print(f"    {dim(f'{i}.')} {article['title'][:75]}")
            print(f"       {dim(f'[{date_str}] via {source}')}")
    else:
        logger.warning("No news articles found. Proceeding with price data only.")

    # ── Step 2: Sentiment Analysis ────────────────────────────
    print_section("2 · Sentiment Analysis")

    if articles:
        daily_sentiment = analyze_sentiment(articles, use_finbert=use_finbert)
        overall_sentiment = get_overall_sentiment(articles, use_finbert=use_finbert)

        engine = "FinBERT" if use_finbert else "VADER"
        print_kv("Engine", engine)
        print_kv("Overall Score", f"{overall_sentiment:+.4f}")

        # Interpret
        if overall_sentiment > 0.2:
            sentiment_label = green("Bullish 📈")
        elif overall_sentiment < -0.2:
            sentiment_label = red("Bearish 📉")
        else:
            sentiment_label = yellow("Neutral ➡️")
        print_kv("Market Mood", sentiment_label)
    else:
        daily_sentiment = pd.DataFrame(columns=["date", "sentiment_score"])
        overall_sentiment = 0.0
        print_kv("Market Mood", dim("N/A (no news data)"))

    # ── Step 3: Financial Data ────────────────────────────────
    print_section("3 · Historical Price Data")

    price_df = fetch_price_data(ticker)
    if price_df.empty:
        print(red("\n  ✗ Could not fetch price data. Exiting."))
        sys.exit(1)

    price_df = add_technical_indicators(price_df)
    current_price = float(price_df["Close"].iloc[-1])

    print_kv("Trading Days", str(len(price_df)))
    print_kv("Current Price", format_price(current_price))
    print_kv("52-Day High", format_price(price_df["Close"].max()))
    print_kv("52-Day Low", format_price(price_df["Close"].min()))
    print_kv("Avg Volume", f"{price_df['Volume'].mean():,.0f}")

    # ── Step 4: Merge Features & Train Models ─────────────────
    print_section("4 · Model Training")

    features_df = prepare_features(price_df, daily_sentiment)

    if features_df.empty or len(features_df) < 10:
        print(red("\n  ✗ Not enough data to train models. Need at least 10 data points."))
        sys.exit(1)

    # RandomForest (always runs)
    rf_result = train_random_forest(features_df)

    # LSTM (optional)
    lstm_result = {}
    if not skip_lstm:
        lstm_result = train_lstm(features_df)

    # Ensemble
    ensemble = ensemble_predict(rf_result, lstm_result)

    # ── Step 5: Output Results ────────────────────────────────
    print_section("5 · Prediction Results")
    print()

    results = []
    if rf_result:
        results.append(rf_result)
    if lstm_result:
        results.append(lstm_result)
    if rf_result and lstm_result:
        results.append(ensemble)

    for r in results:
        name = r["model_name"]
        pred = r["predicted_price"]
        change = r["change_pct"]
        direction = green("▲ UPSIDE") if change >= 0 else red("▼ DOWNSIDE")

        print(f"  {bold(name)}")
        print(f"    Predicted Close:  {bold(format_price(pred))}")
        print(f"    Signal:           {direction}  {format_percent(change)}")
        if "mae" in r.get("metrics", {}):
            print(f"    MAE:  {format_price(r['metrics']['mae'])}   RMSE: {format_price(r['metrics']['rmse'])}")
        print()

    # ── Summary Box ───────────────────────────────────────────
    best = ensemble if ensemble else (rf_result if rf_result else lstm_result)
    if best:
        change = best["change_pct"]
        signal = "UPSIDE" if change >= 0 else "DOWNSIDE"
        arrow = "📈" if change >= 0 else "📉"
        color = green if change >= 0 else red

        print(cyan("═" * 60))
        print(cyan("║") + bold("  SUMMARY".ljust(58)) + cyan("║"))
        print(cyan("═" * 60))
        print(f"  Ticker:           {bold(ticker.upper())}")
        print(f"  Current Price:    {bold(format_price(current_price))}")
        print(f"  Predicted Price:  {bold(format_price(best['predicted_price']))}")
        print(f"  Sentiment:        {overall_sentiment:+.4f}")
        print(f"  {arrow} Expected {signal}:  {color(bold(f'{abs(change):.2f}%'))}")
        print(cyan("═" * 60))
        print()
        print(dim("  ⚠  Disclaimer: This is a ML-based estimate, not financial advice."))
        print(dim("     Past performance does not guarantee future results."))
        print()


def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Stock Price Predictor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     # Predict AAPL (default)
  python main.py --ticker MSFT       # Predict Microsoft
  python main.py --ticker TSLA --finbert   # Use FinBERT sentiment
  python main.py --ticker GOOGL --no-lstm  # Skip LSTM, RandomForest only
        """,
    )
    parser.add_argument(
        "--ticker", "-t",
        type=str,
        default=config.DEFAULT_TICKER,
        help=f"Stock ticker symbol (default: {config.DEFAULT_TICKER})",
    )
    parser.add_argument(
        "--finbert",
        action="store_true",
        default=False,
        help="Use FinBERT transformer for sentiment (slower but more accurate)",
    )
    parser.add_argument(
        "--no-lstm",
        action="store_true",
        default=False,
        help="Skip LSTM model training (faster execution)",
    )

    args = parser.parse_args()
    run_pipeline(
        ticker=args.ticker.upper(),
        use_finbert=args.finbert,
        skip_lstm=args.no_lstm,
    )


if __name__ == "__main__":
    main()
