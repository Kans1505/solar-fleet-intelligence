"""
FastAPI backend for Solar Fleet Intelligence.
Exposes /predict and /fleet-health endpoints.
"""
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib

app = FastAPI(title="Solar Fleet Intelligence API", version="1.0")

model = joblib.load('models/best_model.pkl')
FEATURES = joblib.load('models/feature_names.pkl')
metrics = joblib.load('models/metrics.pkl')


class PredictRequest(BaseModel):
    hour: int
    month: int
    is_monsoon: int
    temperature: float
    temp_roll3: float
    irradiance: float
    irr_roll3: float
    dc_power: float
    load_ratio: float
    days_since_start: int
    eff_lag1: float


@app.get("/")
def root():
    return {
        "name": "Solar Fleet Intelligence API",
        "version": "1.0",
        "model": metrics['model_name'],
        "test_r2": round(metrics['r2'], 4),
        "test_mae": round(metrics['mae'], 4),
    }


@app.post("/predict")
def predict(req: PredictRequest):
    d = req.dict()
    d['temp_deviation'] = d['temperature'] - 25.0
    d['irr_per_temp'] = d['irradiance'] / (d['temperature'] + 1)
    d['load_x_temp'] = d['load_ratio'] * d['temperature']

    X = pd.DataFrame([d])[FEATURES].astype(np.float64)
    pred = float(model.predict(X)[0])

    if pred > 0.95:
        status = "excellent"
    elif pred > 0.90:
        status = "healthy"
    elif pred > 0.85:
        status = "warning"
    else:
        status = "critical"

    return {
        "predicted_efficiency": round(pred, 4),
        "predicted_efficiency_pct": round(pred * 100, 2),
        "status": status,
    }


@app.get("/fleet-health")
def fleet_health():
    df = pd.read_csv('data/fleet_health.csv')
    return df.to_dict(orient='records')


@app.get("/cost-impact")
def cost_impact():
    df = pd.read_csv('data/cost_impact.csv')
    return df.to_dict(orient='records')