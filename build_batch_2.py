import pandas as pd
import numpy as np
import os

SCHEMA_DIR = "schema"

print("🏗️  BUILDING EXECUTIVE LAYERS (Worksheets 05-10)...")

# Load Foundation
try:
    df_games = pd.read_csv(f"{SCHEMA_DIR}/02_games_master.csv")
    df_cce = pd.read_csv(f"{SCHEMA_DIR}/04_cce_core.csv")
except FileNotFoundError:
    print("❌ Critical Error: Batch 1 (Foundation) missing. Run Batch 1 first.")
    exit()

# --- SHEET 05: OMEGAS (VOLATILITY ENGINE) ---
print("   > Writing Sheet 05 (Volatility Engine)...")
omegas_data = []
for i, row in df_games.iterrows():
    # MATH: Home Court Advantage (Simple placeholder)
    w_venue = 1.0 if row['home_team'] in ['DEN', 'UTA'] else 0.5
    
    # MATH: Star Gravity (Mocking a star player impact)
    w_gravity = 0.0 # Would come from EPM feed
    
    total_vol = w_venue + w_gravity
    
    omegas_data.append({
        "game_id": row['game_id'],
        "w_gravity": w_gravity,
        "w_venue": w_venue,
        "w_fatigue": 0.0, # Handled in Pillars for now
        "total_volatility": total_vol
    })
df_ws05 = pd.DataFrame(omegas_data)
df_ws05.to_csv(f"{SCHEMA_DIR}/05_omegas.csv", index=False)

# --- SHEET 06: INTEGRITY & ORA (THE LAW) ---
print("   > Writing Sheet 06 (Applying Integrity Constraints)...")
integrity_data = []
GAMMA = 0.05
TAU_ORA = 2.0

for i, row in df_cce.iterrows():
    vol_row = df_ws05.iloc[i]
    
    # 1. Total Prediction (Brain + Volatility)
    delta_w_total = row['raw_prediction'] + vol_row['total_volatility']
    
    # 2. Integrity Constraint
    # Measures how far we drifted from the Fundamental Anchor
    drift = delta_w_total - row['delta_w_fund']
    integrity_penalty = GAMMA * (drift ** 2) * np.sign(drift)
    
    # 3. Final Prediction
    delta_w_final = delta_w_total - integrity_penalty
    
    # 4. ORA Trigger
    ora_engaged = abs(delta_w_final) < TAU_ORA
    
    integrity_data.append({
        "game_id": row['game_id'],
        "delta_w_total": round(delta_w_total, 2),
        "integrity_penalty": round(integrity_penalty, 2),
        "delta_w_final": round(delta_w_final, 2),
        "ora_trigger": ora_engaged,
        "ora_reason": "Low Margin" if ora_engaged else "None"
    })
df_ws06 = pd.DataFrame(integrity_data)
df_ws06.to_csv(f"{SCHEMA_DIR}/06_integrity_ora.csv", index=False)

# --- SHEET 07: PLAYER PROPS (INITIALIZE) ---
print("   > Initializing Sheet 07 (Player Props)...")
cols_07 = ["player_id", "game_id", "prop_type", "line", "agent_proj", "edge"]
pd.DataFrame(columns=cols_07).to_csv(f"{SCHEMA_DIR}/07_player_props.csv", index=False)

# --- SHEET 08: META TRAINER (INITIALIZE) ---
print("   > Initializing Sheet 08 (Meta Trainer)...")
ws08 = [{"iteration": 1, "alpha_current": 3.0, "gamma_current": 0.05, "last_error": 0.0}]
pd.DataFrame(ws08).to_csv(f"{SCHEMA_DIR}/08_meta_trainer.csv", index=False)

# --- SHEET 09: AUDIT LOG (INITIALIZE) ---
print("   > Initializing Sheet 09 (Audit Log)...")
cols_09 = ["timestamp", "game_id", "decision", "reasoning"]
pd.DataFrame(columns=cols_09).to_csv(f"{SCHEMA_DIR}/09_audit_log.csv", index=False)

# --- SHEET 10: DASHBOARD (THE OUTPUT) ---
print("   > Writing Sheet 10 (Final Dashboard)...")
dash_data = []
for i, row in df_ws06.iterrows():
    # Interpret Confidence
    conf = "HIGH"
    if row['ora_trigger']: conf = "LOW (ORA ENGAGED)"
    elif abs(row['integrity_penalty']) > 1.0: conf = "MEDIUM (High Volatility)"
    
    dash_data.append({
        "game_id": row['game_id'],
        "pred_score": row['delta_w_final'],
        "confidence": conf,
        "alert": row['ora_reason']
    })
pd.DataFrame(dash_data).to_csv(f"{SCHEMA_DIR}/10_final_dashboard.csv", index=False)

print("\n✅ BATCH 2 COMPLETE: Executive Layers (05-10) are LIVE.")
print("   - Integrity Constraint Applied.")
print("   - Dashboard Generated.")
