import streamlit as st
import plotly.graph_objects as go
from data_loader import get_data
from ai_engine import train_model, load_model, predict
from scanner import scan_market

st.set_page_config(layout="wide")
st.title("🚀 AI Trading Super Dashboard (V2)")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Scanner", "Train Model"])

# เมนูเลือก Timeframe ให้เหมาะกับสายซิ่ง
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
            
            # --- ระบบแจกซิกแนล ---
            if score > 60 and price > ema20 and rsi > 50:
                st.success("## 🟢 สัญญาณ: BUY NOW (เข้าซื้อได้เลย!)")
            elif score < 40 or price < ema20:
                st.error("## 🔴 สัญญาณ: SELL / AVOID (ขาลง ห้ามเข้า!)")
            else:
                st.warning("## 🟡 สัญญาณ: WAIT (รอดูอาการไปก่อน)")
            
            # --- แผนการเทรด ---
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", f"${price:.2f}")
            col2.metric("AI Score", f"{score:.2f}%")
            col3.metric("🎯 จุดทำกำไร (TP)", f"${resist:.2f}")
            col4.metric("🛑 จุดตัดขาดทุน (SL)", f"${support:.2f}")
            
            # --- กราฟแสดงเส้นแนวรับแนวต้าน ---
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=pred.index, open=pred["Open"], high=pred["High"],
                low=pred["Low"], close=pred["Close"], name="Price"
            ))
            fig.add_trace(go.Scatter(x=pred.index, y=pred["EMA20"], line=dict(color='blue', width=1), name="EMA 20"))
            fig.add_trace(go.Scatter(x=pred.index, y=pred["Support"], line=dict(color='red', width=2, dash='dot'), name="Stop Loss Line"))
            fig.update_layout(height=600, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

elif menu == "Scanner":
    st.subheader(f"📊 Market Scanner (วิเคราะห์ราย {interval})")
    with st.spinner("AI กำลังสแกนหาหุ้นซิ่ง..."):
        results = scan_market(period=period, interval=interval)
        st.dataframe(results, use_container_width=True, height=500)

elif menu == "Train Model":
    st.subheader("🤖 Train AI Model")
    train_sym = st.text_input("Train with symbol", "AAPL")
    if st.button("Train AI Now"):
        with st.spinner("Training..."):
            df = get_data(train_sym, period="1y", interval="1d")
            model = train_model(df)
            st.success("Model trained successfully! AI ฉลาดขึ้นแล้ว")
