import pandas as pd
import os

# Exactly 11 columns as per project call
cols_06 = [
    "game_id", "deltaW_total", "volatility", "omega_integrity_loss", 
    "deltaW_final", "model_confidence", "ora_flag", "ora_side", 
    "ora_nudge", "ora_reasons", "final_score_post_ORA"
]

# Injecting the Logic row (Gama Formulas + Entanglement Rules)
logic_row_06 = {
    "game_id": "LINK: 02_games_master.csv",
    "deltaW_total": "FORMULA: DeltaW_Fund + omega_sum + signal_points",
    "volatility": "FORMULA: deltaW_total - DeltaW_Fund",
    "omega_integrity_loss": "MATH: 0.05 * (volatility^2)",
    "deltaW_final": "FORMULA: deltaW_total - omega_integrity_loss",
    "model_confidence": "ALGO: 1.0 - penalties(imputed, EPM, volatility)",
    "ora_flag": "IF(ABS(deltaW_final) < 2.0 AND confidence <= 0.85, 1, 0)",
    "ora_side": "ENUM: +1(A), -1(B), 0(None)",
    "ora_nudge": "ALGO: 1.5-3.0 scaled by ORA_confidence",
    "ora_reasons": "LOG: Motivation/B2B/Travel/User_Insight",
    "final_score_post_ORA": "FORMULA: IF(ora_flag==1, deltaW_final + nudge, deltaW_final)"
}

# Write to repository root
df_06 = pd.DataFrame(columns=cols_06)
df_06 = pd.concat([df_06, pd.DataFrame([logic_row_06])], ignore_index=True)
df_06.to_csv('06_integrity_ora.csv', index=False)

print("---")
print("🛡️ GATEKEEPER ACTIVE: Worksheet 06 (Integrity & ORA) saved to root.")
print("Logic: Integrity Penalty (gamma=0.05) and ORA triggers baked in.")
print("---")
