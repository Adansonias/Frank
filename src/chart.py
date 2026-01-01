import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use("default")

fig, ax = plt.subplots(figsize=(12, 6))

def update(frame):
    ax.clear()

    try:
        df = pd.read_csv("logs.csv")
    except Exception:
        return

    if df.empty:
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    for ticker in df["ticker"].unique():
        sub = df[df["ticker"] == ticker]

        ax.plot(sub["timestamp"], sub["score"], label=f"{ticker} score")

        buys = sub[sub["decision"] == "BUY"]
        ax.scatter(buys["timestamp"], buys["score"], marker="^", s=100)

        sells = sub[sub["decision"] == "SELL"]
        ax.scatter(sells["timestamp"], sells["score"], marker="v", s=100)

    ax.axhline(0, linestyle="--")
    ax.set_title("Frank — Live Signal Monitor")
    ax.set_xlabel("Time")
    ax.set_ylabel("Score")
    ax.legend(loc="upper left")

ani = FuncAnimation(fig, update, interval=5000)  # refresh every 5s
plt.tight_layout()
plt.show()
