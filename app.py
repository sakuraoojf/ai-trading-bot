import streamlit as st
import plotly.graph_objects as go
from data_loader import get_data
from ai_engine import train_model, load_model, predict
from scanner import scan_market

st.set_page_config(layout="wide")
st.title("🚀 AI Trading Super Dashboard (V6: Risk Manager)")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Scanner", "Train Model"])

# --- เพิ่มแถบตั้งค่าความเสี่ยงด้านซ้ายมือ ---
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ แผงควบคุมความเสี่ยง")
capital = st.sidebar.number_input("เงินทุนในพอร์ตทั้งหมด ($)", min_value=1.0, value=15.0, step=1.0)
risk_pct = st.sidebar.slider("ยอมขาดทุนเต็มที่ต่อรอบ (%)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
st.sidebar.markdown("*(แนะนำให้ตั้งค่า 2% เพื่อความปลอดภัยระดับกองทุน)*")

interval_map = {"15 Minutes (สายซิ่ง Day Trade)": "15m", "1 Hour (สายรันเทรนด์)": "1h", "1 Day (สายถือยาว)": "1d"}
st.sidebar.markdown("---")
selected_tf = st.sidebar.selectbox("Timeframe", list(interval_map.keys()))
interval = interval_map[selected_tf]
period = "60d" if interval in ["15m", "1h"] else "1y"

if menu == "Dashboard":
    symbol = st.text_input("Symbol", "COIN").upper()
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
            atr_sl = last_row['ATR_SL']
            resist = last_row['Resistance']
            vol_surge = last_row['Volume_Surge']
            macro_up = last_row['Macro_Uptrend']
            
            # --- SIGNAL LOGIC ---
            if score > 70 and price > ema20 and rsi > 50 and vol_surge and macro_up:
                st.success("## 🚀 SUPER BUY (เทรนด์ใหญ่เป็นขาขึ้น + วาฬกำลังลาก!)")
                st.balloons()
            elif score > 60 and price > ema20 and rsi > 50 and macro_up:
                st.success("## 🟢 BUY (กราฟสวย ทยอยเก็บสะสม)")
            elif (score > 60 and price > ema20) and not macro_up:
                st.warning("## 🟡 AVOID: กราฟสั้นสวย แต่เทรนด์ใหญ่ยังเป็น 'ขาลง' (อย่าฝืนเล่น!)")
            elif score < 40 or price < ema20:
                st.error("## 🔴 SELL / AVOID (ขาลง หนีด่วน!)")
            else:
                st.warning("## 🟡 WAIT (รอดูอาการไปก่อน)")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", f"${price:.2f}")
            col2.metric("AI Score", f"{score:.2f}%")
            col3.metric("🎯 จุดทำกำไร (TP)", f"${resist:.2f}")
            col4.metric("🛑 ATR Stop Loss", f"${atr_sl:.2f}", "หนีตายอัตโนมัติ", delta_color="off")
            
            # --- FEATURE 1: POSITION SIZING CALCULATOR ---
            st.markdown("### ⚖️ เครื่องคิดเลขคำนวณหน้าตัก (ล็อคความเสี่ยง)")
            risk_amount = capital * (risk_pct / 100)
            distance_to_sl = price - atr_sl
            
            if distance_to_sl > 0:
                position_shares = risk_amount / distance_to_sl
                position_dollars = position_shares * price
                
                # เช็คว่าบอทสั่งให้ซื้อเกินเงินในกระเป๋าเราไหม
                if position_dollars >= capital:
                    position_dollars = capital
                    position_shares = capital / price
                    actual_risk_amount = position_shares * distance_to_sl
                    actual_risk_pct = (actual_risk_amount / capital) * 100
                    st.info(f"💡 **แผนการเทรด (ปลอดภัย):** อนุญาตให้เทรดหมดหน้าตัก (ซื้อเต็มจำนวน **${capital:.2f}**) ได้เลยครับ!\n\n*(เหตุผล: เพราะตอนนี้ราคากับจุด ATR Stop Loss อยู่ใกล้กันมาก หากซวยจริงๆ แล้วโดนคัตลอส คุณจะเสียเงินแค่ **${actual_risk_amount:.2f}** หรือคิดเป็น **{actual_risk_pct:.2f}%** ของพอร์ต ซึ่งอยู่ในระดับที่ปลอดภัยมากครับ)*")
                else:
                    st.warning(f"💡 **แผนการเทรด (ห้าม All-in):** ให้แบ่งเงินเข้าซื้อหุ้นตัวนี้แค่ **${position_dollars:.2f}** เท่านั้นครับ (ซื้อแบบเศษหุ้น {position_shares:.4f} หุ้น)\n\n*(เหตุผล: เพราะตอนนี้ราคาวิ่งห่างจากจุด ATR Stop Loss มากแล้ว หากคุณฝืนซื้อหมดหน้าตักแล้วโดนคัตลอส พอร์ตจะพังครับ แต่ถ้าคุณซื้อด้วยเงินก้อนเล็กตามที่บอทบอก หากโดนคัตลอส คุณจะเสียเงินแค่ **${risk_amount:.2f}** หรือ **{risk_pct}%** ตามเป้าเป๊ะๆ ครับ)*")
            else:
                st.error("💡 **แผนการเทรด:** ราคาพุ่งทะลุจุดปลอดภัยไปแล้ว ห้ามเข้าซื้อเด็ดขาด!")
            
            # --- CHART ---
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=pred.index, open=pred["Open"], high=pred["High"],
                low=pred["Low"], close=pred["Close"], name="Price"
            ))
            fig.add_trace(go.Scatter(x=pred.index, y=pred["EMA20"], line=dict(color='blue', width=1), name="EMA 20"))
            fig.add_trace(go.Scatter(x=pred.index, y=pred["ATR_SL"], line=dict(color='orange', width=2, dash='dot'), name="ATR Stop Loss (เส้นหนีตาย)"))
            
            surge_df = pred[pred["Volume_Surge"] == True]
            if not surge_df.empty:
                fig.add_trace(go.Scatter(
                    x=surge_df.index, y=surge_df["Low"] * 0.99, 
                    mode='markers', marker=dict(color='yellow', size=12, symbol='star'), 
                    name="Whale Alert"
                ))
                
            fig.update_layout(height=600, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

elif menu == "Scanner":
    st.subheader(f"📊 ระบบจับวาฬ (สแกนราย {interval} บนหุ้นซิ่ง 42 ตัว)")
    with st.spinner("AI กำลังสแกนหาจุดพลุแตก..."):
        results = scan_market(period=period, interval=interval)
        if results.empty:
            st.warning("ตอนนี้เทรนด์ใหญ่พังหมด ยังไม่มีหุ้นตัวไหนพร้อมวิ่งครับ!")
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
