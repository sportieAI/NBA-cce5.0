import pandas as pd
import numpy as np
import os
from nba_api.stats.endpoints import leaguegamelog

SCHEMA_DIR = "schema"
if not os.path.exists(SCHEMA_DIR):
    os.makedirs(SCHEMA_DIR)

print("🏗️  BUILDING FOUNDATION (Worksheets 00-04)...")

# --- SHEET 00: AGENT CONFIG ---
print("   > Writing Sheet 00 (Identity)...")
ws00 = [
    {"param": "ALPHA", "value": 3.0, "role": "Signal Scalar"},
    {"param": "GAMMA", "value": 0.05, "role": "Integrity Constraint"},
    {"param": "TAU_ORA", "value": 2.0, "role": "Override Threshold"},
    {"param": "VERSION", "value": "CCE_V5.0", "role": "System Version"}
]
pd.DataFrame(ws00).to_csv(f"{SCHEMA_DIR}/00_agent_config.csv", index=False)

# --- SHEET 01: DATA INVENTORY ---
print("   > Writing Sheet 01 (Sources)...")
ws01 = [
    {"source": "NBA_API_Live", "endpoint": "scoreboard.ScoreBoard", "status": "Active"},
    {"source": "NBA_API_Stats", "endpoint": "stats.leaguegamelog", "status": "Active"}
]
pd.DataFrame(ws01).to_csv(f"{SCHEMA_DIR}/01_data_inventory.csv", index=False)

# --- SHEET 02: GAMES MASTER (THE SOURCE) ---
print("   > Writing Sheet 02 (Fetching Real NBA Data)...")
try:
    # Fetch real 2024-25 Data
    log = leaguegamelog.LeagueGameLog(season='2024-25', player_or_team_abbreviation='T')
    df_raw = log.get_data_frames()[0]
    
    # Transform raw API data into our Schema
    # We create a simplified view for the 'Games Master'
    games_data = []
    processed_ids = set()
    
    for _, row in df_raw.head(100).iterrows():
        gid = row['GAME_ID']
        if gid in processed_ids: continue
        
        # Logic to parse Home/Away from "LAL vs BOS" or "LAL @ BOS"
        matchup = row['MATCHUP']
        is_home = "vs." in matchup
        team = row['TEAM_ABBREVIATION']
        opp = matchup.split(' ')[-1]
        
        # Simulated NetRtg based on actual Plus/Minus for this build
        # (In full prod, this comes from a dedicated stats endpoint)
        net_rtg = row['PLUS_MINUS'] / 2.0 
        
        games_data.append({
            "game_id": gid,
            "date": row['GAME_DATE'],
            "home_team": team if is_home else opp,
            "away_team": opp if is_home else team,
            "netrtg_home": net_rtg if is_home else -net_rtg,
            "netrtg_away": -net_rtg if is_home else net_rtg,
            "is_b2b": False # Placeholder for complex date math
        })
        processed_ids.add(gid)
        
    df_ws02 = pd.DataFrame(games_data)
    df_ws02.to_csv(f"{SCHEMA_DIR}/02_games_master.csv", index=False)
    print(f"     ✅ Fetched {len(df_ws02)} unique games.")

except Exception as e:
    print(f"     ⚠️ API Error: {e}. Generating Emergency Mock Data.")
    # Fallback to Mock if API fails
    df_ws02 = pd.DataFrame([
        {"game_id": "MOCK_001", "home_team": "BOS", "netrtg_home": 5.5, "netrtg_away": 2.1},
        {"game_id": "MOCK_002", "home_team": "LAL", "netrtg_home": -1.2, "netrtg_away": 0.5}
    ])
    df_ws02.to_csv(f"{SCHEMA_DIR}/02_games_master.csv", index=False)

# --- SHEET 03: PILLARS CONTEXT (CALCULATED) ---
print("   > Writing Sheet 03 (Calculating Pillars)...")
pillars_data = []
for _, row in df_ws02.iterrows():
    # MATH: Normalize NetRtg (Z-Score approximation)
    phys_score = (row['netrtg_home'] - row['netrtg_away']) / 10.0
    
    # MATH: Fatigue Decay
    decay = -0.5 if row.get('is_b2b') else 0.0
    
    pillars_data.append({
        "game_id": row['game_id'],
        "physics_score": round(phys_score, 2),
        "deterrence_score": 0.0, # Placeholder
        "decay_x": decay
    })
pd.DataFrame(pillars_data).to_csv(f"{SCHEMA_DIR}/03_pillars_context.csv", index=False)

# --- SHEET 04: CCE CORE (THE BRAIN) ---
print("   > Writing Sheet 04 (Running CCE V5.0 Math)...")
cce_data = []
ALPHA = 3.0

for i, row in df_ws02.iterrows():
    pillars = pillars_data[i]
    
    # MATH LINE 1: Fundamental Anchor
    delta_w_fund = (row['netrtg_home'] - row['netrtg_away']) * 0.5
    
    # MATH LINE 2: Win Signal
    # 30% Physics + 15% Decay
    win_signal = (0.3 * pillars['physics_score']) + (0.15 * pillars['decay_x'])
    
    # MATH LINE 3: Raw Prediction
    raw_pred = delta_w_fund + (ALPHA * win_signal)
    
    cce_data.append({
        "game_id": row['game_id'],
        "delta_w_fund": round(delta_w_fund, 2),
        "win_signal": round(win_signal, 2),
        "raw_prediction": round(raw_pred, 2)
    })
pd.DataFrame(cce_data).to_csv(f"{SCHEMA_DIR}/04_cce_core.csv", index=False)

print("\n✅ BATCH 1 COMPLETE: Worksheets 00, 01, 02, 03, 04 are LIVE.")
