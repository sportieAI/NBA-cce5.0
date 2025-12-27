import pandas as pd
import os
import datetime
import cce_core      # The Math Brain
import human_signals # The Human Layers

# --- CONFIGURATION ---
SCHEMA_DIR = "./schema"
CYCLE_ID = f"IGNITION_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"

print(f"🔥 INITIATING SYSTEM IGNITION: {CYCLE_ID}")

# --- STEP 1: CREATE THE RAW FUEL (Simulating Worksheet 02) ---
# We simulate a "perfect storm" game to test every sensor.
print("⛽ Pumping Raw Fuel (LAL vs BOS)...")
game_data = {
    "game_id": "GAME_IGNITION_001",
    "date": datetime.date.today(),
    "home_team": "LAL",
    "away_team": "BOS",
    "netrtg_home": 2.5,
    "netrtg_away": 4.0,
    "NetRtg_Diff": -1.5, # LAL is underdog by 1.5 NetRtg
    "eFG_Diff": -0.02,
    "Home_B2B": True,    # TEST: Fatigue Sensor
    "Home_Lost_Last": True, # TEST: Resilience Sensor
    "Away_Miles": 2500,  # TEST: Entropy Sensor
    "Actual_Margin": -5  # The Truth (used for Regret calc)
}

# --- STEP 2: THE BRAIN PROCESSES (CCE + HUMAN) ---
print("🧠 Processing via CCE V5.0 & Human Layers...")

# A. The Human Element (Worksheet 03/05)
# Checks: Fatigue, Resilience, Entropy
human_impact = human_signals.calculate_human_signal(game_data)
print(f"   > Human Signal Detected: {human_impact:.2f} pts")

# B. The Causal Core (Worksheet 04)
# Checks: Physics, Deterrence, ORA
cce_result = cce_core.cce_v5_predict(game_data, human_signal=human_impact)
print(f"   > CCE Prediction: {cce_result['DeltaW_Final']:.2f} (Confidence: {cce_result['Integrity_Penalty']:.4f})")

# C. The ORA Audit (Worksheet 06)
ora_engaged, ora_reason = cce_core.run_ora_audit(cce_result, 0.8)
print(f"   > ORA Status: {'ENGAGED' if ora_engaged else 'STANDBY'} ({ora_reason})")

# --- STEP 3: THE MEMORY WRITE (BAKING IT IN) ---
print("💾 Writing to The Sanctuary (Schema CSVs)...")

def append_to_worksheet(filename, data_dict):
    path = os.path.join(SCHEMA_DIR, filename)
    if os.path.exists(path):
        df = pd.read_csv(path)
        # Convert dict to DataFrame row
        new_row = pd.DataFrame([data_dict])
        # Combine and save
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(path, index=False)
        print(f"   ✅ Updated {filename}")
    else:
        print(f"   ❌ Error: {filename} not found.")

# 1. Update Worksheet 04 (The Brain)
append_to_worksheet("04_cce_core.csv", {
    "game_id": game_data["game_id"],
    "delta_w_fund": cce_result["DeltaW_Fund"],
    "win_signal": cce_result["Win_Signal"],
    "raw_prediction": cce_result["DeltaW_Total"]
})

# 2. Update Worksheet 06 (The Law)
append_to_worksheet("06_integrity_ora.csv", {
    "game_id": game_data["game_id"],
    "delta_w_final": cce_result["DeltaW_Final"],
    "integrity_penalty": cce_result["Integrity_Penalty"],
    "ora_trigger": ora_engaged,
    "ora_reasons": ora_reason
})

# 3. Update Worksheet 15 (The Nerves - Regret/Trust)
# Calculate Regret: Prediction - Actual
regret = cce_result["DeltaW_Final"] - game_data["Actual_Margin"]
append_to_worksheet("15_cycle_signals.csv", {
    "game_id": game_data["game_id"],
    "volatility_gap": abs(regret),
    "ora_regret": regret if ora_engaged else 0,
    "trust_delta": 1.0 if abs(regret) < 3 else -1.0,
    "signal_density": 10 # Max density for this test
})

# 4. Update Worksheet 10 (The Dashboard)
append_to_worksheet("10_final_dashboard.csv", {
    "game_id": game_data["game_id"],
    "pred_score": cce_result["DeltaW_Final"],
    "confidence": "HIGH" if not ora_engaged else "LOW",
    "human_signal_alert": f"Resilience Impact: {human_impact:.1f}"
})

print("\n🚀 SYSTEM IGNITION COMPLETE.")
print("The 'Monster' is alive. Data is flowing through the 16-worksheet veins.")
print("Check your 'schema' folder to see the populated files.")
