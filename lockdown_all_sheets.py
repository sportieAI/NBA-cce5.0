import pandas as pd

def save_ws(filename, cols, logic):
    # Ensure logic list matches column length
    logic_row = (logic + [""] * len(cols))[:len(cols)]
    df = pd.DataFrame([logic_row], columns=cols)
    df.to_csv(filename, index=False)
    print(f"💎 FIXED & SAVED: {filename}")

# 00 - Master Agent
save_ws("00_master_agent.csv", 
        ["field", "value", "section"], 
        ["NBA Mathematical Genius", "HEVS-81 + ORA 5.3", "GOVERNANCE"])

# 01 - Data Inventory
save_ws("01_data_inventory.csv", 
        ["source_name", "endpoint", "refresh_rate", "reliability_score"], 
        ["SOURCE: NBA API", "https://stats.nba.com", "Real-time", "0.95"])

# 02 - Games Master
save_ws("02_games_master.csv", 
        ["game_id", "netrtg_delta", "decay_x_raw"] + [f"stat_{i}" for i in range(38)], 
        ["KEY: season_date_home_away", "FORMULA: netrtg_home - netrtg_away", "FORMULA: Q4_eff / Q1_eff"])

# 03 - Pillars Context
save_ws("03_pillars_context.csv", 
        ["team", "date", "rolling_90_netrtg_mean", "rolling_90_netrtg_std", "rolling_90_efg_mean", "rolling_90_efg_std", "rolling_90_vpos_median", "rolling_90_decay_iqr", "last_30_games_count"], 
        ["SOURCE: WS02", "KEY: Date", "ALGO: rolling(90).mean()", "ALGO: rolling(90).std()", "ALGO: rolling(90).mean()", "ALGO: rolling(90).std()", "ALGO: rolling(90).median()", "ALGO: rolling(90).iqr()", "ALGO: count"])

# 04 - CCE Core
save_ws("04_cce_core.csv", 
        ["game_id", "DeltaW_Fund", "physics", "deterrence", "v_pos", "decay_x_z", "win_signal", "win_signal_adj", "signal_points", "alpha_used"], 
        ["LINK: WS02", "ANCHOR: DeltaW", "0.30 Physics", "0.30 Det", "0.25 VPos", "0.15 Decay", "0.30P+0.30D+0.25V+0.15X", "Fatigue Adj", "alpha*signal", "PARAM: Alpha"])

# 05 - Omegas
save_ws("05_omegas.csv", 
        ["game_id", "omega_gravity_epm", "omega_pc_d", "omega_venue", "omega_loadgage", "omega_media_bias", "omega_other", "omega_sum"], 
        ["LINK: WS02", "rho=1.3", "PC-D Logic", "Home +2.5", "B2B/Travel", "CLIP: -1 to +1", "STAKES: Playoff Urgency (+1.5) | Revenge (+0.5)", "TOTAL SUM"])

# 06 - Integrity ORA
save_ws("06_integrity_ora.csv", 
        ["game_id", "deltaW_total", "volatility", "omega_integrity_loss", "deltaW_final", "model_confidence", "ora_flag", "ora_side", "ora_nudge", "ora_reasons", "final_score_post_ORA"], 
        ["LINK: WS02", "TOTAL", "DELTA", "0.05 * volatility^2", "FINAL", "CONFIDENCE", "ORA_FLAG", "SIDE", "NUDGE", "REASONS", "SCORE"])

# 07 - Player Props
save_ws("07_player_props.csv", 
        ["game_id", "player_id", "team", "minutes_proj", "usage_proj", "epm_player", "usage_vacuum", "lineup_exposure", "points_proj", "rebounds_proj", "assists_proj", "prop_confidence", "imputed_flag"], 
        ["LINK: WS02", "PLAYER", "TEAM", "MINS", "USAGE", "EPM", "VACUUM: DISTRIBUTE usage", "GRAVITY: +1.2 scale", "POINTS", "REBOUNDS", "ASSISTS", "CONF", "FLAG"])

# 08 - Meta Trainer
save_ws("08_meta_trainer.csv", 
        ["task_id", "task_desc", "alpha", "gamma", "tau_ORA", "delta_ORA", "model_type", "mae", "ev", "cover_rate", "calibration", "regime_stability", "notes", "artifact_path"], 
        ["TASK", "DESC", "ALPHA", "0.05 (GAMMA)", "TAU", "DELTA", "MODEL", "MAE", "EV", "COVER", "CALIB", "STABILITY", "NOTES", "PATH"])

print("\n✅ PROJECT ENTIRETY SAVED TO DISK.")
