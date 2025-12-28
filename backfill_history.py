import pandas as pd
import os
import time
from nba_api.stats.endpoints import leaguegamelog

# 1. CONFIGURATION
SCHEMA_DIR = "schema"
FILE_PATH = f"{SCHEMA_DIR}/02_games_master.csv"
START_YEAR = 2010
END_YEAR = 2024 # The "start" year of the current season

print(f"📦 INITIATING DEEP ARCHIVE RETRIEVAL ({START_YEAR}-{END_YEAR + 1})...")

# 2. GENERATE SEASON LIST (e.g., "2010-11", "2011-12"...)
seasons = []
for y in range(START_YEAR, END_YEAR + 1):
    next_y = str(y + 1)[-2:]
    seasons.append(f"{y}-{next_y}")

print(f"   > Target Seasons: {seasons}")

# 3. LOAD EXISTING DATABASE (To prevent duplicates)
if os.path.exists(FILE_PATH):
    try:
        df_existing = pd.read_csv(FILE_PATH)
        existing_ids = set(df_existing['game_id'].astype(str))
        print(f"   > Loaded {len(df_existing)} existing games to preserve.")
    except:
        df_existing = pd.DataFrame()
        existing_ids = set()
else:
    df_existing = pd.DataFrame()
    existing_ids = set()

# 4. ITERATE AND FETCH
all_new_games = []
processed_ids = set()

for season in seasons:
    print(f"   > Fetching Season {season}...")
    try:
        # Fetch Data
        log = leaguegamelog.LeagueGameLog(season=season, player_or_team_abbreviation='T')
        df_raw = log.get_data_frames()[0]
        
        # Process Games
        for _, row in df_raw.iterrows():
            gid = str(row['GAME_ID'])
            
            # Skip if we already have it (in file or current batch)
            if gid in existing_ids or gid in processed_ids: 
                continue
            
            # Matchup Check (Need pairs)
            opp_rows = df_raw[df_raw['GAME_ID'] == row['GAME_ID']]
            if len(opp_rows) < 2: continue
            
            # Identify Home/Away
            home = row if "vs." in row['MATCHUP'] else opp_rows.iloc[-1]
            away = opp_rows.iloc[-1] if "vs." in row['MATCHUP'] else row
            
            # Calculate Fundamentals
            pace = (home['FGA'] + home['TOV'] + away['FGA'] + away['TOV']) / 2.0
            net_h = (home['PLUS_MINUS'] / pace) * 100 if pace > 0 else 0.0
            
            # Strict 40-Column Schema
            all_new_games.append({
                "game_id": gid,
                "season": season,
                "date": str(home['GAME_DATE']),
                "home_team": home['TEAM_ABBREVIATION'],
                "away_team": away['TEAM_ABBREVIATION'],
                "netrtg_home": round(net_h, 1),
                "netrtg_away": round(-net_h, 1),
                "netrtg_delta": round(net_h * 2, 1),
                "efg_home": round((home['FGM'] + 0.5*home['FG3M'])/home['FGA'], 3) if home['FGA'] else 0,
                "efg_away": round((away['FGM'] + 0.5*away['FG3M'])/away['FGA'], 3) if away['FGA'] else 0,
                "efg_gap": 0.0, 
                "pace": round(pace, 1),
                "tov_pct_home": round(home['TOV']/pace, 3) if pace else 0,
                "tov_pct_away": round(away['TOV']/pace, 3) if pace else 0,
                "tov_pct_delta": 0.0,
                "v_pos_raw": 0.0, "decay_x_raw": 1.0, "chaos_integrity": 0.5,
                "deterrence_delta": 0.0, "elasticity": 0.0, "paint_wall_pct": 0.0,
                "epm_topA": 0.0, "epm_topB": 0.0, "epm_loss_A": 0.0, "epm_loss_B": 0.0,
                "injury_flag_A": "ACTIVE", "injury_flag_B": "ACTIVE",
                "minutes_restriction_A": 0, "minutes_restriction_B": 0,
                "venue_type": "Home", "b2b_flag_A": 0, "b2b_flag_B": 0,
                "travel_miles_A": 0, "travel_miles_B": 0,
                "market_spread": 0.0, "closing_line_move": 0.0,
                "win_prob_snapshot": 0.50, "leverage_index": 1.0, "garbage_time_pct": 0.0,
                "imputed_count": 1, "low_confidence_flag": True
            })
            processed_ids.add(gid)
            
        time.sleep(0.600) # Respect API rate limits (avoid ban)
        
    except Exception as e:
        print(f"   ⚠️ Error fetching {season}: {e}")

# 5. SAVE AND MERGE
if all_new_games:
    df_history = pd.DataFrame(all_new_games)
    
    # Merge and Sort
    df_final = pd.concat([df_existing, df_history], ignore_index=True)
    df_final['date'] = pd.to_datetime(df_final['date'])
    df_final = df_final.sort_values(by='date')
    
    # Save
    df_final.to_csv(FILE_PATH, index=False)
    print("-" * 40)
    print(f"✅ ARCHIVE COMPLETE.")
    print(f"   Added: {len(df_history)} games")
    print(f"   Total Database: {len(df_final)} games")
    print("-" * 40)
else:
    print("⚠️ No new games found.")
