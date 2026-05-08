import yfinance as yf
import pandas as pd
import numpy as np

def get_data(symbol="AAPL", period="60d", interval="15m"):
    df = yf.download(symbol, period=period, interval=interval)
    if df.empty:
        return df
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df["VOL_SMA"] = df["Volume"].rolling(20).mean()
    
    # คำนวณแนวรับ (Stop Loss) และแนวต้าน (Take Profit)
    df["Support"] = df["Low"].rolling(20).min()
    df["Resistance"] = df["High"].rolling(20).max()

    df = df.dropna()
    return df
