import pandas as pd
import os
import time
from requests.exceptions import RequestException
from nba_api.stats.endpoints import leaguegamelog

# 1. CONFIGURATION
SCHEMA_DIR = "schema"
FILE_PATH = f"{SCHEMA_DIR}/02_games_master.csv"
START_YEAR = 2010
END_YEAR = 2024 # Current season start

print(f"🛡️ STARTING BULLETPROOF ARCHIVE ({START_YEAR}-{END_YEAR})...")

# 2. DEFINE HELPER: GET EMPTY ROW (Strict 40 Columns)
def get_clean_row(row, home, away, net_h, pace, seas):
    return {
        "game_id": str(row['GAME_ID']),
        "season": seas,
        "date": str(home['GAME_DATE']),
        "home_team": home['TEAM_ABBREVIATION'],
        "away_team": away['TEAM_ABBREVIATION'],
        "netrtg_home": round(net_h, 1),
        "netrtg_away": round(-net_h, 1),
        "netrtg_delta": round(net_h * 2, 1),
        "efg_home": 0.50, "efg_away": 0.50, "efg_gap": 0.0,
        "pace": round(pace, 1),
        "tov_pct_home": 0.13, "tov_pct_away": 0.13, "tov_pct_delta": 0.0,
        "v_pos_raw": 0.0, "decay_x_raw": 1.0, "chaos_integrity": 0.5,
        "deterrence_delta": 0.0, "elasticity": 0.0, "paint_wall_pct": 0.0,
        "epm_topA": 0.0, "epm_topB": 0.0, "epm_loss_A": 0.0, "epm_loss_B": 0.0,
        "injury_flag_A": "ACTIVE", "injury_flag_B": "ACTIVE",
        "minutes_restriction_A": 0, "minutes_restriction_B": 0,
        "venue_type": "Home", "b2b_flag_A": 0, "b2b_flag_B": 0,
        "travel_miles_A": 0, "travel_miles_B": 0,
        "market_spread": 0.0, "closing_line_move": 0.0,
        "win_prob_snapshot": 0.50, "leverage_index": 1.0, 
        "garbage_time_pct": 0.0, "imputed_count": 1, "low_confidence_flag": True
    }

# 3. LOAD EXISTING IDS (To Skip what we already have)
if os.path.exists(FILE_PATH):
    df_master = pd.read_csv(FILE_PATH)
    existing_ids = set(df_master['game_id'].astype(str))
    print(f"   > Found {len(existing_ids)} games already saved.")
else:
    df_master = pd.DataFrame()
    existing_ids = set()

# 4. ROBUST LOOP (One Season at a Time)
for year in range(START_YEAR, END_YEAR + 1):
    season_str = f"{year}-{str(year+1)[-2:]}"
    print(f"\n📅 CHECKING SEASON: {season_str}")
    
    # RETRY LOGIC (Try 3 times before giving up on a season)
    success = False
    attempts = 0
    while not success and attempts < 3:
        try:
            # Fetch
            log = leaguegamelog.LeagueGameLog(season=season_str, player_or_team_abbreviation='T', timeout=30)
            df_raw = log.get_data_frames()[0]
            success = True
            
        except Exception as e:
            attempts += 1
            print(f"   ⚠️ Connection Error (Attempt {attempts}/3): {e}")
            print("   ⏳ Waiting 15 seconds to cool down...")
            time.sleep(15)

    if not success:
        print(f"   ❌ FAILED to fetch {season_str}. Skipping to next year.")
        continue

    # PROCESS THE DATA
    new_games = []
    processed_in_batch = set()
    
    for _, row in df_raw.iterrows():
        gid = str(row['GAME_ID'])
        
        # SKIP DUPLICATES
        if gid in existing_ids or gid in processed_in_batch: 
            continue
        
        # Matchup Logic
        opp_rows = df_raw[df_raw['GAME_ID'] == row['GAME_ID']]
        if len(opp_rows) < 2: continue
        
        home = row if "vs." in row['MATCHUP'] else opp_rows.iloc[-1]
        away = opp_rows.iloc[-1] if "vs." in row['MATCHUP'] else row
        
        pace = (home['FGA'] + home['TOV'] + away['FGA'] + away['TOV']) / 2.0
        net_h = (home['PLUS_MINUS'] / pace) * 100 if pace > 0 else 0.0
        
        # Build Row
        clean_row = get_clean_row(row, home, away, net_h, pace, season_str)
        new_games.append(clean_row)
        processed_in_batch.add(gid)
        existing_ids.add(gid) # Add to memory so we don't re-add in future loops

    # SAVE IMMEDIATELY (Checkpoint)
    if new_games:
        print(f"   > Found {len(new_games)} new games. SAVING...")
        
        df_new = pd.DataFrame(new_games)
        
        # Reload Master (in case file changed) and Append
        if os.path.exists(FILE_PATH):
            df_current = pd.read_csv(FILE_PATH)
            df_final = pd.concat([df_current, df_new], ignore_index=True)
        else:
            df_final = df_new
        
        # Sort and Write
        df_final['date'] = pd.to_datetime(df_final['date'])
        df_final = df_final.sort_values(by='date')
        df_final.to_csv(FILE_PATH, index=False)
        print(f"   ✅ SAVED. Total Database Size: {len(df_final)}")
    else:
        print(f"   > Season {season_str} is already fully archived.")
        
    print("   💤 Resting 3s...")
    time.sleep(3)

print("\n🏆 ARCHIVE JOB FINISHED.")
