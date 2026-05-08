import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

MODEL_PATH = "model.pkl"
FEATURES = ["return", "rsi", "ema_diff", "volume_ratio"]

def prepare_features(df):
    df = df.copy()
    df["return"] = df["Close"].pct_change()
    df["ema_diff"] = df["EMA20"] - df["EMA50"]
    df["volume_ratio"] = df["Volume"] / df["VOL_SMA"]
    df = df.dropna()
    df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
    return df.dropna()

def train_model(df):
    df = prepare_features(df)
    X = df[FEATURES]
    y = df["target"]
    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return model

def load_model():
    if not os.path.exists(MODEL_PATH):
        print("Auto-training initial model on AAPL...")
        from data_loader import get_data
        df = get_data("AAPL")
        train_model(df)
    return joblib.load(MODEL_PATH)

def predict(df, model):
    df = prepare_features(df)
    X = df[FEATURES]
    proba = model.predict_proba(X)[:, 1]
    df["score"] = proba * 100
    return df
