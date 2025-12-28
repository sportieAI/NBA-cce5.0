import pandas as pd
import os

# Define Columns 
cols_00 = ["field", "value", "section"]

# Injecting the Agent's Governance and Logic [cite: 33, 34, 35]
logic_data = [
    {"field": "Agent Identity", "value": "NBA Mathematical Genius Agent (CCE V5.0 + ORA 5.3)", "section": "IDENTITY"},
    {"field": "Fundamental Anchor Law", "value": "NetRtg_A - NetRtg_B (Baseline Truth)", "section": "GOVERNANCE"},
    {"field": "HEVS-81 Win Signal", "value": "0.30*P + 0.30*D + 0.25*V + 0.15*X", "section": "MATH_ENGINE"},
    {"field": "Integrity Constraint", "value": "gamma * volatility^2 (gamma=0.05)", "section": "EXECUTIVE"},
    {"field": "ORA Threshold", "value": "tau_ORA = 2.0 (Engagement Trigger)", "section": "EXECUTIVE"},
    {"field": "Workflow: Ingest", "value": "Source 01 -> Raw CSV -> WS 02", "section": "PIPELINE"},
    {"field": "Workflow: Reasoning", "value": "WS 02 -> WS 03 -> WS 04 (Win Signal)", "section": "PIPELINE"},
    {"field": "Workflow: Decision", "value": "WS 05 -> WS 06 (Final Prediction)", "section": "PIPELINE"}
]

# Write to root
df_00 = pd.DataFrame(logic_data, columns=cols_00)
df_00.to_csv('00_master_agent.csv', index=False)

print("---")
print("✅ SUCCESS: Worksheet 00 (Master Agent) updated in root.")
print("Logic: Governance, Math Laws, and Data Workflow injected.")
print("---")
