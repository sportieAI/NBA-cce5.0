import pandas as pd

# Define the "Gama" Logic Rows for the missing sheets
logic_data = {
    "00_master_agent.csv": {
        "field": "Agent Identity", 
        "value": "NBA Mathematical Genius (HEVS-81 + ORA 5.3)", 
        "section": "GOVERNANCE"
    },
    "02_games_master.csv": {
        "game_id": "KEY: season_date_home_away", 
        "netrtg_delta": "FORMULA: netrtg_home - netrtg_away", 
        "decay_x_raw": "FORMULA: Q4_efficiency / Q1_efficiency"
    },
    "05_omegas.csv": {
        "game_id": "LINK: WS02", 
        "omega_gravity_epm": "rho=1.3 | Gap > 2.0", 
        "omega_other": "STAKES: Playoff Urgency (+1.5) | Revenge (+0.5)"
    },
    "07_player_props.csv": {
        "game_id": "LINK: WS02", 
        "lineup_exposure": "GRAVITY: +1.2 scale if 2+ Spacers", 
        "usage_vacuum": "ALGO: DISTRIBUTE(missing_usage)"
    },
    "08_meta_trainer.csv": {
        "task_id": "KEY: season_regime", 
        "regime_stability": "GUARDRAIL: deviation from 3-season mean", 
        "mae": "METRIC: MAE on Holdout"
    }
}

for file, logic_row in logic_data.items():
    try:
        df = pd.read_csv(file)
        # Create a DataFrame for the new logic row with the same columns
        new_row = pd.DataFrame([logic_row], columns=df.columns)
        # Insert at the top
        df_new = pd.concat([new_row, df], ignore_index=True).drop_duplicates().head(1)
        df_new.to_csv(file, index=False)
        print(f"✅ Logic baked into {file}")
    except Exception as e:
        print(f"❌ Failed to update {file}: {e}")

print("\n--- BAKE COMPLETE: Run final_root_check.py again to verify. ---")
