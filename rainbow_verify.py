import pandas as pd

files = {
    "00_master_agent.csv": "HEVS-81",
    "02_games_master.csv": "netrtg_delta",
    "04_cce_core.csv": "win_signal",
    "05_omegas.csv": "rho=1.3",
    "06_integrity_ora.csv": "volatility^2",
    "07_player_props.csv": "GRAVITY",
    "08_meta_trainer.csv": "STABILITY",
    "09_audit_log.csv": "log_id"
}

print("🌈 RAINBOW ALIGNMENT CHECK:")
for f, marker in files.items():
    try:
        df = pd.read_csv(f)
        # We check if the logic marker exists in the first data row
        row_str = "|".join(map(str, df.iloc[0].values))
        if marker in row_str:
            print(f"✅ {f:<22} | ALIGNED | Marker Found: {marker}")
        else:
            print(f"⚠️ {f:<22} | SHIFTED | Marker '{marker}' not in correct column")
    except Exception as e:
        print(f"❌ {f:<22} | ERROR: {e}")
