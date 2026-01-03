import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from project_root import get_project_root
from pathlib import Path

# --------------------
# Chart setup
# --------------------
plt.style.use("default")
fig, ax = plt.subplots(figsize=(12, 6))
ax2 = None  # will be created inside update()


# --------------------
# Load all daily logs
# --------------------
def load_all_logs():
    project_root = get_project_root()
    log_root = project_root / "log"

    frames = []

    for day_dir in sorted(log_root.iterdir()):
        if not day_dir.is_dir():
            continue

        csv_path = day_dir / "decisions.csv"
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                df["log_day"] = day_dir.name
                frames.append(df)
            except Exception:
                continue

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


# --------------------
# Update plot
# --------------------
def update(frame):
    global ax2
    ax.clear()
    ax2 = ax.twinx()  # recreate secondary axis each update

    # Load logs
    df = load_all_logs()
    if df.empty:
        ax.set_title("No logs found")
        return

    # Parse timestamps safely
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    if df.empty:
        ax.set_title("No valid timestamps in logs")
        return

    # Last 7 days
    end_time = df["timestamp"].max()
    start_time = end_time - pd.Timedelta(days=7)

    # Plot per ticker
    for ticker in df["ticker"].unique():
        sub = df[df["ticker"] == ticker]

        ax.plot(
            sub["timestamp"],
            sub["score"],
            label=f"{ticker} score",
            linewidth=1.5
        )

        # Buy/sell markers
        buys = sub[sub["decision"].str.contains("BUY")]
        sells = sub[sub["decision"].str.contains("SELL")]

        ax.scatter(buys["timestamp"], buys["score"], marker="^", s=100, alpha=0.9)
        ax.scatter(sells["timestamp"], sells["score"], marker="v", s=100, alpha=0.9)

    # Equity curve
    if "equity" in df.columns:
        equity_df = df.sort_values("timestamp")
        ax2.plot(
            equity_df["timestamp"],
            equity_df["equity"],
            linestyle="--",
            linewidth=1.5,
            alpha=0.6,
            label="Equity"
        )
        ax2.set_ylabel("Equity ($)")

    # Styling
    ax.axhline(0, linestyle="--", linewidth=1, alpha=0.6)
    ax.set_xlim(start_time, end_time)
    ax.set_title("Frank — Live Signal Monitor (Last 7 Days)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Score")
    ax.grid(True, alpha=0.3)

    # Legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left")


# --------------------
# Live animation
# --------------------
ani = FuncAnimation(
    fig,
    update,
    interval=5000,
    cache_frame_data=False
)

plt.tight_layout()
plt.show()
