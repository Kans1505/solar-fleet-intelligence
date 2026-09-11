"""
SHAP explainability for the FINAL model.
"""
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt

df = pd.read_csv('data/inverter_features.csv', parse_dates=['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

# Recreate same features as train_v3
df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()).dt.days
df['temp_deviation'] = df['temperature'] - 25.0
df['irr_per_temp'] = df['irradiance'] / (df['temperature'] + 1)
df['load_x_temp'] = df['load_ratio'] * df['temperature']

FEATURES = joblib.load('models/feature_names.pkl')
model = joblib.load('models/best_model.pkl')

sample = df.sample(2000, random_state=42)
X_sample = sample[FEATURES].astype(np.float64)

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_sample)

plt.figure()
shap.summary_plot(shap_values, X_sample, feature_names=FEATURES, plot_type='bar', show=False)
plt.tight_layout()
plt.savefig('shap_bar.png', dpi=120, bbox_inches='tight')
plt.close()

plt.figure()
shap.summary_plot(shap_values, X_sample, feature_names=FEATURES, show=False)
plt.tight_layout()
plt.savefig('shap_summary.png', dpi=120, bbox_inches='tight')
plt.close()

mean_abs = np.abs(shap_values).mean(axis=0)
top = sorted(zip(FEATURES, mean_abs), key=lambda x: -x[1])[:5]
print("🔝 Top 5 drivers of efficiency:")
for i, (f, v) in enumerate(top, 1):
    print(f"  {i}. {f}  ({v:.4f})")
print("\n✅ Saved -> shap_bar.png, shap_summary.png")