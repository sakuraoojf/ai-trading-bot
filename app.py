import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from data_loader import get_data
from ai_engine import train_model, load_model, predict
from scanner import scan_market

st.set_page_config(layout="wide")
st.title("🚀 AI Trading Super Dashboard (V12: Level 6 Arbitrage)")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Scanner", "Stock Duel", "Train Model"])

# --- ตั้งค่าความเสี่ยง (Risk Management) ---
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ แผงควบคุมความเสี่ยง")
capital = st.sidebar.number_input("เงินทุนในพอร์ตทั้งหมด ($)", min_value=1.0, value=15.0, step=1.0)
risk_pct = st.sidebar.slider("ยอมขาดทุนเต็มที่ต่อรอบ (%)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)

interval_map = {"15 Minutes (สายซิ่ง Day Trade)": "15m", "1 Hour (สายรันเทรนด์)": "1h", "1 Day (สายถือยาว)": "1d"}
st.sidebar.markdown("---")
selected_tf = st.sidebar.selectbox("Timeframe", list(interval_map.keys()))
interval = interval_map[selected_tf]
period = "60d" if interval in ["15m", "1h"] else "1y"

if menu == "Dashboard":
    
    # --- FEATURE 3: SECTOR HEATMAP ---
    st.markdown("### 🗺️ เรดาร์จับกระแสเงิน (วาฬเข้ากลุ่มไหน?)")
    etfs = {"XLK": "เทคโนโลยี", "IBIT": "คริปโต", "XLY": "ฟุ่มเฟือย", "XLF": "การเงิน", "XLE": "พลังงาน"}
    cols = st.columns(5)
    for idx, (ticker, name) in enumerate(etfs.items()):
        try:
            etf_df = yf.download(ticker, period="5d", interval="1d", progress=False)
            if not etf_df.empty and len(etf_df) >= 2:
                if isinstance(etf_df.columns, pd.MultiIndex):
                    etf_df.columns = etf_df.columns.droplevel(1)
                close_today = float(etf_df["Close"].iloc[-1])
                close_yest = float(etf_df["Close"].iloc[-2])
                pct_change = ((close_today - close_yest) / close_yest) * 100
                cols[idx].metric(f"{ticker} ({name})", f"${close_today:.2f}", f"{pct_change:.2f}%")
            else:
                cols[idx].metric(f"{ticker} ({name})", "N/A", "0.00%")
        except:
            cols[idx].metric(f"{ticker} ({name})", "Error", "0.00%")
            
    st.markdown("---")
    
    symbol = st.text_input("ค้นหาหุ้นที่ Discord แจ้งเตือน (Symbol)", "COIN").upper()
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
            bull_engulfing = last_row['Bullish_Engulfing']
            
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
                
            if bull_engulfing:
                st.info("🔥 **PATTERN DETECTED:** พบสัญลักษณ์ 🕯️ **Bullish Engulfing (แท่งเทียนกลืนกินขาขึ้น)** เพิ่งเกิดพฤติกรรมการกวาดซื้อกลับตัวอย่างรุนแรง ถือเป็นจุดเข้าที่มีความแม่นยำสูงมาก!")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Price", f"${price:.2f}")
            col2.metric("AI Score", f"{score:.2f}%")
            col3.metric("🎯 จุดทำกำไร (TP)", f"${resist:.2f}")
            col4.metric("🛑 ATR Stop Loss", f"${atr_sl:.2f}", "หนีตายอัตโนมัติ", delta_color="off")
            
            st.markdown("### ⚖️ เครื่องคิดเลขคำนวณหน้าตัก (ล็อคความเสี่ยง)")
            risk_amount = capital * (risk_pct / 100)
            distance_to_sl = price - atr_sl
            
            if distance_to_sl > 0:
                position_shares = risk_amount / distance_to_sl
                position_dollars = position_shares * price
                if position_dollars >= capital:
                    position_dollars = capital
                    position_shares = capital / price
                    actual_risk_amount = position_shares * distance_to_sl
                    actual_risk_pct = (actual_risk_amount / capital) * 100
                    st.info(f"💡 **แผนการเทรด (ปลอดภัย):** อนุญาตให้เทรดหมดหน้าตัก (ซื้อเต็มจำนวน **${capital:.2f}**) ได้เลยครับ!\n\n*(เหตุผล: เพราะตอนนี้ราคากับจุด ATR Stop Loss อยู่ใกล้กันมาก หากโดนคัตลอส คุณจะเสียเงินแค่ **${actual_risk_amount:.2f}** หรือคิดเป็น **{actual_risk_pct:.2f}%** ของพอร์ต ซึ่งปลอดภัยมาก)*")
                else:
                    st.warning(f"💡 **แผนการเทรด (ห้าม All-in):** ให้แบ่งเงินเข้าซื้อหุ้นตัวนี้แค่ **${position_dollars:.2f}** เท่านั้นครับ (ซื้อเศษหุ้น {position_shares:.4f} หุ้น)\n\n*(เหตุผล: เพราะราคาวิ่งห่างจาก ATR Stop Loss มากแล้ว หากคุณแบ่งไม้ซื้อตามที่บอทบอก หากโดนคัตลอส คุณจะเสียเงินแค่ **${risk_amount:.2f}** หรือ **{risk_pct}%** ตามเป้าเป๊ะๆ)*")
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
                
            pattern_df = pred[pred["Bullish_Engulfing"] == True]
            if not pattern_df.empty:
                fig.add_trace(go.Scatter(
                    x=pattern_df.index, y=pattern_df["Low"] * 0.97, 
                    mode='text', text='🕯️', textposition='bottom center', textfont=dict(size=20),
                    name="Bullish Engulfing"
                ))
                
            fig.update_layout(height=600, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

# ====================================================
# --- LEVEL 6: AI CORRELATION ENGINE (เรดาร์หาหุ้นแฝด) ---
# ====================================================
elif menu == "Stock Duel":
    st.subheader("⚔️ สังเวียนเปรียบเทียบหุ้น & เรดาร์หาหุ้นแฝด")
    st.markdown("ระบบจะประเมิน AI Score และคำนวณหาค่า **ความเหมือน (Correlation)** ว่าเป็นหุ้นแฝดที่วิ่งตามกันหรือไม่ เพื่อหาจังหวะดักเก็งกำไรแบบชัวร์ๆ (Statistical Arbitrage)")
    
    col1, col2 = st.columns(2)
    sym1 = col1.text_input("🔵 นักมวยฝั่งน้ำเงิน (Symbol 1)", "NVDA").upper()
    sym2 = col2.text_input("🔴 นักมวยฝั่งแดง (Symbol 2)", "AMD").upper()
    
    if st.button("🔥 สั่ง AI เริ่มการประลองและค้นหาหุ้นแฝด!"):
        with st.spinner("AI กำลังวิเคราะห์ความสัมพันธ์ของกราฟ..."):
            df1 = get_data(sym1, period=period, interval=interval)
            df2 = get_data(sym2, period=period, interval=interval)
            
            if df1.empty or df2.empty:
                st.error("❌ ข้อมูลหุ้นไม่ครบ ตรวจสอบชื่อหุ้นให้ถูกต้องอีกครั้งครับ")
            else:
                model = load_model()
                pred1 = predict(df1, model)
                pred2 = predict(df2, model)
                
                s1_score = pred1.iloc[-1]['score']
                s2_score = pred2.iloc[-1]['score']
                
                # --- LEVEL 6: CORRELATION ENGINE ---
                st.markdown("---")
                st.markdown("### 🔗 AI Correlation Engine (เรดาร์หาหุ้นแฝด)")
                
                # คำนวณความสัมพันธ์ (Pearson Correlation) ระหว่างราคาปิด 2 ตัว
                # Align data indices
                aligned_df = pd.DataFrame({"P1": pred1["Close"], "P2": pred2["Close"]}).dropna()
                if len(aligned_df) > 10:
                    correlation = aligned_df["P1"].corr(aligned_df["P2"]) * 100
                else:
                    correlation = 0
                    
                p1_base = pred1["Close"].iloc[0]
                p2_base = pred2["Close"].iloc[0]
                pred1["Perf"] = ((pred1["Close"] - p1_base) / p1_base) * 100
                pred2["Perf"] = ((pred2["Close"] - p2_base) / p2_base) * 100
                perf_gap = abs(pred1["Perf"].iloc[-1] - pred2["Perf"].iloc[-1])

                if correlation >= 80:
                    st.success(f"**คะแนนความเหมือน:** {correlation:.2f}% 👯 (ยืนยัน: สองตัวนี้คือ **หุ้นแฝด!** วิ่งตามกันเสมอ)")
                    if perf_gap > 3.0: # ถ้าห่างกันเกิน 3% ให้สัญญาณ Arbitrage
                        laggard = sym1 if pred1["Perf"].iloc[-1] < pred2["Perf"].iloc[-1] else sym2
                        leader = sym2 if laggard == sym1 else sym1
                        st.info(f"💡 **สัญญาณเก็งกำไรขั้นสูง (Arbitrage):** ตอนนี้ **{leader}** พุ่งนำหน้าไปแล้ว ทิ้งให้ **{laggard}** รั้งท้าย (Gap ห่างกัน {perf_gap:.2f}%) นี่คือจังหวะทองในการเข้าซื้อ **{laggard}** เพื่อเก็งกำไรตอนที่ราคามันวิ่งตามไปปิดช่องว่าง!")
                    else:
                        st.warning("💡 ตอนนี้หุ้นแฝดคู่นี้ยังวิ่งตีคู่กันมา สูสีมากครับ ยังไม่มีช่องว่าง Arbitrage ให้ทำกำไร")
                        
                elif correlation >= 50:
                    st.info(f"**คะแนนความเหมือน:** {correlation:.2f}% (วิ่งคล้ายกัน) มีความสัมพันธ์กันในระดับปานกลาง")
                elif correlation <= -50:
                    st.error(f"**คะแนนความเหมือน:** {correlation:.2f}% 🧲 (วิ่งสวนทางกันชัดเจน) เหมาะสำหรับซื้อตัวนึงเพื่อ Hedging พอร์ต")
                else:
                    st.warning(f"**คะแนนความเหมือน:** {correlation:.2f}% (ต่างคนต่างวิ่ง) สองตัวนี้แทบไม่มีความเชื่อมโยงกันเลย")
                
                st.markdown("---")
                
                # --- กรรมการชูมือ ---
                if s1_score > s2_score:
                    st.success(f"🏆 **ผู้ชนะ AI Score:** 🔵 {sym1} ({s1_score:.2f}% ชนะ {sym2} ที่ได้ {s2_score:.2f}%)")
                elif s2_score > s1_score:
                    st.success(f"🏆 **ผู้ชนะ AI Score:** 🔴 {sym2} ({s2_score:.2f}% ชนะ {sym1} ที่ได้ {s1_score:.2f}%)")
                else:
                    st.warning("🤝 เสมอกัน! (กรรมการให้คะแนนเท่ากันเป๊ะ)")
                
                st.markdown("### 📈 กราฟเปรียบเทียบผลงาน (Performance %)")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=pred1.index, y=pred1["Perf"], name=f"🔵 {sym1}", line=dict(color='#00b4d8', width=2)))
                fig.add_trace(go.Scatter(x=pred2.index, y=pred2["Perf"], name=f"🔴 {sym2}", line=dict(color='#ff4d4d', width=2)))
                
                fig.update_layout(yaxis_title="ผลตอบแทน / ขาดทุน (%)", template="plotly_dark", height=500, hovermode="x unified")
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
