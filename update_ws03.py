import pandas as pd
import os

# Define the columns for the Pillars Context
cols_03 = [
    "team", "date", 
    "rolling_90_netrtg_mean", "rolling_90_netrtg_std",
    "rolling_90_efg_mean", "rolling_90_efg_std",
    "rolling_90_vpos_median", "rolling_90_decay_iqr",
    "last_30_games_count"
]

# Injecting the Logic row (Gama Formulas + Sources)
# Formula source: robust_z = (x - median) / (IQR / 1.349)
logic_row_03 = {
    "team": "SOURCE: Games Master (WS02)",
    "date": "KEY: ISO Date",
    "rolling_90_netrtg_mean": "ALGO: rolling(90).mean() ",
    "rolling_90_netrtg_std": "ALGO: rolling(90).std() ",
    "rolling_90_efg_mean": "ALGO: rolling(90).mean() ",
    "rolling_90_efg_std": "ALGO: rolling(90).std() ",
    "rolling_90_vpos_median": "ALGO: rolling(90).median() ",
    "rolling_90_decay_iqr": "ALGO: rolling(90).quantile(0.75)-0.25 ",
    "last_30_games_count": "ALGO: count(non-null) in window "
}

# Write to root CSV
df_03 = pd.DataFrame(columns=cols_03)
df_03 = pd.concat([df_03, pd.DataFrame([logic_row_03])], ignore_index=True)
df_03.to_csv('03_pillars_context.csv', index=False)

print("---")
print("✅ SUCCESS: Worksheet 03 (Pillars Context) created in root.")
print("Logic: Normalization and Rolling Window formulas injected.")
print("---")
