import pandas as pd
from collections import deque

import config
from data import get_latest_data
from ai_strategy import compute_signals, score_signals
from broker import Broker

# -------------------------------------------------
# PARAMETERS
# -------------------------------------------------

SCORE_HISTORY_LENGTH = 50
MIN_HISTORY_FOR_TRADE = 20
UPPER_QUANTILE = 0.80
LOWER_QUANTILE = 0.20

CONFIDENCE_DECAY = 0.97
EXIT_DECAY_THRESHOLD = 0.25

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
    high_vol = vol_series.quantile(0.80)
    low_vol = vol_series.quantile(0.20)

    if volatility >= high_vol:
        return "HIGH_VOL"
    if volatility <= low_vol:
        return "LOW_VOL"
    if trend > 0 and momentum > 0:
        return "TREND_UP"
    if trend < 0 and momentum < 0:
        return "TREND_DOWN"

    return "CHOPPY"

# -------------------------------------------------
# BACKTEST FUNCTION
# -------------------------------------------------

def run_backtest(ticker):
    print(f"\n--- Backtesting {ticker} ---")

    df = get_latest_data(ticker)
    if df is None or len(df) < 100:
        print("Not enough data")
        return

    broker = Broker(
        starting_cash=10.0,
        name="frank_backtest",
        commission_per_trade=0.005,
        spread_pct=0.0005,
        slippage_pct=0.0003
    )

    score_history = deque(maxlen=SCORE_HISTORY_LENGTH)
    volatility_history = deque(maxlen=SCORE_HISTORY_LENGTH)
    entry_confidence = None
    trades = 0

    for i in range(len(df)):
        data = df.iloc[:i+1]
        if len(data) < 10:
            continue

        signals = compute_signals(data)
        score = score_signals(signals)
        price = float(data["Close"].iloc[-1].item())

        score_history.append(score)
        volatility_history.append(signals["volatility"])

        regime = classify_regime(signals, volatility_history)

        if len(score_history) < MIN_HISTORY_FOR_TRADE:
            continue

        series = pd.Series(score_history)
        high = series.quantile(UPPER_QUANTILE)
        low = series.quantile(LOWER_QUANTILE)

        strong_up = score > high and signals["trend"] > 0 and signals["momentum"] > 0
        strong_down = score < low and signals["trend"] < 0 and signals["momentum"] < 0

        # ✅ Corrected indentation and regime gating
        if (regime in ("TREND_UP", "LOW_VOL")
            and strong_up
            and ticker not in broker.positions):

            max_amount = broker.cash - broker.commission
            if max_amount > 0:
                broker.buy(ticker, price, max_amount)
                entry_confidence = score
                trades += 1

        elif ticker in broker.positions:
            entry_confidence *= CONFIDENCE_DECAY
            decay_exit = abs(entry_confidence) < EXIT_DECAY_THRESHOLD * abs(score)
            if strong_down or decay_exit:
                broker.sell(ticker, price)
                entry_confidence = None
                trades += 1

    final_price = float(df["Close"].iloc[-1].item())
    final_equity = broker.cash + sum(pos["shares"] * final_price for pos in broker.positions.values())

    print(f"Trades: {trades}")
    print(f"Final equity: ${final_equity:.2f}")
    print(f"PnL: ${final_equity - 10.0:.2f}")

# -------------------------------------------------
# RUN
# -------------------------------------------------

if __name__ == "__main__":
    for ticker in config.TICKERS:
        run_backtest(ticker)
