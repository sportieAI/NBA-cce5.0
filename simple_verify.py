import pandas as pd
import os

files = [
    "00_master_agent.csv", "01_data_inventory.csv", "02_games_master.csv", 
    "03_pillars_context.csv", "04_cce_core.csv", "05_omegas.csv", 
    "06_integrity_ora.csv", "07_player_props.csv", "08_meta_trainer.csv"
]

print("🔍 RAW LOGIC ROW CHECK:\n")
for f in files:
    if os.path.exists(f):
        df = pd.read_csv(f)
        logic_row = df.iloc[0].tolist()
        print(f"📄 {f}: {logic_row[:3]}...") # Showing first 3 logic points
    else:
        print(f"❌ {f} MISSING")
