import csv
from datetime import datetime
from pathlib import Path
from project_root import get_project_root

LOG_PATH = get_project_root() / "log"
LOG_PATH.mkdir(exist_ok=True)
LOG_FILE = LOG_PATH / "logs.csv"


def log_decision(
    ticker,
    signals,
    score,
    decision,
    price,
    cash,
    realized_pnl,
    equity,
    high_thresh=None,
    low_thresh=None,
    entry_confidence=None,
    current_confidence=None,
    near_market_close=False,
    decision_reason="none"
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                "decision_reason",
                "price",
                "cash",
                "realized_pnl",
                "equity",
                "high_threshold",
                "low_threshold",
                "entry_confidence",
                "current_confidence",
                "near_market_close"
            ])

        writer.writerow([
            timestamp,
            ticker,
            signals["trend"],
            signals["momentum"],
            signals["volatility"],
            score,
            decision,
            decision_reason,
            price,
            cash,
            realized_pnl,
            equity,
            high_thresh,
            low_thresh,
            entry_confidence,
            current_confidence,
            near_market_close
        ])
