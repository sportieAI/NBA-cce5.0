import pandas as pd
import os

# --- CONFIGURATION ---
SCHEMA_DIR = "./schema"
os.makedirs(SCHEMA_DIR, exist_ok=True)

# --- THE 17-WORKSHEET SANCTUARY ---
# Exact match to your "NBAworksheets.txt" and "Nbaglossary.txt"
structure = {
    # 00: IDENTITY
    "00_agent_config.csv": ["section", "field", "value", "description"],
    
    # 01-03: SENSORY INPUT
    "01_data_inventory.csv": ["source_id", "source_name", "type", "endpoint_or_file", "last_fetch", "latency"],
    "02_games_master.csv": ["game_id", "season", "date", "home_team", "away_team", "netrtg_home", "netrtg_away"],
    "03_pillars_context.csv": ["team_id", "physics_score", "deterrence_score", "v_pos", "decay_x"],

    # 04-06: CORE REASONING (BRAIN)
    "04_cce_core.csv": ["game_id", "delta_w_fund", "win_signal", "raw_prediction"],
    "05_omegas.csv": ["game_id", "w_gravity", "w_venue", "w_fatigue", "w_media", "total_volatility"],
    "06_integrity_ora.csv": ["game_id", "delta_w_final", "integrity_penalty", "ora_trigger", "ora_nudge", "ora_reasons"],

    # 07-10: EXECUTION & OUTPUT
    "07_player_props.csv": ["player_id", "stat_type", "line", "agent_proj", "edge"],
    "08_meta_trainer.csv": ["iteration", "alpha_weight", "gamma_weight", "calibration_error"],
    "09_audit_log.csv": ["timestamp", "decision", "override_status", "reasoning_path"],
    "10_final_dashboard.csv": ["game_id", "pred_score", "confidence", "human_signal_alert"],

    # 11-14: LOGIC AUDIT
    "11_transaction_log.csv": ["order_id", "amount", "stake_pct", "status"],
    "12_predictions_history.csv": ["game_id", "predicted_margin", "actual_margin", "error"],
    "13_audit_ledger.csv": ["cycle_id", "roi", "win_rate", "sharpe_ratio"],
    "14_visualization_data.csv": ["metric_name", "timestamp", "value"],

    # 15-16: LEARNING MEMORY (The Nerves)
    "15_cycle_signals.csv": ["game_id", "volatility_gap", "ora_regret", "trust_delta", "signal_density"],
    "16_posterior_props.csv": ["player_id", "prior_mean", "observed_val", "posterior_mean"]
}

print("🏗️  Constructing the NBA-CCE5.0 Sanctuary...")

count = 0
for filename, cols in structure.items():
    path = os.path.join(SCHEMA_DIR, filename)
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)
        print(f"✅ Initialized: {filename}")
        count += 1
    else:
        print(f"⏩ Verified: {filename}")

print(f"\n🏛️  Sanctuary Complete. {count} new worksheets created.")
print("All 17 files are now ready for the Agent.")
