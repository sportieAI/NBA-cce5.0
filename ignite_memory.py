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
print("⛽ Pumping Raw Fuel (LAL vs BOS)...")
game_data = {
    "game_id": "GAME_IGNITION_001",
    "date": datetime.date.today(),
    "home_team": "LAL",
    "away_team": "BOS",
    "netrtg_home": 2.5,
    "netrtg_away": 4.0,
    "NetRtg_Diff": -1.5,
    "eFG_Diff": -0.02,
    "Home_B2B": True,    # TEST: Fatigue Sensor
    "Home_Lost_Last": True, # TEST: Resilience Sensor
    "Away_Miles": 2500,  # TEST: Entropy Sensor
    "Actual_Margin": -5  # The Truth (used for Regret calc)
}

# --- STEP 2: THE BRAIN PROCESSES (CCE + HUMAN) ---
print("🧠 Processing via CCE V5.0 & Human Layers...")

human_impact = human_signals.calculate_human_signal(game_data)
print(f"   > Human Signal Detected: {human_impact:.2f} pts")

cce_result = cce_core.cce_v5_predict(game_data, human_signal=human_impact)
print(f"   > CCE Prediction: {cce_result['DeltaW_Final']:.2f} (Confidence: {cce_result['Integrity_Penalty']:.4f})")

ora_engaged, ora_reason = cce_core.run_ora_audit(cce_result, 0.8)
print(f"   > ORA Status: {'ENGAGED' if ora_engaged else 'STANDBY'} ({ora_reason})")

# --- STEP 3: THE MEMORY WRITE (BAKING IT IN) ---
print("💾 Writing to The Sanctuary (Schema CSVs)...")

def append_to_worksheet(filename, data_dict):
    path = os.path.join(SCHEMA_DIR, filename)
    if os.path.exists(path):
        df = pd.read_csv(path)
        new_row = pd.DataFrame([data_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(path, index=False)
        print(f"   ✅ Updated {filename}")
    else:
        print(f"   ❌ Error: {filename} not found.")

# Update Worksheet 04 (The Brain)
append_to_worksheet("04_cce_core.csv", {
    "game_id": game_data["game_id"],
    "delta_w_fund": cce_result["DeltaW_Fund"],
    "win_signal": cce_result["Win_Signal"],
    "raw_prediction": cce_result["DeltaW_Total"]
})

# Update Worksheet 15 (The Nerves - Regret/Trust)
regret = cce_result["DeltaW_Final"] - game_data["Actual_Margin"]
append_to_worksheet("15_cycle_signals.csv", {
    "game_id": game_data["game_id"],
    "volatility_gap": abs(regret),
    "ora_regret": regret if ora_engaged else 0,
    "trust_delta": 1.0 if abs(regret) < 3 else -1.0,
    "signal_density": 10
})

print("\n🚀 SYSTEM IGNITION COMPLETE.")
print("The 'Monster' is alive. Data is flowing through the 16-worksheet veins.")
