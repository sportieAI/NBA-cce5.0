import pandas as pd

# Define the specific Gama logic for the Pillars Context
logic_row_03 = {
    "team": "SOURCE: WS02 Games Master",
    "date": "KEY: ISO Date",
    "rolling_90_netrtg_mean": "ALGO: rolling(90).mean()",
    "rolling_90_netrtg_std": "ALGO: rolling(90).std()",
    "rolling_90_efg_mean": "ALGO: rolling(90).mean()",
    "rolling_90_efg_std": "ALGO: rolling(90).std()",
    "rolling_90_vpos_median": "ALGO: rolling(90).median()",
    "rolling_90_decay_iqr": "ALGO: rolling(90).quantile(0.75)-0.25",
    "last_30_games_count": "ALGO: count(non-null) in window"
}

try:
    df = pd.read_csv('03_pillars_context.csv')
    new_row = pd.DataFrame([logic_row_03], columns=df.columns)
    # Force the logic row to the top
    df_final = pd.concat([new_row, df], ignore_index=True).drop_duplicates().head(1)
    df_final.to_csv('03_pillars_context.csv', index=False)
    print("---")
    print("✅ SUCCESS: Worksheet 03 (Pillars Context) logic is now baked in.")
    print("---")
except Exception as e:
    print(f"❌ Error updating WS03: {e}")
