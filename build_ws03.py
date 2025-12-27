import pandas as pd
import numpy as np
import os

# 1. CONFIGURATION
SCHEMA_DIR = "schema"
INPUT_FILE = f"{SCHEMA_DIR}/02_games_master.csv"
OUTPUT_FILE = f"{SCHEMA_DIR}/03_pillars_context.csv"

print("🏗️  BUILDING WORKSHEET 03: PILLARS CONTEXT...")

# 2. LOAD SOURCE DATA (Worksheet 02)
if not os.path.exists(INPUT_FILE):
    print(f"❌ Error: {INPUT_FILE} missing. Run build_ws02.py first.")
    exit()

df_games = pd.read_csv(INPUT_FILE)
print(f"    > Loaded {len(df_games)} games from Master.")

# 3. RESHAPE DATA (Game-Centric -> Team-Centric)
# We need a single timeline per team to calculate rolling stats.
team_logs = []

for _, row in df_games.iterrows():
    # Home Team Perspective
    team_logs.append({
        "team": row['home_team'],
        "date": row['date'],
        "netrtg": row['netrtg_home'],
        "efg": row['efg_home'],
        "v_pos": row['v_pos_raw'],
        "decay": row['decay_x_raw']
    })
    # Away Team Perspective
    team_logs.append({
        "team": row['away_team'],
        "date": row['date'],
        "netrtg": row['netrtg_away'],
        "efg": row['efg_away'],
        "v_pos": row['v_pos_raw'], 
        "decay": row['decay_x_raw']
    })

df_teams = pd.DataFrame(team_logs).sort_values(by=['team', 'date'])

# 4. COMPUTE ROLLING METRICS (The Normalization Baseline)
context_rows = []

for team_id, group in df_teams.groupby('team'):
    # Rule: Use 90-game rolling window 
    # Rule: If sample < 30, we still calculate (min_periods=1) but track the count 
    roll = group.rolling(window=90, min_periods=1)
    
    # Standard Z-Score Inputs (Mean & Std)
    means_net = roll['netrtg'].mean()
    stds_net = roll['netrtg'].std()
    
    means_efg = roll['efg'].mean()
    stds_efg = roll['efg'].std()
    
    # Robust Scaling Inputs (Median & IQR) 
    median_v = roll['v_pos'].median()
    
    q1_decay = roll['decay'].quantile(0.25)
    q3_decay = roll['decay'].quantile(0.75)
    iqr_decay = q3_decay - q1_decay
    
    # Rolling Count (for Confidence Logic)
    counts = roll['netrtg'].count()
    
    for i in group.index:
        # Fallback Logic: If std is NaN (first game), give it a safe default to prevent div/0 later
        safe_std_net = 5.0 if pd.isna(stds_net[i]) else stds_net[i]
        safe_std_efg = 0.05 if pd.isna(stds_efg[i]) else stds_efg[i]
        safe_iqr = 0.1 if pd.isna(iqr_decay[i]) or iqr_decay[i] == 0 else iqr_decay[i]

        context_rows.append({
            "team": team_id,
            "date": group.loc[i, 'date'],
            
            # The Normalization Anchors
            "rolling_90_netrtg_mean": round(means_net[i], 2),
            "rolling_90_netrtg_std": round(safe_std_net, 2),
            "rolling_90_efg_mean": round(means_efg[i], 3),
            "rolling_90_efg_std": round(safe_std_efg, 3),
            
            # The Robust Anchors
            "rolling_90_vpos_median": round(median_v[i], 2),
            "rolling_90_decay_iqr": round(safe_iqr, 3),
            
            # The Confidence Switch
            "last_30_games_count": int(counts[i])
        })

# 5. SAVE WORKSHEET 03
df_ws03 = pd.DataFrame(context_rows)
df_ws03 = df_ws03[[
    "team", "date", 
    "rolling_90_netrtg_mean", "rolling_90_netrtg_std", 
    "rolling_90_efg_mean", "rolling_90_efg_std", 
    "rolling_90_vpos_median", "rolling_90_decay_iqr", 
    "last_30_games_count"
]]

df_ws03.to_csv(OUTPUT_FILE, index=False)

print(f"✅ WORKSHEET 03 CREATED: {OUTPUT_FILE}")
print(f"    - Calculated Rolling Means & Stds (NetRtg, eFG).")
print(f"    - Calculated Robust Metrics (Median, IQR) for V_Pos/Decay.")
print(df_ws03.tail(3).to_string())
