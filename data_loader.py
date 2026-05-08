import yfinance as yf
import pandas as pd
import pandas_ta as ta

def get_data(symbol="AAPL", period="6mo", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    df["EMA20"] = ta.ema(df["Close"], length=20)
    df["EMA50"] = ta.ema(df["Close"], length=50)
    df["RSI"] = ta.rsi(df["Close"], length=14)
    df["VOL_SMA"] = df["Volume"].rolling(20).mean()

    df = df.dropna()
    return df
