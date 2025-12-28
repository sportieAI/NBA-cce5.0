import pandas as pd
import os

# Define Worksheet 06 Columns as per Project Call
cols_06 = [
    "game_id", "deltaW_total", "volatility", "omega_integrity_loss", 
    "deltaW_final", "model_confidence", "ora_flag", "ora_side", 
    "ora_nudge", "ora_reasons", "final_score_post_ORA"
]

# Create the CSV in the repository root
df_06 = pd.DataFrame(columns=cols_06)

# Populate a template row with the core math definitions
template_row = {
    "game_id": "FORMULA_REFERENCE",
    "deltaW_total": "Fund + Omegas + Signals",
    "volatility": "Total - Fund",
    "omega_integrity_loss": "gamma * (volatility^2)",
    "deltaW_final": "Total - IntegrityLoss",
    "model_confidence": "Baseline 1.0 minus penalties",
    "ora_flag": "IF ABS(Final) < 2.0 AND Conf <= 0.85",
    "ora_side": "+1/-1/0",
    "ora_nudge": "1.5 to 3.0 scaled by ORA_Conf",
    "ora_reasons": "Motivation/B2B/Travel/Scratches",
    "final_score_post_ORA": "Final + Nudge"
}

df_06 = pd.concat([df_06, pd.DataFrame([template_row])], ignore_index=True)
df_06.to_csv('06_integrity_ora.csv', index=False)

print("---")
print("✅ SUCCESS: Worksheet 06 (Integrity & ORA) saved to Repo Root.")
print("---")
