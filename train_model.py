"""
GridHaat — AI Anomaly Detection Model
Trains Isolation Forest on BD energy consumption patterns.
Outputs anomaly scores used by the dashboard.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle, os

def train_model():
    print("Loading data...")
    df = pd.read_csv("data/bd_energy_data.csv", parse_dates=["timestamp"])

    # Feature engineering
    df["hour_sin"]   = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"]   = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"]    = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"]    = np.cos(2 * np.pi * df["day_of_week"] / 7)

    # Per-sector normalization
    df["consumption_norm"] = df.groupby("sector")["consumption_mw"].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    df["rolling_mean_6h"] = df.groupby("sector")["consumption_mw"].transform(
        lambda x: x.rolling(6, min_periods=1).mean()
    )
    df["deviation_from_rolling"] = df["consumption_mw"] - df["rolling_mean_6h"]

    FEATURES = [
        "consumption_norm", "deviation_from_rolling",
        "hour_sin", "hour_cos", "dow_sin", "dow_cos", "is_weekend"
    ]

    scaler  = StandardScaler()
    X       = scaler.fit_transform(df[FEATURES].fillna(0))

    print("Training Isolation Forest...")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.12,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X)

    scores = model.decision_function(X)
    preds  = model.predict(X)

    # Normalize scores to 0-100 anomaly scale (100 = most anomalous)
    score_min, score_max = scores.min(), scores.max()
    df["anomaly_score"] = (1 - (scores - score_min) / (score_max - score_min)) * 100
    df["is_anomaly"]    = (preds == -1).astype(int)

    # Evaluate against ground truth
    from sklearn.metrics import precision_score, recall_score, f1_score
    gt  = df["is_wastage_event"].astype(int)
    pr  = df["is_anomaly"]
    p   = precision_score(gt, pr)
    r   = recall_score(gt, pr)
    f1  = f1_score(gt, pr)
    print(f"  Precision: {p:.3f} | Recall: {r:.3f} | F1: {f1:.3f}")

    # Save enriched data + model artifacts
    df.to_csv("data/bd_energy_scored.csv", index=False)
    os.makedirs("models", exist_ok=True)
    with open("models/isolation_forest.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("models/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("models/features.pkl", "wb") as f:
        pickle.dump(FEATURES, f)

    # Recent 7 days for live simulation
    recent = df[df["timestamp"] >= df["timestamp"].max() - pd.Timedelta(days=7)].copy()
    recent.to_csv("data/recent_7days.csv", index=False)

    print(f"\nModel saved. {int(df['is_anomaly'].sum())} anomalies detected in 90 days.")
    print(f"Top wastage sectors:")
    top = df[df["is_anomaly"]==1].groupby("sector")["wastage_mw"].sum().sort_values(ascending=False)
    for s, v in top.head(5).items():
        print(f"  {s[:45]}: {v:.0f} MW-hrs wasted")

if __name__ == "__main__":
    train_model()
