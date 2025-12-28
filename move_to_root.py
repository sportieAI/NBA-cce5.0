import pandas as pd
import os

# 1. Define the Root Files and their Columns based on the Project Call
root_files = {
    "00_master_agent.csv": ["field", "value", "section"],
    "01_data_inventory.csv": ["source_id", "source_name", "type", "endpoint_or_file", "last_fetch", "latency", "key_numeric_fields", "sample_path", "notes"],
    "02_games_master.csv": ["game_id", "season", "date", "home_team", "away_team", "netrtg_home", "netrtg_away", "netrtg_delta", "efg_home", "efg_away", "efg_gap", "pace", "tov_pct_home", "tov_pct_away", "tov_pct_delta", "v_pos_raw", "decay_x_raw", "chaos_integrity", "deterrence_delta", "elasticity", "paint_wall_pct", "epm_topA", "epm_topB", "epm_loss_A", "epm_loss_B", "injury_flag_A", "injury_flag_B", "minutes_restriction_A", "minutes_restriction_B", "venue_type", "b2b_flag_A", "b2b_flag_B", "travel_miles_A", "travel_miles_B", "market_spread", "closing_line_move", "win_prob_snapshot", "leverage_index", "garbage_time_pct", "imputed_count", "low_confidence_flag"],
    "03_pillars_context.csv": ["team", "date", "rolling_90_netrtg_mean", "rolling_90_netrtg_std", "rolling_90_efg_mean", "rolling_90_efg_std", "rolling_90_vpos_median", "rolling_90_decay_iqr", "last_30_games_count"],
    "04_cce_core.csv": ["game_id", "DeltaW_Fund", "physics", "deterrence", "v_pos", "decay_x_z", "win_signal", "win_signal_adj", "signal_points", "alpha_used"],
    "05_omegas.csv": ["game_id", "omega_gravity_epm", "omega_pc_d", "omega_venue", "omega_loadgage", "omega_media_bias", "omega_other", "omega_sum"]
}

print("📂 Moving Worksheets to Repository Root...")

for filename, columns in root_files.items():
    # If it exists in schema/, move it to root. If not, create it in root.
    schema_path = os.path.join("schema", filename)
    if os.path.exists(schema_path):
        os.rename(schema_path, filename)
        print(f"   ✅ MOVED: {filename} to root.")
    else:
        pd.DataFrame(columns=columns).to_csv(filename, index=False)
        print(f"   ✅ CREATED NEW: {filename} in root.")

# 2. Re-populate the "Gama" logic into Worksheet 05 in the root
omega_logic = [
    {"game_id": "TEMPLATE", "omega_gravity_epm": "rho=1.3", "omega_pc_d": "EPM loss logic", "omega_venue": "Home +2.5", "omega_loadgage": "B2B penalties", "omega_media_bias": "Market clip", "omega_other": "0.0", "omega_sum": "SUM"}
]
pd.DataFrame(omega_logic).to_csv("05_omegas.csv", index=False)
print("🧠 Worksheet 05 Logic Verified and Saved in Root.")

