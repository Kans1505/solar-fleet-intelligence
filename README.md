\# 🔆 Solar Fleet Intelligence



ML system for solar inverter efficiency prediction, fleet health monitoring, and cost-impact analysis.



\## 🎯 Problem

Solar inverters lose efficiency due to temperature, load, soiling, and aging. Identifying \*\*why\*\* and \*\*how much it costs\*\* enables proactive maintenance and ROI decisions.



\## 📊 Results

| Metric | Value |

|---|---|

| Test R² | \*\*0.9004\*\* |

| Test MAE | \*\*0.0083\*\* |

| 5-Fold CV R² | \*\*0.9058 ± 0.0014\*\* |

| Fleet annual loss detected | \*\*₹5.55 Lakh\*\* |



\## 🛠️ Tech Stack

\- \*\*Model:\*\* XGBoost (LightGBM equivalent)

\- \*\*Explainability:\*\* SHAP

\- \*\*Anomaly Detection:\*\* Isolation Forest

\- \*\*Backend:\*\* FastAPI

\- \*\*Frontend:\*\* Gradio

\- \*\*Data:\*\* Physics-based synthetic (IEC 61724 + real inverter datasheet params)



\## 🚀 Features

\- \*\*Efficiency Prediction\*\* — from temp, load, irradiance, weather, aging

\- \*\*Fleet Health Monitoring\*\* — Isolation Forest flags anomalous inverters

\- \*\*Cost Impact Analysis\*\* — ₹ loss per inverter, annualized

\- \*\*SHAP Explainability\*\* — top drivers of efficiency

\- \*\*REST API\*\* — production-ready endpoints

\- \*\*Interactive Dashboard\*\* — Gradio UI



\## 📁 Project Structure

