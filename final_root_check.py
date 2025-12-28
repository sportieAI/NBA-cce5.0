import pandas as pd
import os

worksheets = {
    "00_master_agent.csv": ["HEVS-81", "ORA Threshold"],
    "01_data_inventory.csv": ["SOURCE", "OWNER"],
    "02_games_master.csv": ["netrtg_delta", "decay_x_raw"],
    "03_pillars_context.csv": ["rolling(90)", "z-score"],
    "04_cce_core.csv": ["0.30", "0.25", "win_signal"],
    "05_omegas.csv": ["rho=1.3", "Revenge", "Stakes"],
    "06_integrity_ora.csv": ["0.05", "volatility^2", "ora_nudge"],
    "07_player_props.csv": ["GRAVITY", "Synergy", "Vacuum"],
    "08_meta_trainer.csv": ["alpha", "STABILITY", "mae"]
}

print("🔍 STARTING FULL ROOT AUDIT...\n")
missing_files = []

for ws, logic_markers in worksheets.items():
    if os.path.exists(ws):
        try:
            df = pd.read_csv(ws)
            # Check the logic row (first row of data)
            content = str(df.iloc[0].values)
            checks = [m in content for m in logic_markers]
            
            status = "✅ VALIDATED" if all(checks) else "⚠️ LOGIC MISSING"
            print(f"{ws:<25} | Columns: {len(df.columns):<2} | {status}")
        except Exception as e:
            print(f"{ws:<25} | ❌ ERROR: {e}")
    else:
        print(f"{ws:<25} | ❌ NOT FOUND")
        missing_files.append(ws)

print("\n---")
if not missing_files:
    print("💎 ALL SYSTEMS LOADED: Project Entirety is preserved in Root.")
else:
    print(f"🚨 ALERT: {len(missing_files)} files are missing from Root.")
print("---\n")
