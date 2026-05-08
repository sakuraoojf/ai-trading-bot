import pandas as pd
from data_loader import get_data
from ai_engine import load_model, predict

# แก๊งหุ้นซิ่ง อัปเดตใหม่!
TICKERS = [
    "MARA", "RIOT", "COIN",  
    "TSLA", "NIO", "RIVN",   
    "PLTR", "SOFI", "AI",    
    "GME", "AMC", "HOOD"     
]

def scan_market(period="60d", interval="15m"):
    model = load_model()
    results = []

    for t in TICKERS:
        df = get_data(t, period=period, interval=interval)
        if df.empty:
            continue
            
        pred = predict(df, model)
        if not pred.empty:
            last_row = pred.iloc[-1]
            score = last_row["score"]
            price = last_row["Close"]
            rsi = last_row["RSI"]
            ema20 = last_row["EMA20"]
            
            # เช็คซิกแนล
            if score > 60 and price > ema20 and rsi > 50:
                status = "🟢 BUY"
            elif score < 40 or price < ema20:
                status = "🔴 SELL"
            else:
                status = "🟡 WAIT"
                
            results.append({
                "Symbol": t,
                "Signal": status,
                "AI Score (%)": round(score, 2),
                "Price": round(price, 2),
                "RSI": round(rsi, 2)
            })

    # เรียงลำดับตัวที่น่าซื้อที่สุดไว้บนสุด
    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res = df_res.sort_values(by="AI Score (%)", ascending=False).reset_index(drop=True)
    return df_res
