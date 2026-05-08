import pandas as pd
from data_loader import get_data
from ai_engine import load_model, predict

# Top หุ้นซิ่งแห่งปี (คริปโต, AI, EV, Big Tech)
TICKERS = [
    "MARA", "RIOT", "COIN", "MSTR", "GME", "AMC", "HOOD", 
    "TSLA", "NIO", "RIVN", "LCID", "XPEV",
    "NVDA", "AMD", "PLTR", "SOFI", "AI", "SMCI", "CRWD", "PANW", "MU", "INTC", "ARM",
    "AAPL", "MSFT", "META", "GOOGL", "AMZN", "NFLX",
    "BABA", "JD", "PDD",
    "ROKU", "SQ", "PYPL", "UBER", "DASH", "AFRM", "UPST", "CVNA", "SHOP", "SNOW", "DDOG"
]

def scan_market(period="60d", interval="15m"):
    model = load_model()
    results = []

    for t in TICKERS:
        try:
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
                vol_surge = last_row["Volume_Surge"]
                
                # [อัปเกรด V3] โชว์เฉพาะตัวที่เข้าเงื่อนไขทำกำไร
                if score > 70 and price > ema20 and rsi > 50 and vol_surge:
                    status = "🚀 SUPER BUY (วาฬเข้า!)"
                elif score > 60 and price > ema20 and rsi > 50:
                    status = "🟢 BUY (น่าเก็บ)"
                else:
                    # ข้ามหุ้นที่กราฟพังทิ้งไปเลย ไม่ต้องเอามาโชว์ให้รกตา
                    continue
                    
                results.append({
                    "Symbol": t,
                    "Signal": status,
                    "AI Score (%)": round(score, 2),
                    "Price": round(price, 2),
                    "RSI": round(rsi, 2)
                })
        except:
            continue

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res = df_res.sort_values(by="AI Score (%)", ascending=False).reset_index(drop=True)
    return df_res
