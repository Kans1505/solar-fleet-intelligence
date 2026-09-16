"""
FastAPI backend for Solar Fleet Intelligence.
Now with API key authentication + request logging + CORS.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib

from api.auth import verify_api_key, log_request

app = FastAPI(title="Solar Fleet Intelligence API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(log_request)

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
    """Public endpoint — no auth required."""
    return {
        "name": "Solar Fleet Intelligence API",
        "version": "2.0",
        "model": metrics['model_name'],
        "test_r2": round(metrics['r2'], 4),
        "test_mae": round(metrics['mae'], 4),
        "auth": "X-API-Key header required for /predict, /fleet-health, /cost-impact"
    }


@app.post("/predict")
def predict(req: PredictRequest, user: str = Depends(verify_api_key)):
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
        "requested_by": user
    }


@app.get("/fleet-health")
def fleet_health(user: str = Depends(verify_api_key)):
    df = pd.read_csv('data/fleet_health.csv')
    return {"requested_by": user, "data": df.to_dict(orient='records')}


@app.get("/cost-impact")
def cost_impact(user: str = Depends(verify_api_key)):
    df = pd.read_csv('data/cost_impact.csv')
    return {"requested_by": user, "data": df.to_dict(orient='records')}