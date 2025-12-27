import pandas as pd
import os
import json

# --- CONFIGURATION ---
SCHEMA_DIR = "./schema"
SIGNALS_PATH = os.path.join(SCHEMA_DIR, "15_cycle_signals.csv")
PAYLOAD_PATH = os.path.join(SCHEMA_DIR, "openmic_payloads.csv")

def generate_narrative_payloads():
    """
    Reads raw math signals and converts them into Open Mic narrative prompts.
    """
    if not os.path.exists(SIGNALS_PATH):
        print("⚠️ No signals found yet. Run the Engine first!")
        return

    # 1. Read the Memory
    df_signals = pd.read_csv(SIGNALS_PATH)
    
    payloads = []
    
    for _, row in df_signals.iterrows():
        # 2. Translate Math to English
        narrative_hooks = []
        
        # Hook 1: Volatility (The "Stress" Factor)
        if row['volatility_gap'] > 12:
            narrative_hooks.append("CHAOS_DETECTED: This game defied logic.")
        elif row['volatility_gap'] < 3:
            narrative_hooks.append("SNIPER_ACCURACY: The model saw this coming perfectly.")
            
        # Hook 2: Regret (The "Apology" Factor)
        if row['ORA_regret'] == 1:
            narrative_hooks.append("REGRET_PROTOCOL: I overthought this. My override was wrong.")
        
        # Hook 3: Trust (The "Swagger" Factor)
        if row['trust_delta'] > 0.4:
            narrative_hooks.append("FALSE_CONFIDENCE: I was sure, but I was wrong. Humble me.")

        # 3. Build the Payload
        payload = {
            "game_id": row['game_id'],
            "cycle_id": row['cycle_id'],
            "primary_emotion": "Regret" if row['ORA_regret'] == 1 else "Confidence",
            "narrative_prompt": " | ".join(narrative_hooks),
            "raw_volatility": row['volatility_gap']
        }
        payloads.append(payload)

    # 4. Save to Open Mic
    if payloads:
        df_payloads = pd.DataFrame(payloads)
        df_payloads.to_csv(PAYLOAD_PATH, index=False)
        print(f"🎙️ Open Mic Bridge Live. Generated {len(payloads)} commentary prompts.")
        print(f"📄 Saved to: {PAYLOAD_PATH}")
    else:
        print("💤 No new signals to process.")

if __name__ == "__main__":
    generate_narrative_payloads()