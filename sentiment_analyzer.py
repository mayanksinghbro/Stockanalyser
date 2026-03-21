"""
sentiment_analyzer.py — Assign sentiment scores to financial news headlines.

Supports two engines:
  1. VADER (default) — fast, no GPU, good for short text
  2. FinBERT (optional) — HuggingFace transformer fine-tuned on financial text
"""

from datetime import datetime
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import config
from utils import logger


# ─── VADER Engine ─────────────────────────────────────────────
class VaderAnalyzer:
    """Lightweight sentiment using VADER's compound score."""

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def score(self, text: str) -> float:
        """Return compound sentiment score in [-1, 1]."""
        return self.analyzer.polarity_scores(text)["compound"]

    def score_batch(self, texts: List[str]) -> List[float]:
        return [self.score(t) for t in texts]


# ─── FinBERT Engine (Optional) ────────────────────────────────
class FinBERTAnalyzer:
    """
    Finance-specific sentiment using ProsusAI/finbert.
    Maps labels: positive → +1, negative → -1, neutral → 0.
    Final score is the weighted sum.
    """

    def __init__(self):
        try:
            from transformers import pipeline
            logger.info("Loading FinBERT model (this may take a moment)...")
            self.pipe = pipeline(
                "sentiment-analysis",
                model=config.FINBERT_MODEL,
                tokenizer=config.FINBERT_MODEL,
                top_k=None,            # return all label scores
                truncation=True,
                max_length=512,
            )
            logger.info("FinBERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load FinBERT: {e}")
            raise

    def score(self, text: str) -> float:
        """Return weighted sentiment score in [-1, 1]."""
        results = self.pipe(text)[0]
        label_map = {"positive": 1.0, "negative": -1.0, "neutral": 0.0}
        weighted = sum(
            r["score"] * label_map.get(r["label"], 0.0) for r in results
        )
        return round(weighted, 4)

    def score_batch(self, texts: List[str]) -> List[float]:
        return [self.score(t) for t in texts]


# ─── Factory ──────────────────────────────────────────────────
def get_analyzer(use_finbert: Optional[bool] = None):
    """Return the configured sentiment analyzer engine."""
    if use_finbert is None:
        use_finbert = config.USE_FINBERT

    if use_finbert:
        return FinBERTAnalyzer()
    return VaderAnalyzer()


# ─── Main Analysis Function ──────────────────────────────────
def analyze_sentiment(
    articles: List[Dict],
    use_finbert: Optional[bool] = None,
) -> pd.DataFrame:
    """
    Score each headline and aggregate daily sentiment.

    Args:
        articles: List of {"title": str, "published": datetime|None, ...}
        use_finbert: Override config setting for FinBERT usage

    Returns:
        DataFrame with columns: ['date', 'sentiment_score', 'num_articles']
    """
    engine_name = "FinBERT" if (use_finbert or config.USE_FINBERT) else "VADER"
    logger.info(f"Analyzing sentiment with {engine_name}...")
    analyzer = get_analyzer(use_finbert)

    # Score each headline
    scored = []
    for article in articles:
        score = analyzer.score(article["title"])
        scored.append({
            "title": article["title"],
            "published": article.get("published"),
            "sentiment_score": score,
        })

    df = pd.DataFrame(scored)

    if df.empty:
        logger.warning("No articles to analyze")
        return pd.DataFrame(columns=["date", "sentiment_score", "num_articles"])

    # Log score distribution
    mean_score = df["sentiment_score"].mean()
    logger.info(
        f"  Scores — Mean: {mean_score:.3f}, "
        f"Min: {df['sentiment_score'].min():.3f}, "
        f"Max: {df['sentiment_score'].max():.3f}"
    )

    # Aggregate by date
    df["date"] = pd.to_datetime(df["published"]).dt.date

    # Articles without a valid date get today's date
    today = datetime.now().date()
    df["date"] = df["date"].fillna(today)

    daily = (
        df.groupby("date")
        .agg(
            sentiment_score=("sentiment_score", "mean"),
            num_articles=("sentiment_score", "count"),
        )
        .reset_index()
    )

    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").reset_index(drop=True)

    logger.info(f"  Aggregated sentiment for {len(daily)} trading days")
    return daily


def get_overall_sentiment(articles: List[Dict], use_finbert: Optional[bool] = None) -> float:
    """Return a single overall sentiment score for all headlines."""
    analyzer = get_analyzer(use_finbert)
    if not articles:
        return 0.0
    scores = analyzer.score_batch([a["title"] for a in articles])
    return round(float(np.mean(scores)), 4)


# ─── Quick Test ───────────────────────────────────────────────
if __name__ == "__main__":
    test_headlines = [
        {"title": "Apple stock surges to all-time high on strong earnings", "published": datetime.now()},
        {"title": "Investors worried about Apple supply chain disruptions", "published": datetime.now()},
        {"title": "Apple announces new AI features for iPhone", "published": datetime.now()},
        {"title": "Market crash fears grow as tech stocks tumble", "published": datetime.now()},
        {"title": "Apple beats revenue expectations by wide margin", "published": datetime.now()},
    ]

    df = analyze_sentiment(test_headlines)
    print("\nDaily Sentiment:")
    print(df.to_string(index=False))

    overall = get_overall_sentiment(test_headlines)
    print(f"\nOverall Sentiment: {overall:.4f}")
