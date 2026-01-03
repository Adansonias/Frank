# logger.py

import csv
from datetime import datetime
from pathlib import Path
from project_root import get_project_root


def get_daily_log_path():
    """
    Create /log/YYYY-MM-DD.csv automatically.
    """
    root = get_project_root() / "log"
    root.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    return root / f"{today}.csv"


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
    decision_reason="none",
    regime="UNKNOWN"
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = get_daily_log_path()
    file_exists = log_file.exists()

    # ---- Console output ----
    print(f"\n[{timestamp}] {ticker}")
    print(f"  regime: {regime}")
    for k, v in signals.items():
        print(f"  {k}: {v:.6f}")
    print(f"  score: {score:.6f}")
    print(f"  decision: {decision} ({decision_reason})")
    print(f"  price: {price:.2f}")
    print(f"  equity: {equity:.2f}")

    # ---- CSV output ----
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "ticker",
                "regime",
                "trend",
                "momentum",
                "volatility",
                "score",
                "high_thresh",
                "low_thresh",
                "decision",
                "decision_reason",
                "price",
                "cash",
                "realized_pnl",
                "equity",
                "entry_confidence",
                "current_confidence",
                "near_market_close"
            ])

        writer.writerow([
            timestamp,
            ticker,
            regime,
            signals["trend"],
            signals["momentum"],
            signals["volatility"],
            score,
            high_thresh,
            low_thresh,
            decision,
            decision_reason,
            price,
            cash,
            realized_pnl,
            equity,
            entry_confidence,
            current_confidence,
            near_market_close
        ])
