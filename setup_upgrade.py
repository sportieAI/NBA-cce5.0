import pandas as pd
import os
import numpy as np

# Define file paths
project_root = "./"
schema_path = os.path.join(project_root, "schema")
os.makedirs(schema_path, exist_ok=True)

# 1. NEW WORKSHEET 15: CYCLE SIGNALS
cols_signals = [
    "game_id", "cycle_id", "timestamp", "agent_variant",
    "volatility_gap", "ORA_regret", "ORA_miss", "trust_delta",
    "signal_density", "signal_conflict", "emotional_trigger",
    "narrative_conflict", "notes"
]
df_signals = pd.DataFrame(columns=cols_signals)
path_signals = os.path.join(schema_path, "15_cycle_signals.csv")
if not os.path.exists(path_signals):
    df_signals.to_csv(path_signals, index=False)
    print(f"✅ Created: {path_signals}")

# 2. NEW WORKSHEET 16: POSTERIOR PROPS
cols_props = [
    "player_id", "player_name", "stat_type", "last_updated",
    "prior_mean", "prior_var", "observed_val",
    "posterior_mean", "posterior_var", "posterior_hit_rate", "sample_size"
]
df_props = pd.DataFrame(columns=cols_props)
path_props = os.path.join(schema_path, "16_posterior_props.csv")
if not os.path.exists(path_props):
    df_props.to_csv(path_props, index=False)
    print(f"✅ Created: {path_props}")

print("\n🚀 System Upgrade: Signal & Bayesian Layers Ready.")