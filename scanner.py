from data_loader import get_data
from ai_engine import load_model, predict

TICKERS = ["AAPL","MSFT","TSLA","NVDA","AMD","SPY","QQQ"]

def scan_market():
    model = load_model()
    results = []

    for t in TICKERS:
        df = get_data(t)
        pred = predict(df, model)

        if not pred.empty:
            score = pred["score"].iloc[-1]
            results.append({
                "symbol": t,
                "score": round(score, 2)
            })

    return sorted(results, key=lambda x: x["score"], reverse=True)
