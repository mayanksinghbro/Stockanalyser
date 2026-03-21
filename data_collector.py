"""
data_collector.py — Scrape recent financial news headlines for a stock ticker.

Uses Google News RSS and Yahoo Finance RSS as sources.
Falls back gracefully if one source is unavailable.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

import config
from utils import logger


def _clean_headline(text: str) -> str:
    """Remove HTML entities, extra whitespace, and source suffixes."""
    text = re.sub(r"<[^>]+>", "", text)             # strip HTML tags
    text = re.sub(r"\s+", " ", text).strip()         # collapse whitespace
    text = re.sub(r"\s*-\s*[A-Za-z\s]+$", "", text)  # remove " - Source Name"
    return text


def _parse_rss_date(date_str: str) -> Optional[datetime]:
    """Try multiple date formats common in RSS feeds."""
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%a, %d %b %Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def scrape_news(ticker: str, max_articles: int = None) -> List[Dict]:
    """
    Scrape recent news headlines for the given ticker from RSS feeds.

    Returns:
        List of dicts: [{"title": str, "published": datetime|None, "source": str}]
    """
    if max_articles is None:
        max_articles = config.MAX_NEWS_ARTICLES

    headers = {"User-Agent": config.USER_AGENT}
    all_articles = []

    for feed_url_template in config.NEWS_RSS_FEEDS:
        feed_url = feed_url_template.format(ticker=ticker)
        logger.info(f"Fetching news from: {feed_url[:80]}...")

        try:
            response = requests.get(
                feed_url,
                headers=headers,
                timeout=config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {feed_url[:50]}...: {e}")
            continue

        soup = BeautifulSoup(response.content, "lxml-xml")
        items = soup.find_all("item")

        if not items:
            # Fallback: try HTML parser for non-standard RSS
            soup = BeautifulSoup(response.content, "html.parser")
            items = soup.find_all("item")

        logger.info(f"  Found {len(items)} articles")

        for item in items:
            title_tag = item.find("title")
            pub_date_tag = item.find("pubDate") or item.find("published")
            source_tag = item.find("source")

            if not title_tag or not title_tag.text.strip():
                continue

            headline = _clean_headline(title_tag.text)

            # Skip headlines that are too short or don't seem relevant
            if len(headline) < 10:
                continue

            pub_date = None
            if pub_date_tag and pub_date_tag.text:
                pub_date = _parse_rss_date(pub_date_tag.text)

            source = source_tag.text.strip() if source_tag and source_tag.text else "Unknown"

            all_articles.append({
                "title": headline,
                "published": pub_date,
                "source": source,
            })

    # Deduplicate by headline
    seen = set()
    unique_articles = []
    for article in all_articles:
        key = article["title"].lower()
        if key not in seen:
            seen.add(key)
            unique_articles.append(article)

    # Sort by date (most recent first), handling None dates
    unique_articles.sort(
        key=lambda x: x["published"] or datetime.min,
        reverse=True,
    )

    # Cap at max_articles
    result = unique_articles[:max_articles]
    logger.info(f"Collected {len(result)} unique headlines for {ticker}")
    return result


def get_headlines_text(articles: List[Dict]) -> List[str]:
    """Extract just the headline text from article dicts."""
    return [a["title"] for a in articles]


# ─── Quick Test ───────────────────────────────────────────────
if __name__ == "__main__":
    articles = scrape_news("AAPL")
    for i, article in enumerate(articles[:10], 1):
        date_str = article["published"].strftime("%Y-%m-%d") if article["published"] else "N/A"
        print(f"  {i:2d}. [{date_str}] {article['title']}")
