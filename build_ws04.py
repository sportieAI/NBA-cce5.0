import pandas as pd
import numpy as np
import os

# 1. SETUP
SCHEMA_DIR = "schema"
print("🧠 IGNITING WORKSHEET 04: CCE CORE...")

# Load Inputs
df_games = pd.read_csv(f"{SCHEMA_DIR}/02_games_master.csv")
df_context = pd.read_csv(f"{SCHEMA_DIR}/03_pillars_context.csv")

# 2. DEFINE THE MATH (Z-Score & Helpers)
def get_z_score(val, mean, std):
    if pd.isna(std) or std == 0: return 0.0
    z = (val - mean) / std
    return max(min(z, 3.0), -3.0)

def get_robust_z(val, median, iqr):
    if pd.isna(iqr) or iqr == 0: return 0.0
    sigma_est = iqr / 1.349
    z = (val - median) / sigma_est
    return max(min(z, 3.0), -3.0)

# 3. PROCESS EVERY GAME
cce_rows = []
ALPHA = 3.0

for _, game in df_games.iterrows():
    gid = game['game_id']
    date = str(game['date'])
    
    # Context Lookup
    ctx_h = df_context[(df_context['team'] == game['home_team']) & (df_context['date'] == date)]
    ctx_a = df_context[(df_context['team'] == game['away_team']) & (df_context['date'] == date)]
    
    # Fallback
    if ctx_h.empty: ctx_h = df_context[df_context['team'] == game['home_team']].tail(1)
    if ctx_a.empty: ctx_a = df_context[df_context['team'] == game['away_team']].tail(1)
    
    if ctx_h.empty or ctx_a.empty: continue
        
    ctx_h = ctx_h.iloc[0]
    ctx_a = ctx_a.iloc[0]

    # PILLARS MATH (HEVS-81)
    delta_w_fund = game['netrtg_home'] - game['netrtg_away']
    
    # Physics
    pool_std_net = (ctx_h['rolling_90_netrtg_std'] + ctx_a['rolling_90_netrtg_std']) / 2
    z_net = get_z_score(game['netrtg_delta'], 0, pool_std_net)
    physics = (0.6 * z_net) # Simplified for test

    # Win Signal
    win_signal = (0.30 * physics) # Placeholder for full sum
    signal_points = ALPHA * win_signal

    cce_rows.append({
        "game_id": gid,
        "DeltaW_Fund": round(delta_w_fund, 2),
        "physics": round(physics, 3),
        "deterrence": 0.0,
        "v_pos": 0.0,
        "decay_x_z": 0.0,
        "win_signal": round(win_signal, 3),
        "win_signal_adj": round(win_signal, 3),
        "signal_points": round(signal_points, 3),
        "alpha_used": ALPHA
    })

# 4. EXPORT
df_cce = pd.DataFrame(cce_rows)
outfile = f"{SCHEMA_DIR}/04_cce_core.csv"
df_cce.to_csv(outfile, index=False)

print(f"✅ WORKSHEET 04 CREATED: {outfile}")
print(df_cce.head().to_string())
