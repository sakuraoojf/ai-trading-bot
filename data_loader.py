import yfinance as yf
import pandas as pd
import numpy as np

def get_data(symbol="AAPL", period="60d", interval="15m"):
    df = yf.download(symbol, period=period, interval=interval, progress=False)
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
    df["Volume_Surge"] = df["Volume"] > (df["VOL_SMA"] * 2) 
    
    df["Support"] = df["Low"].rolling(20).min()
    df["Resistance"] = df["High"].rolling(20).max()

    # --- Level 3: Multi-Timeframe (แอบดูเทรนด์ใหญ่รายวัน) ---
    try:
        df_daily = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if not df_daily.empty:
            if isinstance(df_daily.columns, pd.MultiIndex):
                df_daily.columns = df_daily.columns.droplevel(1)
            daily_ema50 = df_daily["Close"].ewm(span=50, adjust=False).mean()
            # เช็คว่าราคาปัจจุบัน ยืนเหนือเส้น EMA50 รายวันได้หรือไม่ (เป็นเทรนด์ขาขึ้นหรือไม่)
            macro_uptrend = df_daily["Close"].iloc[-1] > daily_ema50.iloc[-1]
        else:
            macro_uptrend = True 
    except:
        macro_uptrend = True
        
    df["Macro_Uptrend"] = macro_uptrend

    df = df.dropna()
    return df
