import pandas as pd
import numpy as np

# ────────────────────────────────────────────────
# 1. Load historical returns (same as before)
# ────────────────────────────────────────────────
url = "https://www.stern.nyu.edu/~adamodar/pc/datasets/histretSP.xls"
df = pd.read_excel(url, sheet_name="Returns", skiprows=12)
df = df[['Year', 'S&P 500', 'US T. Bond (10-year)', 'Inflation']].dropna()
df = df[df['Year'] >= 1928].reset_index(drop=True)

stocks = df['S&P 500']
bonds  = df['US T. Bond (10-year)']
infl   = df['Inflation']

real_stocks_mean = ((1 + stocks) / (1 + infl) - 1).mean()
real_bonds_mean  = ((1 + bonds) / (1 + infl) - 1).mean()

print("Historical real returns (geometric-ish approximation):")
print(f"  Stocks: {real_stocks_mean:.1%}")
print(f"  Bonds:  {real_bonds_mean:.1%}\n")

# ────────────────────────────────────────────────
# 2. READ YOUR PERSONAL VALUES FROM CSV
# ────────────────────────────────────────────────
config_file = "savings.csv"          # ← change if filename is different

try:
    config = pd.read_csv(config_file)
    initial     = float(config['initial_savings'].iloc[0])
    age         = int(config['current_age'].iloc[0])
    monthly     = float(config['monthly_contribution'].iloc[0])
    years       = int(config['years_to_retirement'].iloc[0])
    stock_alloc = float(config['stock_allocation'].iloc[0])
except Exception as e:
    print(f"Error reading {config_file}: {e}")
    print("Using fallback/example values instead.")
    initial     = 50000
    age         = 35
    monthly     = 1000
    years       = 30
    stock_alloc = 0.60

annual_contrib = monthly * 12
end_age = age + years

# Portfolio expected returns (arithmetic for simplicity)
port_return_nom  = stock_alloc * stocks.mean() + (1 - stock_alloc) * bonds.mean()
port_return_real = (1 + port_return_nom) / (1 + infl.mean()) - 1

# Future value with annual contributions (end-of-year)
fv = initial
for _ in range(years):
    fv = fv * (1 + port_return_nom) + annual_contrib

fv_today_dollars = fv / (1 + infl.mean()) ** years

print("══════════════════════════════════════════════════════")
print(f"   YOUR SAVINGS PROJECTION (as of March 2026)   ")
print("══════════════════════════════════════════════════════")
print(f"  Current savings     : ${initial:,.0f}")
print(f"  Age now / at goal    : {age} → {end_age}")
print(f"  Monthly contribution : ${monthly:,.0f}  (→ ${annual_contrib:,.0f}/yr)")
print(f"  Years ahead          : {years}")
print(f"  Stock allocation     : {stock_alloc:.0%} / Bonds {1-stock_alloc:.0%}")
print()
print(f"  Expected nominal return : {port_return_nom:.1%} p.a.")
print(f"  Expected real return    : {port_return_real:.1%} p.a.")
print()
print(f"  Projected balance in {years} years:")
print(f"    • Nominal            ${fv:,.0f}")
print(f"    • In today's dollars ${fv_today_dollars:,.0f}")
print("══════════════════════════════════════════════════════")