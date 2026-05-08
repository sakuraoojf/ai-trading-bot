import streamlit as st
import plotly.graph_objects as go
from data_loader import get_data
from ai_engine import train_model, load_model, predict
from scanner import scan_market

st.title("🚀 AI Trading Super Dashboard (ML)")
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Scanner", "Train Model"])

if menu == "Dashboard":
    symbol = st.text_input("Symbol", "AAPL")
    df = get_data(symbol)
    model = load_model()
    pred = predict(df, model)

    if not pred.empty:
        st.metric("AI Score", f"{pred['score'].iloc[-1]:.2f}%")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=pred.index, open=pred["Open"], high=pred["High"],
            low=pred["Low"], close=pred["Close"]
        ))
        st.plotly_chart(fig)
    else:
        st.error("Not enough data to calculate indicators.")

elif menu == "Scanner":
    st.subheader("📊 Market Scanner")
    results = scan_market()
    st.table(results)

elif menu == "Train Model":
    st.subheader("🤖 Train AI Model")
    symbol = st.text_input("Train with symbol", "AAPL")
    if st.button("Train"):
        df = get_data(symbol)
        model = train_model(df)
        st.success("Model trained successfully!")
