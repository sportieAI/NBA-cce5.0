import pandas as pd
import numpy as np
import os

# 1. SETUP
SCHEMA_DIR = "schema"
FILE_PATH = f"{SCHEMA_DIR}/02_games_master.csv"
print(f"🔧 REPAIRING SCHEMA FOR: {FILE_PATH}")

# 2. LOAD EXISTING FILE
if not os.path.exists(FILE_PATH):
    print("❌ Error: File not found. Creating empty shell.")
    df = pd.DataFrame()
else:
    df = pd.read_csv(FILE_PATH)
    print(f"   > Loaded {len(df)} games.")

# 3. DEFINE THE MASTER BLUEPRINT (Exact 40 Columns)
# (Copied strictly from your requirements)
master_columns = {
    "game_id": "text", "season": "int", "date": "date", 
    "home_team": "text", "away_team": "text",
    "netrtg_home": 0.0, "netrtg_away": 0.0, "netrtg_delta": 0.0,
    "efg_home": 0.50, "efg_away": 0.50, "efg_gap": 0.0,
    "pace": 98.0,
    "tov_pct_home": 0.13, "tov_pct_away": 0.13, "tov_pct_delta": 0.0,
    "v_pos_raw": 0.0, "decay_x_raw": 1.0,
    "chaos_integrity": 0.5, "deterrence_delta": 0.0, 
    "elasticity": 0.0, "paint_wall_pct": 0.0,
    "epm_topA": 0.0, "epm_topB": 0.0, "epm_loss_A": 0.0, "epm_loss_B": 0.0,
    "injury_flag_A": "ACTIVE", "injury_flag_B": "ACTIVE",
    "minutes_restriction_A": 0, "minutes_restriction_B": 0,
    "venue_type": "Home",
    "b2b_flag_A": 0, "b2b_flag_B": 0,
    "travel_miles_A": 0, "travel_miles_B": 0,
    "market_spread": 0.0, "closing_line_move": 0.0,
    "win_prob_snapshot": 0.50, "leverage_index": 1.0, "garbage_time_pct": 0.0,
    "imputed_count": 1, "low_confidence_flag": True
}

# 4. ENFORCE SCHEMA (Add missing columns with defaults)
for col, default_val in master_columns.items():
    if col not in df.columns:
        print(f"   + Adding missing column: {col}")
        df[col] = default_val

# 5. RE-ORDER COLUMNS (To match blueprint order)
df = df[list(master_columns.keys())]

# 6. SAVE UPDATED FILE
df.to_csv(FILE_PATH, index=False)
print("✅ REPAIR COMPLETE. All 40 Columns are now present.")
print("-" * 30)
print(df[["game_id", "netrtg_delta", "tov_pct_delta", "epm_topA"]].head().to_string())
