# ai_strategy.py

def compute_signals(df):
    closes = df["Close"]

    short_trend = (closes.iloc[-1] - closes.iloc[-5]) / closes.iloc[-5]
    momentum = closes.diff().iloc[-5:].mean()
    volatility = closes.pct_change().iloc[-10:].std()

    return {
        "trend": float(short_trend),
        "momentum": float(momentum),
        "volatility": float(volatility)
    }


def score_signals(signals):
    score = (
        0.5 * signals["trend"] +
        0.3 * signals["momentum"] -
        0.4 * signals["volatility"]
    )
    return score
