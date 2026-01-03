# config.py

TICKERS = [
    # ---- Broad Market ----
    "SPY",   # S&P 500 benchmark
    "QQQ",   # Tech-heavy index

    # ---- Technology ----
    "AAPL",  # Large-cap tech
    "MSFT",  # Enterprise tech
    "NVDA",  # High-volatility growth

    # ---- Financials ----
    "JPM",   # Bank
    "GS",    # Investment banking

    # ---- Energy ----
    "XOM",   # Oil major

    # ---- Healthcare ----
    "JNJ",   # Defensive healthcare
    "PFE",   # Pharma

    # ---- Consumer ----
    "AMZN",  # Consumer + cloud
    "KO",    # Defensive consumer staples

    # ---- Industrials ----
    "CAT",   # Cyclical industrials
]

TOTAL_CAPITAL = 10.0
AI_CAPITAL = 10

MAX_POSITION_PCT = 0.20   # 20% per trade
DECISION_INTERVAL_MIN = 5
MAX_TRADES_PER_DAY = 5

MARKET_TIMEZONE = "US/Eastern"
