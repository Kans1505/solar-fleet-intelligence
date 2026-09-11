"""
Anomaly detection for fleet health monitoring.
Flags inverters whose efficiency deviates from expected pattern.
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest

df = pd.read_csv('data/inverter_features.csv', parse_dates=['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()).dt.days
df['temp_deviation'] = df['temperature'] - 25.0
df['irr_per_temp'] = df['irradiance'] / (df['temperature'] + 1)
df['load_x_temp'] = df['load_ratio'] * df['temperature']

FEATURES = joblib.load('models/feature_names.pkl')
model = joblib.load('models/best_model.pkl')

# Predicted vs actual -> residual = anomaly signal
X = df[FEATURES].astype(np.float64)
df['predicted_efficiency'] = model.predict(X)
df['residual'] = df['efficiency'] - df['predicted_efficiency']

# Isolation Forest on residuals + key features
iso_features = ['residual', 'temperature', 'load_ratio', 'days_since_start']
iso = IsolationForest(contamination=0.02, random_state=42)
df['anomaly'] = iso.fit_predict(df[iso_features])
df['anomaly'] = df['anomaly'].map({1: 'normal', -1: 'anomaly'})

# Per-inverter anomaly rate
summary = df.groupby('inverter_id').agg(
    anomaly_count=('anomaly', lambda s: (s == 'anomaly').sum()),
    total=('anomaly', 'count'),
    avg_efficiency=('efficiency', 'mean'),
    avg_residual=('residual', 'mean'),
).reset_index()
summary['anomaly_rate_%'] = (summary['anomaly_count'] / summary['total'] * 100).round(2)
summary = summary.sort_values('anomaly_rate_%', ascending=False)

print("🚨 Fleet Health Summary:")
print(summary.to_string(index=False))

# Save
summary.to_csv('data/fleet_health.csv', index=False)
df[['timestamp', 'inverter_id', 'efficiency', 'predicted_efficiency', 'residual', 'anomaly']].to_csv(
    'data/anomaly_results.csv', index=False
)
print("\n✅ Saved -> data/fleet_health.csv, data/anomaly_results.csv")