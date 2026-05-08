import yfinance as yf
import pandas as pd

def get_data(symbol="AAPL", period="6mo", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # คำนวณ EMA ด้วย pandas โดยตรง
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    # คำนวณ RSI ด้วย pandas โดยตรง
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["VOL_SMA"] = df["Volume"].rolling(20).mean()

    df = df.dropna()
    return df
