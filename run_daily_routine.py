import pandas as pd
import datetime
from nba_api.live.nba.endpoints import scoreboard
import cce_core
import human_signals
import os

# CONFIGURATION
SCHEMA_DIR = "./schema"
TODAY = datetime.date.today()

print(f"🌅 STARTING DAILY ROUTINE: {TODAY}")

# --- PART 1: THE MORNING AUDIT (Yesterday's Games) ---
print("\n🕵️‍♂️ RUNNING MORNING AUDIT...")
# (In a full version, this fetches yesterday's scores via API)
# For now, we simulate the 'Wake Up' check
print("   > Checking for 'Regret' signals from yesterday...")
if os.path.exists(f"{SCHEMA_DIR}/15_cycle_signals.csv"):
    df_signals = pd.read_csv(f"{SCHEMA_DIR}/15_cycle_signals.csv")
    recent_regret = df_signals.tail(1)['volatility_gap'].values[0]
    print(f"   > System Morning Mood: {'⚠️ CAUTIOUS' if recent_regret > 5 else '✅ CONFIDENT'} (Last Gap: {recent_regret})")
else:
    print("   > No history found. Starting fresh.")

# --- PART 2: THE DAY'S PREDICTIONS (Today's Games) ---
print("\n🔮 GENERATING TODAY'S PREDICTIONS...")

# Mocking a game for today to test the loop
today_games = [
    {"game_id": "TODAY_GAME_1", "home_team": "GSW", "away_team": "PHX", "netrtg_home": 5.0, "netrtg_away": 6.2, "Home_B2B": False, "Actual_Margin": 0},
    {"game_id": "TODAY_GAME_2", "home_team": "NYK", "away_team": "CLE", "netrtg_home": 3.0, "netrtg_away": 1.5, "Home_B2B": True, "Actual_Margin": 0}
]

for game in today_games:
    # 1. Calculate Human Signal
    h_sig = human_signals.calculate_human_signal(game)
    
    # 2. Run CCE Prediction
    pred = cce_core.cce_v5_predict(game, human_signal=h_sig)
    
    # 3. ORA Check
    ora, reason = cce_core.run_ora_audit(pred, 0.9)
    
    print(f"   🏀 {game['home_team']} vs {game['away_team']}")
    print(f"      > Prediction: {game['home_team']} by {pred['DeltaW_Final']:.1f}")
    print(f"      > Human Factor: {h_sig:.1f} pts")
    print(f"      > Status: {'⛔ ORA WARNING' if ora else '✅ GREEN LIGHT'}")
    print("-" * 30)

print("\n✅ DAILY ROUTINE COMPLETE. ready for betting execution.")