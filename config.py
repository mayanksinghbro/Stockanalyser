"""
config.py — Central configuration for the Stock Predictor.
Adjust these parameters to tune scraping, analysis, and model behavior.
"""

# ─── Default Ticker ───────────────────────────────────────────
DEFAULT_TICKER = "AAPL"

# ─── Data Collection ──────────────────────────────────────────
LOOKBACK_DAYS = 60                       # Historical price window
MAX_NEWS_ARTICLES = 50                   # Cap on scraped headlines
REQUEST_TIMEOUT = 10                     # Seconds before HTTP timeout
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# RSS feed templates — {ticker} is replaced at runtime
NEWS_RSS_FEEDS = [
    "https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en",
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
]

# ─── Sentiment Analysis ──────────────────────────────────────
USE_FINBERT = False                      # Set True to use HuggingFace FinBERT (slower, more accurate)
FINBERT_MODEL = "ProsusAI/finbert"       # HuggingFace model ID

# ─── Model Parameters ────────────────────────────────────────
# RandomForest
RF_N_ESTIMATORS = 200
RF_MAX_DEPTH = 10
RF_RANDOM_STATE = 42

# LSTM
LSTM_LOOKBACK = 10                       # Days of history per sample
LSTM_HIDDEN_SIZE = 64
LSTM_NUM_LAYERS = 2
LSTM_EPOCHS = 50
LSTM_LEARNING_RATE = 0.001
LSTM_BATCH_SIZE = 16

# Train/Test split
TEST_SIZE = 0.20

# ─── Output ───────────────────────────────────────────────────
DECIMAL_PLACES = 2
