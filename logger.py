# logger.py

import csv
import os
from datetime import datetime

LOG_FILE = "logs.csv"

def log_decision(ticker, signals, score, decision, price, cash, realized_pnl, equity):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print to console
    print(f"\n[{timestamp}] {ticker}")
    for k, v in signals.items():
        print(f"  {k}: {v:.6f}")
    print(f"  score: {score:.6f}")
    print(f"  decision: {decision}")
    print(f"  cash: {cash:.2f} | realized_pnl: {realized_pnl:.2f} | equity: {equity:.2f}")

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "ticker",
                "trend",
                "momentum",
                "volatility",
                "score",
                "decision",
                "price",
                "cash",
                "realized_pnl",
                "equity"
            ])

        writer.writerow([
            timestamp,
            ticker,
            signals["trend"],
            signals["momentum"],
            signals["volatility"],
            score,
            decision,
            price,
            cash,
            realized_pnl,
            equity
        ])
