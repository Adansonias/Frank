# logger.py

import csv
from datetime import datetime
from pathlib import Path
from project_root import get_project_root

# Always write logs to /log/logs.csv
LOG_PATH = get_project_root() / "log"
LOG_PATH.mkdir(exist_ok=True)

LOG_FILE = LOG_PATH / "logs.csv"


def log_decision(ticker, signals, score, decision, price, cash, realized_pnl, equity):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n[{timestamp}] {ticker}")
    for k, v in signals.items():
        print(f"  {k}: {v:.6f}")
    print(f"  score: {score:.6f}")
    print(f"  decision: {decision}")
    print(f"  price: {price:.2f}")
    print(f"  equity: {equity:.2f}")

    file_exists = LOG_FILE.exists()

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
