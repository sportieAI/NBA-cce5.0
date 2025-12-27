import pandas as pd
import numpy as np
import os
from nba_api.stats.endpoints import leaguegamelog

# 1. SETUP
SCHEMA_DIR = "schema"
if not os.path.exists(SCHEMA_DIR):
    os.makedirs(SCHEMA_DIR)

print("🏗️  BUILDING WORKSHEET 02: GAMES MASTER...")
print("    > Connecting to NBA API for Real Game Logs...")

# 2. FETCH REAL DATA (The Meat)
# We pull the 2024-25 Season Logs
try:
    log = leaguegamelog.LeagueGameLog(season='2024-25', player_or_team_abbreviation='T')
    df_raw = log.get_data_frames()[0]
    print(f"    ✅ Fetched {len(df_raw)} raw game records.")
except Exception as e:
    print(f"    ⚠️ API Error: {e}. (Check internet connection).")
    exit()

# 3. PROCESS INTO MASTER SCHEMA
print("    > Processing Causal Metrics (NetRtg, eFG, Pace)...")

games_list = []
processed_ids = set()

# We pair up Home/Away rows to create single "Matchup" rows
for _, row in df_raw.iterrows():
    game_id = row['GAME_ID']
    if game_id in processed_ids:
        continue
    
    # Find the opponent row (the other side of the game)
    opp_row = df_raw[df_raw['GAME_ID'] == game_id].iloc[-1] 
    if len(df_raw[df_raw['GAME_ID'] == game_id]) < 2: continue # Skip incomplete data

    # Identify Home/Away
    # MATCHUP format is usually "BOS vs. NYK" (Home) or "BOS @ NYK" (Away)
    if "vs." in row['MATCHUP']:
        home = row
        away = opp_row
    else:
        home = opp_row
        away = row
    
    # --- CALCULATE REAL METRICS ---
    # 1. Possessions (Approx) = 0.5 * ((FGA + 0.4*FTA - 1.07*(ORB/(ORB+DRB))*(FGA-FG) + TOV) + (Opp...))
    # Simplified Pace Estimate for Speed: FGA + TOV
    pace_est = (home['FGA'] + home['TOV'] + away['FGA'] + away['TOV']) / 2.0
    
    # 2. Net Rating (Pts Diff / Pace * 100)
    net_h = (home['PLUS_MINUS'] / pace_est) * 100
    net_a = -net_h
    
    # 3. eFG% = (FGM + 0.5 * 3PM) / FGA
    efg_h = (home['FGM'] + 0.5 * home['FG3M']) / home['FGA'] if home['FGA'] > 0 else 0
    efg_a = (away['FGM'] + 0.5 * away['FG3M']) / away['FGA'] if away['FGA'] > 0 else 0
    
    # 4. Turnover %
    tov_h = home['TOV'] / pace_est
    tov_a = away['TOV'] / pace_est

    # --- BUILD THE ROW (EXACT COLUMNS) ---
    games_list.append({
        "game_id": game_id,
        "season": "2024-25",
        "date": home['GAME_DATE'],
        "home_team": home['TEAM_ABBREVIATION'],
        "away_team": away['TEAM_ABBREVIATION'],
        
        # FUNDAMENTALS
        "netrtg_home": round(net_h, 1),
        "netrtg_away": round(net_a, 1),
        "netrtg_delta": round(net_h - net_a, 1),
        "efg_home": round(efg_h, 3),
        "efg_away": round(efg_a, 3),
        "efg_gap": round(efg_h - efg_a, 3),
        "pace": round(pace_est, 1),
        "tov_pct_home": round(tov_h, 3),
        "tov_pct_away": round(tov_a, 3),
        "tov_pct_delta": round(tov_h - tov_a, 3),
        
        # SAVANT / ADVANCED (Placeholders for now, populated by '01' Feeds later)
        "v_pos_raw": 0.0,         # Needs PBP Source
        "decay_x_raw": 1.0,       # Needs PBP Source
        "chaos_integrity": 0.5,
        "deterrence_delta": 0.0,
        "elasticity": 0.0,
        "paint_wall_pct": 0.0,
        
        # EPM / INJURIES (Needs Rotowire Source)
        "epm_topA": 5.0, "epm_topB": 4.2,
        "epm_loss_A": 0.0, "epm_loss_B": 0.0,
        "injury_flag_A": "ACTIVE", "injury_flag_B": "ACTIVE",
        "minutes_restriction_A": None, "minutes_restriction_B": None,
        
        # CONTEXT
        "venue_type": "Home",
        "b2b_flag_A": 0, "b2b_flag_B": 0,
        "travel_miles_A": 0, "travel_miles_B": 500,
        "market_spread": -4.5,    # Mock Vegas Line
        "closing_line_move": 0.0,
        "win_prob_snapshot": 0.65,
        "leverage_index": 1.0,
        "garbage_time_pct": 0.0,
        
        # FLAGS
        "imputed_count": 5,       # Tracking that we imputed Savant data
        "low_confidence_flag": True
    })
    
    processed_ids.add(game_id)

# 4. SAVE
df_ws02 = pd.DataFrame(games_list)
outfile = f"{SCHEMA_DIR}/02_games_master.csv"
df_ws02.to_csv(outfile, index=False)

print(f"✅ WORKSHEET 02 CREATED: {outfile}")
print(f"    - Loaded {len(df_ws02)} unique matchups.")
print(f"    - Calculated NetRtg, eFG%, and Pace from Box Scores.")
print(f"    - Savant columns initialized (ready for feed).")
print("-" * 30)
print(df_ws02[["game_id", "home_team", "netrtg_delta", "efg_gap"]].head().to_string())
