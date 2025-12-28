import pandas as pd
import os

# 1. SETUP FOLDERS
SCHEMA_DIR = "schema"
if not os.path.exists(SCHEMA_DIR):
    os.makedirs(SCHEMA_DIR)

print("🚀 DEPLOYING FULL SYSTEM TO DISK...")

# 2. DEFINE THE 12-WORKSHEET ARCHITECTURE
sheets = {
    "00_master_agent": ["field", "value", "section"],
    "01_data_inventory": ["source_id", "source_name", "type", "endpoint_or_file", "last_fetch", "latency", "key_numeric_fields", "sample_path", "notes"],
    "02_games_master": ["game_id", "season", "date", "home_team", "away_team", "netrtg_home", "netrtg_away", "netrtg_delta", "efg_home", "efg_away", "efg_gap", "pace", "tov_pct_home", "tov_pct_away", "tov_pct_delta", "v_pos_raw", "decay_x_raw", "chaos_integrity", "deterrence_delta", "elasticity", "paint_wall_pct", "epm_topA", "epm_topB", "epm_loss_A", "epm_loss_B", "injury_flag_A", "injury_flag_B", "minutes_restriction_A", "minutes_restriction_B", "venue_type", "b2b_flag_A", "b2b_flag_B", "travel_miles_A", "travel_miles_B", "market_spread", "closing_line_move", "win_prob_snapshot", "leverage_index", "garbage_time_pct", "imputed_count", "low_confidence_flag"],
    "03_pillars_context": ["team", "date", "rolling_90_netrtg_mean", "rolling_90_netrtg_std", "rolling_90_efg_mean", "rolling_90_efg_std", "rolling_90_vpos_median", "rolling_90_decay_iqr", "last_30_games_count"],
    "04_cce_core": ["game_id", "DeltaW_Fund", "physics", "deterrence", "v_pos", "decay_x_z", "win_signal", "win_signal_adj", "signal_points", "alpha_used"],
    "05_omegas": ["game_id", "omega_gravity_epm", "omega_pc_d", "omega_venue", "omega_loadgage", "omega_media_bias", "omega_other", "omega_sum"],
    "06_integrity_ora": ["game_id", "deltaW_total", "volatility", "omega_integrity_loss", "deltaW_final", "model_confidence", "ora_flag", "ora_side", "ora_nudge", "ora_reasons", "final_score_post_ORA"],
    "07_player_props": ["game_id", "player_id", "team", "minutes_proj", "usage_proj", "epm_player", "usage_vacuum", "lineup_exposure", "points_proj", "rebounds_proj", "assists_proj", "prop_confidence", "imputed_flag"],
    "08_meta_trainer": ["task_id", "task_desc", "alpha", "gamma", "tau_ORA", "delta_ORA", "model_type", "mae", "ev", "cover_rate", "calibration", "notes", "artifact_path"],
    "09_audit_log": ["timestamp", "game_id", "deltaW_fund", "deltaW_final", "final_score_post_ORA", "ora_used", "ora_reasons", "human_reviewed", "reviewer", "decision", "artifact_path"],
    "10_dashboard_kpi": ["date", "games_scored", "cover_rate", "mae", "avg_ev", "ora_rate", "ora_override_rate", "human_queue_length", "data_latency_alert"],
    "openmic_payloads": ["game_id", "payload_json", "generated_text", "model_version", "timestamp", "human_edit_flag"]
}

# 3. CREATE FILES
for name, cols in sheets.items():
    pd.DataFrame(columns=cols).to_csv(f"{SCHEMA_DIR}/{name}.csv", index=False)
    print(f"   ✅ Created: {name}.csv")

# 4. ADD DATA WORKFLOW TO MASTER AGENT (WS 00)
workflow = [
    {"field": "Ingest Phase", "value": "Pull PBP, box, lineup, market lines", "section": "Workflow"},
    {"field": "Engineering Phase", "value": "Build WS02 and WS03 context", "section": "Workflow"},
    {"field": "Causal Core Phase", "value": "Compute Pillars and Win_Signal (WS04)", "section": "Workflow"},
    {"field": "Volatility Phase", "value": "Compute Omegas (WS05)", "section": "Workflow"},
    {"field": "Executive Control", "value": "Integrity + ORA Overrides (WS06)", "section": "Workflow"},
    {"field": "Output Phase", "value": "Dashboard (WS10) + OpenMic Narrative", "section": "Workflow"}
]
pd.DataFrame(workflow).to_csv(f"{SCHEMA_DIR}/00_master_agent.csv", index=False)
print("🏆 WORKFLOW ADDED TO MASTER AGENT.")

