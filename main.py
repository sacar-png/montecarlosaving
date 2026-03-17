import pandas as pd
import numpy as np

# ────────────────────────────────────────────────
# 1. LOAD HISTORICAL DATA FROM KAGGLE CSVs
# ────────────────────────────────────────────────

# A. Inflation (annual rates 1929+)
try:
    df_infl = pd.read_csv("inflation_1929_2024.csv")  # adjust filename if needed
    # Assume columns are something like: 'Year', 'Inflation Rate' or similar
    # Clean/rename — adjust column names based on your downloaded file
    df_infl = df_infl.rename(columns=lambda x: x.strip().lower().replace(' ', '_').replace('%', ''))
    df_infl = df_infl[['year', 'inflation_rate']]  # adapt if columns differ (e.g. 'december_inflation')
    df_infl['inflation_rate'] = df_infl['inflation_rate'] / 100  # convert % to decimal
    df_infl = df_infl.sort_values('year')
except Exception as e:
    print(f"Error loading inflation CSV: {e}")
    print("Using fallback average inflation 3.1%")
    infl_mean = 0.031
else:
    infl_mean = df_infl['inflation_rate'].mean()
    print(f"Loaded inflation data: {len(df_infl)} years, mean = {infl_mean:.1%}")

# B. S&P 500 — compute annual returns from daily data
try:
    df_sp = pd.read_csv("SPX.csv")  # adjust filename if needed
    df_sp['Date'] = pd.to_datetime(df_sp['Date'])
    # Use Adjusted Close for total returns (includes dividends)
    df_year = df_sp.groupby(df_sp['Date'].dt.year)['Adj Close'].last().reset_index()
    df_year = df_year.rename(columns={'Date': 'year', 'Adj Close': 'close'})
    df_year['S&P 500'] = df_year['close'].pct_change()          # annual return
    df_year = df_year.dropna(subset=['S&P 500'])
    stocks_mean = df_year['S&P 500'].mean()
    print(f"Loaded S&P 500 data: {len(df_year)} annual returns, arithmetic mean = {stocks_mean:.1%}")
except Exception as e:
    print(f"Error loading S&P 500 CSV: {e}")
    print("Using fallback S&P 500 mean 11.8%")
    stocks_mean = 0.118

# C. Bonds — no good long Kaggle series → use long-term historical average
bonds_mean = 0.051   # ≈ Damodaran/Ibbotson long-term 10yr T.Bond total return
print(f"Using fallback 10yr T.Bond mean return: {bonds_mean:.1%}")

real_stocks_mean = (1 + stocks_mean) / (1 + infl_mean) - 1
real_bonds_mean  = (1 + bonds_mean)  / (1 + infl_mean) - 1
print(f"Approximate real returns → Stocks: {real_stocks_mean:.1%}   Bonds: {real_bonds_mean:.1%}\n")

# ────────────────────────────────────────────────
# 2. READ YOUR PERSONAL SAVINGS CONFIG FROM CSV (1st approach)
# ────────────────────────────────────────────────
config_file = "savings.csv"

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

# Portfolio expected return (arithmetic, simple weighted average)
port_return_nom  = stock_alloc * stocks_mean + (1 - stock_alloc) * bonds_mean
port_return_real = (1 + port_return_nom) / (1 + infl_mean) - 1

# Future value calculation — compound initial + annual contributions (end-of-year)
fv = initial
for _ in range(years):
    fv = fv * (1 + port_return_nom) + annual_contrib

fv_today_dollars = fv / (1 + infl_mean) ** years

# ────────────────────────────────────────────────
# 3. OUTPUT YOUR PROJECTION
# ────────────────────────────────────────────────
print("═══════════════════════════════════════════════════════════════")
print(f"   YOUR SAVINGS PROJECTION   (as of March 2026)              ")
print("═══════════════════════════════════════════════════════════════")
print(f"  Current savings        : ${initial:,.0f}")
print(f"  Age now / at retirement : {age} → {end_age}")
print(f"  Monthly contribution    : ${monthly:,.0f}  (${annual_contrib:,.0f}/year)")
print(f"  Years ahead             : {years}")
print(f"  Portfolio mix           : Stocks {stock_alloc:.0%} / Bonds {1-stock_alloc:.0%}")
print()
print(f"  Expected annual returns:")
print(f"    Nominal portfolio     : {port_return_nom:.1%}")
print(f"    Real (after inflation): {port_return_real:.1%}")
print()
print(f"  Projected balance after {years} years:")
print(f"    • Nominal (future $)     ${fv:,.0f}")
print(f"    • In today's purchasing power ${fv_today_dollars:,.0f}")
print("═══════════════════════════════════════════════════════════════")

# Optional: quick sensitivity
print("\nQuick sensitivity (real terms, today's $):")
for sa in [0.40, 0.60, 0.80]:
    pr_nom = sa * stocks_mean + (1-sa) * bonds_mean
    pr_real = (1 + pr_nom) / (1 + infl_mean) - 1
    fv_sens = initial
    for _ in range(years):
        fv_sens = fv_sens * (1 + pr_nom) + annual_contrib
    fv_sens_real = fv_sens / (1 + infl_mean)**years
    print(f"  {sa:.0%} stocks → ${fv_sens_real:,.0f}")