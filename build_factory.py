import os
import pandas as pd

# 1. Create the Directory
SCHEMA_DIR = "schema"
if not os.path.exists(SCHEMA_DIR):
    os.makedirs(SCHEMA_DIR)
    print(f"📂 Created directory: {SCHEMA_DIR}")

# 2. Define the 17-Worksheet Architecture (Exact Match to Blueprint)
structure = {
    "00_agent_config.csv": ["section", "field", "value", "description"],
    "01_data_inventory.csv": ["source_id", "source_name", "type", "endpoint", "last_fetch"],
    "02_games_master.csv": ["game_id", "date", "home_team", "away_team", "netrtg_home", "netrtg_away"],
    "03_pillars_context.csv": ["team_id", "physics_score", "deterrence_score", "v_pos", "decay_x"],
    "04_cce_core.csv": ["game_id", "delta_w_fund", "win_signal", "raw_prediction"],
    "05_omegas.csv": ["game_id", "w_gravity", "w_venue", "w_fatigue", "w_media", "total_volatility"],
    "06_integrity_ora.csv": ["game_id", "delta_w_final", "integrity_penalty", "ora_trigger", "ora_reason"],
    "07_player_props.csv": ["player_id", "stat_type", "line", "agent_proj", "edge"],
    "08_meta_trainer.csv": ["iteration", "alpha_weight", "gamma_weight", "calibration_error"],
    "09_audit_log.csv": ["timestamp", "decision", "override_status", "reasoning_path"],
    "10_final_dashboard.csv": ["game_id", "pred_score", "confidence", "human_signal_alert"],
    "11_transaction_log.csv": ["order_id", "amount", "stake_pct", "status"],
    "12_predictions_history.csv": ["game_id", "predicted_margin", "actual_margin", "error"],
    "13_audit_ledger.csv": ["cycle_id", "roi", "win_rate", "sharpe_ratio"],
    "14_visualization_data.csv": ["metric_name", "timestamp", "value"],
    "15_cycle_signals.csv": ["game_id", "volatility_gap", "ora_regret", "trust_delta", "signal_density"],
    "16_posterior_props.csv": ["player_id", "prior_mean", "observed_val", "posterior_mean"]
}

# 3. Build the Files
print("🏗️  Constructing the 17-Worksheet System...")
for filename, cols in structure.items():
    path = os.path.join(SCHEMA_DIR, filename)
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)
        print(f"   ✅ Created: {filename}")
    else:
        print(f"   ⏩ Exists: {filename}")

# 4. Final Count
count = len(os.listdir(SCHEMA_DIR))
print(f"\n🏛️  FACTORY STATUS: {count}/17 Worksheets Active.")
