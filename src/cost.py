"""
Cost impact analysis.
Estimates ₹ lost due to efficiency drop, per inverter.
"""
import pandas as pd

# --- Assumptions (Tata Solar typical) ---
TARIFF_PER_KWH = 8.0        # ₹ per kWh (commercial solar)
NOMINAL_EFFICIENCY = 0.95   # target efficiency for healthy inverter
DAYS_IN_YEAR = 365

df = pd.read_csv('data/inverter_features.csv', parse_dates=['timestamp'])

# Per-inverter stats
stats = df.groupby('inverter_id').agg(
    total_energy_kwh=('energy_kwh', 'sum'),
    avg_efficiency=('efficiency', 'mean'),
    days=('timestamp', lambda s: (s.max() - s.min()).days + 1),
).reset_index()

# Expected energy if efficiency were nominal
stats['expected_energy_kwh'] = stats['total_energy_kwh'] * (NOMINAL_EFFICIENCY / stats['avg_efficiency'])
stats['energy_loss_kwh'] = stats['expected_energy_kwh'] - stats['total_energy_kwh']
stats['revenue_loss_inr'] = stats['energy_loss_kwh'] * TARIFF_PER_KWH

# Annualize
stats['annual_loss_inr'] = (stats['revenue_loss_inr'] / stats['days']) * DAYS_IN_YEAR

stats = stats.sort_values('annual_loss_inr', ascending=False)

total_annual = stats['annual_loss_inr'].sum()

print("💰 COST IMPACT ANALYSIS (per inverter)")
print("=" * 70)
print(stats[['inverter_id', 'avg_efficiency', 'energy_loss_kwh',
             'annual_loss_inr']].to_string(index=False))
print("=" * 70)
print(f"📊 Fleet annual loss due to inefficiency: ₹{total_annual:,.0f}")
print(f"📊 Monthly loss: ₹{total_annual/12:,.0f}")
print(f"📊 Per-inverter avg annual loss: ₹{total_annual/len(stats):,.0f}")

stats.to_csv('data/cost_impact.csv', index=False)
print("\n✅ Saved -> data/cost_impact.csv")