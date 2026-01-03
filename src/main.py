import time
from datetime import datetime
import pytz
from collections import deque
import pandas as pd

import config
from data import get_latest_data
from ai_strategy import compute_signals, score_signals
from broker import Broker
from risk import allowed_to_trade
from logger import log_decision


# -------------------------------------------------
# CONFIGURABLE LOGIC PARAMETERS
# -------------------------------------------------

SCORE_HISTORY_LENGTH = 50
MIN_HISTORY_FOR_TRADE = 20
UPPER_QUANTILE = 0.80
LOWER_QUANTILE = 0.20

CONFIDENCE_DECAY = 0.97
EXIT_DECAY_THRESHOLD = 0.25

MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0
CLOSE_BUFFER_MINUTES = 10
OVERNIGHT_HOLD_THRESHOLD = 0.6


# -------------------------------------------------
# STATE
# -------------------------------------------------

score_history = {
    ticker: deque(maxlen=SCORE_HISTORY_LENGTH)
    for ticker in config.TICKERS
}

entry_confidence = {}
entry_confidence_original = {}
last_trade_day = None


# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def get_market_prices(broker, latest_price, current_ticker):
    return {
        t: latest_price if t == current_ticker else broker.positions[t]["entry_price"]
        for t in broker.positions
    }

def get_last_price(df):
    return float(df["Close"].iloc[-1].item())

def minutes_to_market_close(now):
    close_time = now.replace(
        hour=MARKET_CLOSE_HOUR,
        minute=MARKET_CLOSE_MINUTE,
        second=0,
        microsecond=0
    )
    return (close_time - now).total_seconds() / 60

def is_near_market_close(now):
    return 0 <= minutes_to_market_close(now) <= CLOSE_BUFFER_MINUTES


# -------------------------------------------------
# MARKET HOURS GATE  <<< IMPORTANT
# -------------------------------------------------

def is_market_open(now):
    if now.weekday() >= 5:
        return False

    open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)

    return open_time <= now <= close_time


# -------------------------------------------------
# REGIME CLASSIFICATION
# -------------------------------------------------

def classify_regime(signals, volatility_history):
    if len(volatility_history) < 20:
        return "UNKNOWN"

    trend = signals["trend"]
    momentum = signals["momentum"]
    volatility = signals["volatility"]

    vol_series = pd.Series(volatility_history)
    if volatility >= vol_series.quantile(0.80):
        return "HIGH_VOL"
    if volatility <= vol_series.quantile(0.20):
        return "LOW_VOL"

    if trend > 0 and momentum > 0:
        return "TREND_UP"
    if trend < 0 and momentum < 0:
        return "TREND_DOWN"

    return "CHOPPY"


# -------------------------------------------------
# BROKER SETUP
# -------------------------------------------------

broker = Broker(starting_cash=config.AI_CAPITAL, name="frank")
trades_today = 0

eastern = pytz.timezone(config.MARKET_TIMEZONE)
print("AI Trader started")


# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------

while True:
    now = datetime.now(eastern)
    today = now.date()

    # Reset daily trade counter
    if last_trade_day != today:
        trades_today = 0
        last_trade_day = today

    # ⛔ HARD STOP AFTER MARKET CLOSE <<< THIS FIXES YOUR ISSUE
    if not is_market_open(now) and not is_near_market_close(now):
        time.sleep(300)  # sleep 5 minutes quietly
        continue

    # Timing gate
    if now.minute % config.DECISION_INTERVAL_MIN != 0:
        time.sleep(30)
        continue

    for ticker in config.TICKERS:
        df = get_latest_data(ticker)
        if df is None or len(df) < 10:
            continue

        signals = compute_signals(df)
        score = score_signals(signals)
        price = get_last_price(df)

        regime = classify_regime(signals, score_history[ticker])

        score_history[ticker].append(score)
        history = score_history[ticker]

        decision = "HOLD"
        decision_reason = "none"
        high_thresh = None
        low_thresh = None
        current_confidence = None
        near_close = is_near_market_close(now)

        # -------- Market close handler --------
        if near_close and ticker in broker.positions:
            current_confidence = entry_confidence[ticker]
            original = entry_confidence_original[ticker]

            if abs(current_confidence) < OVERNIGHT_HOLD_THRESHOLD * abs(original):
                broker.sell(ticker, price)
                decision = "SELL"
                decision_reason = "market_close_exit"
                entry_confidence.pop(ticker, None)
                entry_confidence_original.pop(ticker, None)

        # -------- Normal trading --------
        elif len(history) >= MIN_HISTORY_FOR_TRADE and regime != "HIGH_VOL":
            series = pd.Series(history)
            high_thresh = series.quantile(UPPER_QUANTILE)
            low_thresh = series.quantile(LOWER_QUANTILE)

            strong_up = score > high_thresh and signals["trend"] > 0 and signals["momentum"] > 0
            strong_down = score < low_thresh and signals["trend"] < 0 and signals["momentum"] < 0

            if strong_up and ticker not in broker.positions and allowed_to_trade(trades_today, config.MAX_TRADES_PER_DAY):
                amount = broker.cash * config.MAX_POSITION_PCT
                if broker.buy(ticker, price, amount):
                    entry_confidence[ticker] = score
                    entry_confidence_original[ticker] = score
                    trades_today += 1
                    decision = "BUY"
                    decision_reason = "strong_up_signal"

            elif ticker in broker.positions:
                entry_confidence[ticker] *= CONFIDENCE_DECAY
                current_confidence = entry_confidence[ticker]

                if abs(current_confidence) < EXIT_DECAY_THRESHOLD * abs(entry_confidence_original[ticker]):
                    broker.sell(ticker, price)
                    decision = "SELL"
                    decision_reason = "confidence_decay_exit"
                    entry_confidence.pop(ticker, None)
                    entry_confidence_original.pop(ticker, None)

        prices = get_market_prices(broker, price, ticker)
        equity = broker.equity(prices)

        log_decision(
            ticker,
            signals,
            score,
            decision,
            price,
            broker.cash,
            broker.realized_pnl,
            equity,
            regime=regime,
            decision_reason=decision_reason
        )

    time.sleep(60)
