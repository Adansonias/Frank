# main.py

import time
from datetime import datetime
import pytz

import config
from data import get_latest_data
from ai_strategy import compute_signals, score_signals
from broker import Broker
from risk import allowed_to_trade
from logger import log_decision


# Create broker (paper mode)
broker = Broker(starting_cash=config.AI_CAPITAL, name="frank")
trades_today = 0

eastern = pytz.timezone(config.MARKET_TIMEZONE)

print("AI Trader started (paper mode with PnL)")

while True:
    now = datetime.now(eastern)
    print("Heartbeat:", now.strftime("%H:%M:%S"))

    if now.minute % config.DECISION_INTERVAL_MIN != 0:
        time.sleep(30)
        continue

    for ticker in config.TICKERS:
        df = get_latest_data(ticker)
        if df is None or len(df) < 10:
            continue

        signals = compute_signals(df)
        score = score_signals(signals)
        price = df["Close"].iloc[-1]

        decision = "NO TRADE"

        # --- BUY ---
        if score > config.BUY_THRESHOLD and allowed_to_trade(trades_today, config.MAX_TRADES_PER_DAY):
            amount = broker.cash * config.MAX_POSITION_PCT
            if broker.buy(ticker, price, amount):
                trades_today += 1
                decision = "BUY"

        # --- SELL ---
        elif score < config.SELL_THRESHOLD:
            pnl = broker.sell(ticker, price)
            if pnl is not False:
                decision = "SELL"

        # --- PnL + Equity ---
        prices = {ticker: price}
        equity = broker.equity(prices)

        # --- LOG EVERYTHING ---
        log_decision(
            ticker,
            signals,
            score,
            decision,
            price,
            broker.cash,
            broker.realized_pnl,
            equity
        )

    time.sleep(60)
