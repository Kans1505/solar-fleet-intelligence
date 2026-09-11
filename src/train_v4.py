"""
FINAL production model — XGBoost only (LightGBM DLL issue on Py3.14).
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error
from xgboost import XGBRegressor

df = pd.read_csv('data/inverter_features.csv', parse_dates=['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()).dt.days
df['temp_deviation'] = df['temperature'] - 25.0
df['irr_per_temp'] = df['irradiance'] / (df['temperature'] + 1)
df['load_x_temp'] = df['load_ratio'] * df['temperature']

FEATURES = [
    'hour', 'month', 'is_monsoon',
    'temperature', 'temp_roll3', 'temp_deviation',
    'irradiance', 'irr_roll3', 'irr_per_temp',
    'dc_power', 'load_ratio', 'load_x_temp',
    'days_since_start', 'eff_lag1'
]
TARGET = 'efficiency'

X = df[FEATURES].astype(np.float64)
y = df[TARGET].astype(np.float64)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=df['month']
)

model = XGBRegressor(n_estimators=400, learning_rate=0.05, max_depth=6,
                     random_state=42, tree_method='hist')

kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv = cross_val_score(model, X_train, y_train, cv=kf, scoring='r2', n_jobs=-1)
print(f"XGBoost CV R² = {cv.mean():.4f} ± {cv.std():.4f}")

model.fit(X_train, y_train)
pred = model.predict(X_test)
r2 = r2_score(y_test, pred)
mae = mean_absolute_error(y_test, pred)
print(f"XGBoost TEST: R² = {r2:.4f} | MAE = {mae:.4f}")

joblib.dump(model, 'models/best_model.pkl')
joblib.dump(FEATURES, 'models/feature_names.pkl')
joblib.dump({'model_name': 'XGBoost', 'r2': r2, 'mae': mae}, 'models/metrics.pkl')
print("✅ Saved -> models/")