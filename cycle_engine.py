import pandas as pd
import os
import uuid
import datetime
import numpy as np

# --- CONFIGURATION ---
SCHEMA_DIR = "./schema"
SIGNALS_PATH = os.path.join(SCHEMA_DIR, "15_cycle_signals.csv")
PROPS_PATH = os.path.join(SCHEMA_DIR, "16_posterior_props.csv")
HISTORY_PATH = os.path.join(SCHEMA_DIR, "12_predictions_history.csv")

# Ensure history file exists (if not created yet)
if not os.path.exists(HISTORY_PATH):
    pd.DataFrame(columns=["game_id", "cycle_id", "timestamp", "prediction"]).to_csv(HISTORY_PATH, index=False)

# --- BAYESIAN BRAIN ---
def bayesian_update(prior_mean, prior_var, observed_val, lik_var=10.0):
    """Refines player expectations based on new evidence."""
    if prior_var == 0: prior_var = 1.0
    numerator = (lik_var * prior_mean) + (prior_var * observed_val)
    denominator = prior_var + lik_var
    post_mean = numerator / denominator
    post_var = 1 / ((1/prior_var) + (1/lik_var))
    return post_mean, post_var

# --- THE CYCLE RUNNER ---
def run_historical_cycle_upgraded(games_df, agent, cycle_id=None):
    if cycle_id is None:
        cycle_id = str(uuid.uuid4())[:8]
    
    print(f"⚡ Starting Historical Cycle {cycle_id}...")
    
    signal_rows = []
    prop_updates = []
    
    for idx, row in games_df.iterrows():
        # 1. BLIND PREDICTION (Mask Actuals)
        blind_row = row.copy()
        blind_row['Actual_Margin'] = None # Hide the truth!
        
        # 2. Agent Predicts
        prediction_artifact = agent.predict(blind_row)
        
        pred_margin = prediction_artifact.get('predicted_margin', 0)
        conf = prediction_artifact.get('confidence', 0.5)
        ora_used = prediction_artifact.get('ora_used', False)
        
        # 3. REVEAL & EVALUATE
        actual_margin = row.get('Actual_Margin', 0)
        actual_winner_home = actual_margin > 0
        pred_winner_home = pred_margin > 0
        
        # 4. GENERATE META-SIGNALS
        vol_gap = abs(pred_margin - actual_margin)
        
        # ORA Regret: Did ORA intervene and make it worse?
        ora_regret = 0
        if ora_used:
            raw_pred = prediction_artifact.get('raw_margin', pred_margin)
            if (raw_pred > 0) == actual_winner_home and (pred_margin > 0) != actual_winner_home:
                ora_regret = 1
        
        # ORA Miss: Should ORA have intervened?
        ora_miss = 0
        if not ora_used and vol_gap > 10.0:
            ora_miss = 1
            
        # Trust Delta: High confidence but wrong result?
        is_correct = (pred_winner_home == actual_winner_home)
        trust_delta = abs(conf - (1.0 if is_correct else 0.0))
        
        signal_rows.append({
            "game_id": row.get('game_id', idx),
            "cycle_id": cycle_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "agent_variant": getattr(agent, "version", "v1.0"),
            "volatility_gap": round(vol_gap, 2),
            "ORA_regret": ora_regret,
            "ORA_miss": ora_miss,
            "trust_delta": round(trust_delta, 3),
            "signal_density": prediction_artifact.get('signal_density', 0),
            "notes": "High volatility" if vol_gap > 12 else "Normal"
        })

    # 5. COMMIT TO MEMORY
    if signal_rows:
        pd.DataFrame(signal_rows).to_csv(SIGNALS_PATH, mode='a', header=False, index=False)
        print(f"✅ Committed {len(signal_rows)} signals to Long-Term Memory.")
        
    return cycle_id

# --- TEST MODE (Runs only if you run this script directly) ---
if __name__ == "__main__":
    # 1. Create a Fake Agent
    class MockAgent:
        version = "Test_Agent_V1"
        def predict(self, row):
            # Pretend to think
            return {
                "predicted_margin": 5.0, # Predicts Home wins by 5
                "confidence": 0.8,
                "ora_used": False,
                "raw_margin": 5.0
            }

    # 2. Create a Fake Game Dataframe
    data = {
        "game_id": ["GAME_001"],
        "Actual_Margin": [-2.0] # Home actually LOST by 2 (Big upset!)
    }
    df_test = pd.DataFrame(data)

    # 3. Run the Engine
    print("🧪 Running Test Cycle...")
    run_historical_cycle_upgraded(df_test, MockAgent())
    print("🚀 Test Complete. The engine is live.")