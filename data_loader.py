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
    
    df["Resistance"] = df["High"].rolling(20).max()

    # --- Level 5: ระบบวัดความแกว่ง ATR (Average True Range) ---
    df['Prev_Close'] = df['Close'].shift(1)
    df['TR1'] = df['High'] - df['Low']
    df['TR2'] = abs(df['High'] - df['Prev_Close'])
    df['TR3'] = abs(df['Low'] - df['Prev_Close'])
    df['TR'] = df[['TR1', 'TR2', 'TR3']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()
    
    # จุดคัตลอสยืดหยุ่น: ถอยลงมาจากราคาปัจจุบัน 1.5 เท่าของความแกว่ง
    df['ATR_SL'] = df['Close'] - (1.5 * df['ATR'])
    df = df.drop(columns=['Prev_Close', 'TR1', 'TR2', 'TR3', 'TR'])

    # แอบดูเทรนด์ใหญ่
    try:
        df_daily = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if not df_daily.empty:
            if isinstance(df_daily.columns, pd.MultiIndex):
                df_daily.columns = df_daily.columns.droplevel(1)
            daily_ema50 = df_daily["Close"].ewm(span=50, adjust=False).mean()
            macro_uptrend = df_daily["Close"].iloc[-1] > daily_ema50.iloc[-1]
        else:
            macro_uptrend = True 
    except:
        macro_uptrend = True
        
    df["Macro_Uptrend"] = macro_uptrend
    df = df.dropna()
    return df
