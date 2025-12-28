import pandas as pd
import os

SCHEMA_DIR = "schema"
print("👮‍♂️ STARTING SYSTEM VERIFICATION AUDIT...")
print("=" * 60)

# --- DEFINING THE BLUEPRINT (What the Project Calls For) ---
# Exact columns requested in your definitions
BLUEPRINTS = {
    "02_games_master.csv": {
        "columns": [
            "game_id", "season", "date", "home_team", "away_team", 
            "netrtg_home", "netrtg_away", "netrtg_delta",
            "efg_home", "efg_away", "efg_gap", "pace",
            "tov_pct_home", "tov_pct_away", "tov_pct_delta",
            "v_pos_raw", "decay_x_raw", "chaos_integrity",
            "deterrence_delta", "elasticity", "paint_wall_pct",
            "epm_topA", "epm_topB", "epm_loss_A", "epm_loss_B",
            "injury_flag_A", "injury_flag_B", 
            "minutes_restriction_A", "minutes_restriction_B",
            "venue_type", "b2b_flag_A", "b2b_flag_B", 
            "travel_miles_A", "travel_miles_B",
            "market_spread", "closing_line_move", 
            "win_prob_snapshot", "leverage_index", "garbage_time_pct",
            "imputed_count", "low_confidence_flag"
        ],
        "defaults": {
            "numeric": 0.0, "text": "UNKNOWN", "date": "2024-01-01", "bool": False
        }
    },
    "03_pillars_context.csv": {
        "columns": [
            "team", "date", 
            "rolling_90_netrtg_mean", "rolling_90_netrtg_std",
            "rolling_90_efg_mean", "rolling_90_efg_std",
            "rolling_90_vpos_median", "rolling_90_decay_iqr",
            "last_30_games_count"
        ],
        "defaults": {"numeric": 0.0, "text": "UNK"}
    },
    "04_cce_core.csv": {
        "columns": [
            "game_id", "DeltaW_Fund", 
            "physics", "deterrence", "v_pos", "decay_x_z",
            "win_signal", "win_signal_adj", "signal_points", "alpha_used"
        ],
        "defaults": {"numeric": 0.0, "text": "UNK"}
    },
    "05_omegas.csv": {
        "columns": [
            "game_id", "omega_gravity_epm", "omega_pc_d", 
            "omega_venue", "omega_loadgage", "omega_media_bias", 
            "omega_other", "omega_sum"
        ],
        "defaults": {"numeric": 0.0, "text": "UNK"}
    }
}

# --- THE AUDIT LOOP ---
all_green = True

for filename, spec in BLUEPRINTS.items():
    filepath = f"{SCHEMA_DIR}/{filename}"
    required_cols = spec['columns']
    
    print(f"\n📄 CHECKING: {filename}")
    
    # 1. CREATE IF MISSING
    if not os.path.exists(filepath):
        print(f"   ❌ FILE MISSING. Creating shell...")
        df = pd.DataFrame(columns=required_cols)
        df.to_csv(filepath, index=False)
        print(f"   ✅ Created {filename} with 0 rows.")
    else:
        df = pd.read_csv(filepath)
    
    # 2. VERIFY COLUMNS
    missing_cols = []
    for col in required_cols:
        if col not in df.columns:
            missing_cols.append(col)
    
    if missing_cols:
        print(f"   ⚠️  MISSING {len(missing_cols)} COLUMNS (Project Call Requirement).")
        print(f"      Fixing: {missing_cols[:3]}...")
        
        # Inject Missing Columns with Defaults
        for col in missing_cols:
            if "flag" in col or "low_conf" in col:
                df[col] = False
            elif "team" in col or "date" in col or "id" in col:
                df[col] = "UNKNOWN"
            else:
                df[col] = 0.0
        
        # Re-order to match Blueprint exactly
        df = df.reindex(columns=required_cols)
        df.to_csv(filepath, index=False)
        print(f"   ✅ REPAIRED. All {len(required_cols)} columns are now present.")
    else:
        print(f"   ✅ STRUCTURE PERFECT ({len(required_cols)} Cols).")

    # 3. VERIFY ROWS
    print(f"   📊 ROW COUNT: {len(df)}")
    if len(df) < 5:
         print("   ⚠️  WARNING: Data is Sample Sized (Empty or Low).")

# --- FINAL LINKAGE CHECK ---
print("\n🔗 CHECKING WORKSHEET LINKAGE...")
try:
    df02 = pd.read_csv(f"{SCHEMA_DIR}/02_games_master.csv")
    df03 = pd.read_csv(f"{SCHEMA_DIR}/03_pillars_context.csv")
    df04 = pd.read_csv(f"{SCHEMA_DIR}/04_cce_core.csv")
    
    if not df02.empty and not df04.empty:
        # Check if Game IDs match between Master and Brain
        overlap = len(set(df02['game_id'].astype(str)).intersection(set(df04['game_id'].astype(str))))
        print(f"   > WS 02 <--> WS 04: {overlap} Games Linked.")
        if overlap == 0:
            print("   ❌ LINK BROKEN: Brain (04) has no matching Game IDs with Master (02).")
        else:
            print("   ✅ LINK CONFIRMED.")
    else:
        print("   ⚠️ Cannot check links (files are empty).")

except Exception as e:
    print(f"   ⚠️ Linkage Check Failed: {e}")

print("=" * 60)
