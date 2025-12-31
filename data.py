# data.py

import yfinance as yf
import pandas as pd

def get_latest_data(ticker):
    data = yf.download(
        tickers=ticker,
        period="1d",
        interval="1m",
        progress=False
    )

    if data.empty:
        return None

    return data.dropna()
