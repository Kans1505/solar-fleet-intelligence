# Solar Fleet Intelligence — Tata Power Internship Project

**Tata Power Renewable Energy Limited | Python Internship | Sept – Oct 2026**

A production-oriented machine learning system for predicting solar inverter efficiency, monitoring fleet health, and quantifying cost impact — built during my internship at Tata Power Renewable Energy Limited (TPREL).

## 👤 Student Details

| Field | Details |
|---|---|
| Name | Kanishka Nandini |
| Roll Number | 2410031177 |
| Institute | IILM University, Greater Noida, U.P. |
| Programme | B.Tech CSE (AI) |
| Internship Domain | Python Intern |
| Organization | Tata Power Renewable Energy Limited (TPREL) |
| Duration | 1 Month (September 02, 2026 – October 01, 2026) |
| Reporting Guide | Mr. Paresh Onsker — Group Head, Infra & Support |
| GitHub | @Kans1505 |
| LinkedIn | linkedin.com/in/kanishka-nandini |

## 📌 About the Internship

During my internship at Tata Power Renewable Energy Limited, I worked on building an ML-driven system to analyze solar inverter performance across a fleet. The goal: predict efficiency from operating conditions, detect anomalous inverters, and quantify the financial impact of efficiency loss in ₹ — enabling proactive maintenance and ROI decisions.

## 🎯 Objectives

- Predict solar inverter efficiency from physical drivers (temperature, load, irradiance, weather, aging)
- Build a fleet-level anomaly detection system to flag underperforming inverters
- Quantify ₹ cost impact of efficiency loss, per inverter and fleet-wide
- Provide SHAP-based explainability for audit and decision-making
- Deploy a production-ready REST API and interactive dashboard

## 🗓️ Project Timeline

| Phase | Module | Description |
|---|---|---|
| Week 1 | Data & EDA | Physics-based synthetic data generation, feature engineering |
| Week 2 | Modeling | XGBoost + LightGBM, 5-fold CV, time-aware split |
| Week 3 | Explainability & Anomaly | SHAP analysis, Isolation Forest for fleet health |
| Week 4 | Deployment | FastAPI backend, Gradio dashboard, cost impact reporting |

## 📊 Results

| Metric | Value |
|---|---|
| Test R² | **0.9004** |
| Test MAE | **0.0083** |
| 5-Fold CV R² | **0.9058 ± 0.0014** |
| Fleet annual loss detected | **₹5.55 Lakh** |
| Faulty inverters flagged | **3 of 10** |

## 🛠️ Technologies & Tools

Python · Pandas · NumPy · Scikit-learn · XGBoost · LightGBM · SHAP · Isolation Forest · FastAPI · Uvicorn · Gradio · Joblib · Matplotlib

## 🚀 Key Features

- **Efficiency Prediction** — XGBoost model from temperature, load, irradiance, weather, aging
- **Fleet Health Monitoring** — Isolation Forest flags anomalous inverters on residuals
- **Cost Impact Analysis** — ₹ loss per inverter, annualized
- **SHAP Explainability** — top drivers of efficiency (temperature is #1)
- **REST API** — production-ready endpoints with Swagger docs
- **Interactive Dashboard** — Gradio UI with 3 tabs

## 📁 Project Structure

```
solar-fleet-intelligence/
├── data/
│   └── make_data.py            # Physics-based synthetic data generator
├── src/
│   ├── features.py             # Feature engineering
│   ├── train_v4.py             # XGBoost model training (5-fold CV)
│   ├── explain.py              # SHAP explainability
│   ├── anomaly.py              # Isolation Forest anomaly detection
│   └── cost.py                 # ₹ cost impact analysis
├── api/
│   └── main.py                 # FastAPI backend
├── app/
│   └── gradio_app.py           # Gradio dashboard
├── models/                     # Trained model artifacts (gitignored)
├── requirements.txt
└── README.md
```

## 🔧 Setup & Run

```bash
# 1. Clone
git clone https://github.com/Kans1505/solar-fleet-intelligence.git
cd solar-fleet-intelligence

# 2. Install dependencies
py -m pip install -r requirements.txt

# 3. Generate data + train model
py data/make_data.py
py src/features.py
py src/train_v4.py
py src/anomaly.py
py src/cost.py

# 4. Launch dashboard
py app/gradio_app.py

# 5. Launch API (optional)
py -m uvicorn api.main:app --reload
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Model info |
| POST | `/predict` | Predict inverter efficiency |
| GET | `/fleet-health` | Fleet anomaly status |
| GET | `/cost-impact` | ₹ loss analysis |

## 🔍 Model Details

- **Algorithm:** XGBoost Regressor (400 trees, learning rate 0.05, max depth 6)
- **Features (14):** hour, month, is_monsoon, temperature, temp_roll3, temp_deviation, irradiance, irr_roll3, irr_per_temp, dc_power, load_ratio, load_x_temp, days_since_start, eff_lag1
- **Split:** 80/20 stratified by month
- **Validation:** 5-fold cross-validation
- **Explainability:** SHAP TreeExplainer

## 🚨 Anomaly Detection & Cost Impact

Isolation Forest on model residuals identified **3 faulty inverters** (INV-003, INV-007, INV-009) out of 10 with anomaly rates of 2–3.5% vs fleet baseline 1.5%.

Cost analysis (tariff ₹8/kWh, nominal efficiency 95%):
- **INV-003 (soiling):** ₹1.55 Lakh/year loss
- **INV-007 (aging):** ₹0.77 Lakh/year loss
- **INV-009 (sensor fault):** ₹0.81 Lakh/year loss
- **Fleet total:** ₹5.55 Lakh/year

## ⚠️ Data Note

Synthetic dataset generated using **IEC 61724 standards** and real inverter datasheet parameters (temperature coefficient -0.35%/°C, soiling model, monsoon adjustments). Production deployment requires SCADA integration — the pipeline is designed to be **swap-ready** with real CSV feeds.


Thanks to **Tata Power Renewable Energy Limited** for the internship opportunity, and to my reporting guide **Mr. Paresh Onsker (Group Head, Infra & Support)** for guidance throughout the project. Grateful to **IILM University, Greater Noida** for continuous academic support.

**Kanishka Nandini** · B.Tech CSE (AI) · IILM University, Greater Noida
