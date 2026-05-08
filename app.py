import streamlit as st
import plotly.graph_objects as go
from data_loader import get_data
from ai_engine import train_model, load_model, predict
from scanner import scan_market

st.set_page_config(layout="wide")
st.title("🚀 AI Trading Super Dashboard (V3: Whale Catcher)")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Scanner", "Train Model"])

interval_map = {"15 Minutes (สายซิ่ง Day Trade)": "15m", "1 Hour (สายรันเทรนด์)": "1h", "1 Day (สายถือยาว)": "1d"}
selected_tf = st.sidebar.selectbox("Timeframe", list(interval_map.keys()))
interval = interval_map[selected_tf]
period = "60d" if interval in ["15m", "1h"] else "1y"

if menu == "Dashboard":
    symbol = st.text_input("Symbol", "TSLA").upper()
    df = get_data(symbol, period=period, interval=interval)
    
    if df.empty:
        st.error("No data found. Check symbol.")
    else:
        model = load_model()
        pred = predict(df, model)

        if not pred.empty:
            last_row = pred.iloc[-1]
            score = last_row['score']
            price = last_row['Close']
            ema20 = last_row['EMA20']
            rsi = last_row['RSI']
            support = last_row['Support']
            resist = last_row['Resistance']
            vol_surge = last_row['Volume_Surge']
            
            # --- V3 SUPER SIGNAL ---
            if score > 70 and price > ema20 and rsi > 50 and vol_surge:
                st.success("## 🚀 สัญญาณระดับสูงสุด: SUPER BUY (ซื้อเดี๋ยวนี้! เงินก้อนใหญ่กำลังลาก)")
                st.balloons() # ยิงพลุฉลอง
            elif score > 60 and price > ema20 and rsi > 50:
                st.success("## 🟢 สัญญาณ: BUY (กราฟสวย ทยอยเก็บสะสม)")
            elif score < 40 or price < ema20:
                st.error("## 🔴 สัญญาณ: SELL / AVOID (ขาลง หนีด่วน!)")
            else:
                st.warning("## 🟡 สัญญาณ: WAIT (รอดูอาการไปก่อน)")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", f"${price:.2f}")
            col2.metric("AI Score", f"{score:.2f}%")
            col3.metric("🎯 จุดทำกำไร (TP)", f"${resist:.2f}")
            col4.metric("🛑 จุดตัดขาดทุน (SL)", f"${support:.2f}")
            
            # --- CHART ---
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=pred.index, open=pred["Open"], high=pred["High"],
                low=pred["Low"], close=pred["Close"], name="Price"
            ))
            fig.add_trace(go.Scatter(x=pred.index, y=pred["EMA20"], line=dict(color='blue', width=1), name="EMA 20"))
            fig.add_trace(go.Scatter(x=pred.index, y=pred["Support"], line=dict(color='red', width=2, dash='dot'), name="Stop Loss Line"))
            
            # วาดรูปดาวสีเหลืองตรงแท่งที่มี Volume พุ่ง
            surge_df = pred[pred["Volume_Surge"] == True]
            if not surge_df.empty:
                fig.add_trace(go.Scatter(
                    x=surge_df.index, y=surge_df["Low"] * 0.99, 
                    mode='markers', marker=dict(color='yellow', size=12, symbol='star'), 
                    name="Whale Alert (เงินก้อนใหญ่เข้า)"
                ))
                
            fig.update_layout(height=600, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

elif menu == "Scanner":
    st.subheader(f"📊 ระบบจับวาฬ (สแกนราย {interval} บนหุ้นซิ่ง 42 ตัว)")
    st.info("💡 กรองมาเฉพาะหุ้นที่มีสัญญาณ 🚀 SUPER BUY และ 🟢 BUY เท่านั้น ตัวที่กราฟพังจะโดนคัดทิ้งทันที!")
    with st.spinner("AI กำลังสแกนหาจุดพลุแตก... (อาจใช้เวลา 10-20 วินาที)"):
        results = scan_market(period=period, interval=interval)
        if results.empty:
            st.warning("ตอนนี้ยังไม่มีหุ้นตัวไหนพร้อมวิ่งครับ รอดูแท่งเทียนถัดไปนะครับ")
        else:
            st.dataframe(results, use_container_width=True, height=500)

elif menu == "Train Model":
    st.subheader("🤖 Train AI Model")
    train_sym = st.text_input("Train with symbol", "AAPL")
    if st.button("Train AI Now"):
        with st.spinner("Training..."):
            df = get_data(train_sym, period="1y", interval="1d")
            model = train_model(df)
            st.success("Model trained successfully! AI ฉลาดขึ้นแล้ว")
