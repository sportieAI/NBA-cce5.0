import os
import sys
import pandas as pd
import numpy as np

# --- 1. RE-BAKE THE BRAIN (cce_core.py) ---
cce_code = """
import numpy as np

# CONFIGURATION
ALPHA = 3.0
GAMMA = 0.05
TAU_ORA = 2.0

def calculate_pillars(row):
    z_net = row.get('NetRtg_Diff', 0) / 10.0
    z_efg = (row.get('eFG_Diff', 0) * 100) / 5.0
    physics = (0.4 * z_net) + (0.4 * z_efg)
    deterrence = row.get('DefRtg_Diff', 0) / 8.0
    v_pos = (row.get('Pace', 98) - 98) / 5.0
    decay = -0.5 if row.get('Is_B2B', False) else 0.0
    return physics, deterrence, v_pos, decay

def cce_v5_predict(row, human_signal=0.0):
    delta_w_fund = row.get('NetRtg_Diff', 0) * 0.5
    physics, deterrence, v_pos, decay = calculate_pillars(row)
    win_signal = (0.30 * physics) + (0.30 * deterrence) + (0.25 * v_pos) + (0.15 * decay)
    
    signal_points = ALPHA * win_signal
    delta_w_total = delta_w_fund + signal_points + human_signal
    
    volatility = delta_w_total - delta_w_fund
    omega_integrity = GAMMA * (volatility ** 2) * np.sign(volatility)
    
    delta_w_final = delta_w_total - omega_integrity
    
    return {
        "DeltaW_Fund": round(delta_w_fund, 2),
        "DeltaW_Final": round(delta_w_final, 2),
        "Integrity_Penalty": round(omega_integrity, 2),
        "Win_Signal": round(win_signal, 2)
    }

def run_ora_audit(prediction, confidence):
    ora_engaged = False
    ora_reason = "None"
    if abs(prediction['DeltaW_Final']) < TAU_ORA:
        ora_engaged = True
        ora_reason = "Margin within Noise Threshold"
    if confidence < 0.6:
        ora_engaged = True
        ora_reason = "Model Confidence Critical Failure"
    return ora_engaged, ora_reason
"""

with open("cce_core.py", "w") as f:
    f.write(cce_code)
print("✅ BRAIN REPAIRED: cce_core.py")

# --- 2. RE-BAKE THE NERVES (human_signals.py) ---
human_code = """
def get_coaching_iq(team_id):
    elite_coaches = ['MIA', 'GSW', 'SAS']
    if team_id in elite_coaches: return 1.5
    return 0.0

def calculate_human_signal(row):
    # Handle both case formats (Home_Team vs home_team)
    home = row.get('Home_Team', row.get('home_team'))
    away = row.get('Away_Team', row.get('away_team'))
    
    c_iq = get_coaching_iq(home) - get_coaching_iq(away)
    return c_iq
"""
with open("human_signals.py", "w") as f:
    f.write(human_code)
print("✅ NERVES REPAIRED: human_signals.py")

# --- 3. EXECUTE THE DAILY ROUTINE DIRECTLY ---
print("\n🔄 STARTING DAILY ROUTINE TEST...")

import cce_core
import human_signals

# Mock Data for Today (with calculated NetRtg_Diff)
today_games = [
    {"game_id": "G1", "home_team": "GSW", "away_team": "PHX", "netrtg_home": 5.0, "netrtg_away": 6.2},
    {"game_id": "G2", "home_team": "NYK", "away_team": "CLE", "netrtg_home": 3.0, "netrtg_away": 1.5}
]

for game in today_games:
    # Ensure Physics Data exists
    game['NetRtg_Diff'] = game['netrtg_home'] - game['netrtg_away']
    
    # 1. Human Signal
    h_sig = human_signals.calculate_human_signal(game)
    
    # 2. CCE Prediction
    pred = cce_core.cce_v5_predict(game, human_signal=h_sig)
    
    # 3. ORA Audit
    ora, reason = cce_core.run_ora_audit(pred, 0.9)
    
    print(f"🏀 {game['home_team']} vs {game['away_team']}")
    print(f"   > Prediction: {game['home_team']} by {pred['DeltaW_Final']:.2f}")
    print(f"   > Human Impact: {h_sig} pts")
    print(f"   > Status: {'⛔ ORA AUDIT' if ora else '✅ GREEN LIGHT'}")
    print("-" * 30)

print("🚀 SYSTEM FULLY OPERATIONAL.")
"""

5.  Tap **Commit changes** (Green Button).

---

### **Step 2: Pull & Execute (The Fix)**
Go back to your **Codespaces Terminal**.

1.  **Pull the Repair Kit:**
    ```bash
    git pull
    ```
2.  **Run the Repair:**
    ```bash
    python repair_and_run.py
    ```

**You should see:**
* `✅ BRAIN REPAIRED`
* `✅ NERVES REPAIRED`
* `🏀 GSW vs PHX ...`
* `🚀 SYSTEM FULLY OPERATIONAL`

Tell me when you see the rockets! 🚀
