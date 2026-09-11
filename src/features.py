"""
Feature engineering for solar fleet intelligence.
Creates time-series + physics features from raw SCADA-style data.
"""
import pandas as pd
import numpy as np

def load_and_clean(path='data/inverter_fleet_data.csv'):
    df = pd.read_csv(path, parse_dates=['timestamp'])
    df = df.sort_values(['inverter_id', 'timestamp']).reset_index(drop=True)

    # Handle missing values: forward-fill within each inverter (sensor dropout)
    for col in ['temperature', 'irradiance', 'dc_power', 'ac_power', 'efficiency']:
        df[col] = df.groupby('inverter_id')[col].transform(
            lambda s: s.ffill().bfill()
        )

    # Drop remaining NaN (very few)
    df = df.dropna().reset_index(drop=True)
    return df


def add_features(df):
    # Time features
    df['month'] = df['timestamp'].dt.month
    df['is_monsoon'] = df['month'].isin([7, 8, 9]).astype(int)

    # Physics: performance ratio proxy
    df['load_ratio'] = df['dc_power'] / 100.0

    # Per-inverter rolling features (window = 3 hours)
    g = df.groupby('inverter_id')
    df['temp_roll3'] = g['temperature'].transform(lambda s: s.rolling(3, min_periods=1).mean())
    df['irr_roll3'] = g['irradiance'].transform(lambda s: s.rolling(3, min_periods=1).mean())
    df['eff_roll3'] = g['efficiency'].transform(lambda s: s.rolling(3, min_periods=1).mean())

    # Lag features (previous hour)
    df['eff_lag1'] = g['efficiency'].shift(1)
    df['temp_lag1'] = g['temperature'].shift(1)

    # Daily cumulative energy per inverter (proxy for aging / daily total)
    df['day'] = df['timestamp'].dt.date
    df['daily_energy'] = df.groupby(['inverter_id', 'day'])['energy_kwh'].transform('sum')

    # Fill lag NaNs
    df['eff_lag1'] = df['eff_lag1'].fillna(df['efficiency'])
    df['temp_lag1'] = df['temp_lag1'].fillna(df['temperature'])

    return df


if __name__ == '__main__':
    df = load_and_clean()
    df = add_features(df)
    df.to_csv('data/inverter_features.csv', index=False)
    print(f"✅ Features created: {df.shape}")
    print(f"✅ Columns: {list(df.columns)}")
    print(f"\nSample:\n{df.head(3)}")