"""
Gradio UI — Solar Fleet Intelligence Dashboard.
"""
import gradio as gr
import pandas as pd
import numpy as np
import joblib

model = joblib.load('models/best_model.pkl')
FEATURES = joblib.load('models/feature_names.pkl')
metrics = joblib.load('models/metrics.pkl')


def predict_efficiency(hour, month, is_monsoon, temperature, irradiance,
                       dc_power, load_ratio, days_since_start, eff_lag1):
    d = {
        'hour': hour, 'month': month, 'is_monsoon': int(is_monsoon),
        'temperature': temperature, 'temp_roll3': temperature,
        'temp_deviation': temperature - 25.0,
        'irradiance': irradiance, 'irr_roll3': irradiance,
        'irr_per_temp': irradiance / (temperature + 1),
        'dc_power': dc_power, 'load_ratio': load_ratio,
        'load_x_temp': load_ratio * temperature,
        'days_since_start': days_since_start, 'eff_lag1': eff_lag1,
    }
    X = pd.DataFrame([d])[FEATURES].astype(np.float64)
    pred = float(model.predict(X)[0])
    pct = round(pred * 100, 2)

    if pred > 0.95:
        verdict = "✅ EXCELLENT — Optimal operation"
    elif pred > 0.90:
        verdict = "🟢 HEALTHY — Within spec"
    elif pred > 0.85:
        verdict = "⚠️ WARNING — Investigate soon"
    else:
        verdict = "🔴 CRITICAL — Immediate action needed"

    return f"{pct}%", verdict


def load_fleet_health():
    return pd.read_csv('data/fleet_health.csv')


def load_cost_impact():
    return pd.read_csv('data/cost_impact.csv')


with gr.Blocks(title="Solar Fleet Intelligence", theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"""
    # 🔆 Solar Fleet Intelligence
    ### Predict inverter efficiency, monitor fleet health, estimate ₹ impact
    **Model:** {metrics['model_name']} | **Test R²:** {metrics['r2']:.4f} | **MAE:** {metrics['mae']:.4f}
    """)

    with gr.Tab("🎯 Predict Efficiency"):
        with gr.Row():
            with gr.Column():
                hour = gr.Slider(6, 18, value=12, step=1, label="Hour of Day")
                month = gr.Slider(1, 12, value=6, step=1, label="Month")
                is_monsoon = gr.Checkbox(label="Monsoon Season")
                temperature = gr.Slider(10.0, 55.0, value=30.0, step=0.5, label="Temperature (°C)")
            with gr.Column():
                irradiance = gr.Slider(0.0, 1100.0, value=700.0, step=10.0, label="Irradiance (W/m²)")
                dc_power = gr.Slider(0.0, 120.0, value=70.0, step=1.0, label="DC Power (kW)")
                load_ratio = gr.Slider(0.0, 1.2, value=0.7, step=0.05, label="Load Ratio")
                days_since_start = gr.Slider(0, 365, value=180, step=1, label="Days Since Commissioning")
                eff_lag1 = gr.Slider(0.5, 1.0, value=0.93, step=0.01, label="Previous Hour Efficiency")

        btn = gr.Button("🚀 Predict", variant="primary")
        with gr.Row():
            eff_out = gr.Textbox(label="Predicted Efficiency")
            verdict_out = gr.Textbox(label="Status")

        btn.click(predict_efficiency,
                  inputs=[hour, month, is_monsoon, temperature, irradiance,
                          dc_power, load_ratio, days_since_start, eff_lag1],
                  outputs=[eff_out, verdict_out])

    with gr.Tab("🚨 Fleet Health"):
        gr.Markdown("### Anomaly detection across 10 inverters (Isolation Forest)")
        fleet_btn = gr.Button("Load Fleet Health", variant="secondary")
        fleet_table = gr.Dataframe(label="Fleet Health")
        fleet_btn.click(load_fleet_health, outputs=fleet_table)

    with gr.Tab("💰 Cost Impact"):
        gr.Markdown("### ₹ Loss due to inefficiency (annualized)")
        cost_btn = gr.Button("Load Cost Impact", variant="secondary")
        cost_table = gr.Dataframe(label="Cost Impact (₹)")
        cost_btn.click(load_cost_impact, outputs=cost_table)


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, show_error=True)