"""
Solar Fleet Intelligence - Realistic Synthetic Data Generator
Physics-based simulation using IEC 61724 standards + real inverter datasheet params.
NOTE: Synthetic for development. In production, swap with SCADA/CSV feed.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---------------- Config ----------------
N_INVERTERS = 10
DAYS = 365
START_DATE = datetime(2024, 1, 1)
INVERTER_CAPACITY_KW = 100  # each inverter rated 100 kW

# 3 inverters deliberately unhealthy
FAULTY = {'INV-003': 'soiling', 'INV-007': 'aging', 'INV-009': 'faulty_sensor'}

inverter_ids = [f"INV-{i:03d}" for i in range(1, N_INVERTERS + 1)]

rows = []

for inv_id in inverter_ids:
    # Per-inverter baseline health (0.90 - 1.00)
    base_health = np.random.uniform(0.94, 1.00)
    fault_type = FAULTY.get(inv_id, None)

    for day in range(DAYS):
        date = START_DATE + timedelta(days=day)
        doy = date.timetuple().tm_yday

        # Seasonal irradiance (India: peak Mar-May, low Jul-Aug monsoon, low Dec-Jan)
        seasonal = 0.75 + 0.35 * np.sin(2 * np.pi * (doy - 80) / 365)
        monsoon_penalty = 0.25 if 180 <= doy <= 260 else 0.0

        # 24 hourly readings per day (or just daylight hours: 6 to 18)
        for hour in range(6, 19):
            # Solar elevation curve (peak at noon)
            sun_angle = max(0.0, np.sin(np.pi * (hour - 6) / 12))

            # Irradiance (W/m²)
            irradiance = 1000 * sun_angle * seasonal
            irradiance *= (1 - monsoon_penalty)
            irradiance += np.random.normal(0, 30)
            irradiance = max(0, irradiance)

            # Ambient temperature (°C): hotter midday, cooler in monsoon
            temp = 22 + 12 * sun_angle
            temp += 5 * np.sin(2 * np.pi * (doy - 150) / 365)   # seasonal
            temp -= 4 * monsoon_penalty * 10
            temp += np.random.normal(0, 1.5)

            # DC power generated (kW)
            dc_power = INVERTER_CAPACITY_KW * (irradiance / 1000) * base_health
            dc_power += np.random.normal(0, 2)
            dc_power = max(0, dc_power)

            # ---------- Efficiency Physics ----------
            # 1. Temperature effect (datasheet: -0.35%/°C above 25°C)
            temp_loss = 0.0035 * max(0, temp - 25)

            # 2. Load ratio effect (low load → lower eff)
            load_ratio = dc_power / INVERTER_CAPACITY_KW
            load_loss = 0.04 * (1 - min(load_ratio, 1.0)) ** 2

            # 3. Soiling (dust) - accumulates then rain cleans
            soiling = min(0.05, (day % 30) * 0.0015)
            if 180 <= doy <= 260:  # monsoon washes
                soiling *= 0.3

            # 4. Aging (gradual)
            aging = day * 0.00003

            # 5. Per-inverter fault
            fault_loss = 0.0
            if fault_type == 'soiling':
                fault_loss = 0.08
            elif fault_type == 'aging':
                fault_loss = aging * 5
            elif fault_type == 'faulty_sensor':
                fault_loss = 0.03 + 0.02 * np.sin(day / 10)

            efficiency = (
                0.98
                - temp_loss
                - load_loss
                - soiling
                - aging
                - fault_loss
                + np.random.normal(0, 0.008)
            )
            efficiency = float(np.clip(efficiency, 0.3, 1.0))

            ac_power = dc_power * efficiency
            energy_kwh = ac_power  # 1-hour interval

            rows.append({
                'timestamp': date.replace(hour=hour),
                'inverter_id': inv_id,
                'hour': hour,
                'day_of_year': doy,
                'temperature': round(temp, 2),
                'irradiance': round(irradiance, 2),
                'dc_power': round(dc_power, 2),
                'ac_power': round(ac_power, 2),
                'energy_kwh': round(energy_kwh, 2),
                'efficiency': round(efficiency, 4),
            })

df = pd.DataFrame(rows)

# ---------- Inject real-world mess ----------
# 1. Missing values (sensor dropout ~2%)
for col in ['temperature', 'irradiance', 'dc_power', 'ac_power', 'efficiency']:
    mask = np.random.rand(len(df)) < 0.02
    df.loc[mask, col] = np.nan

# 2. Outliers (sensor spikes)
n_out = int(len(df) * 0.002)
out_idx = np.random.choice(len(df), n_out, replace=False)
df.loc[out_idx, 'temperature'] = np.random.uniform(70, 120, n_out)
df.loc[out_idx, 'irradiance'] = np.random.uniform(1400, 2000, n_out)

# Save
df.to_csv('data/inverter_fleet_data.csv', index=False)

print(f"✅ Rows: {len(df):,}")
print(f"✅ Inverters: {df['inverter_id'].nunique()}")
print(f"✅ Date range: {df['timestamp'].min()} → {df['timestamp'].max()}")
print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nEfficiency stats:\n{df['efficiency'].describe()}")
print(f"\nSample:\n{df.head()}")