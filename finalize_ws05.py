import pandas as pd
import os

cols_05 = [
    "game_id", "omega_gravity_epm", "omega_pc_d", "omega_venue", 
    "omega_loadgage", "omega_media_bias", "omega_other", "omega_sum"
]

# Advanced Logic row with your "Notes" included
logic_row_05 = {
    "game_id": "LINK: 02_games_master.csv",
    "omega_gravity_epm": "ρ=1.3 | Gap Threshold > 2.0",
    "omega_pc_d": "ALGO: B_loss - A_loss | +1.0 if High-Qual Replacement",
    "omega_venue": "Home: +2.5 | Neutral: 0 | Pseudo: 0.5-1.5",
    "omega_media_bias": "CLIP: -1 to +1 | Bias = (Spread + DeltaW_Fund)/4",
    "omega_loadgage": "B2B1: -0.5 | B2B2: -1.5 | Travel > 1500mi: -1.5",
    "omega_other": "Coaching / Rest / 3-in-4 Modifiers",
    "omega_sum": "TOTAL VOLATILITY OFFSET"
}

df_05 = pd.DataFrame(columns=cols_05)
df_05 = pd.concat([df_05, pd.DataFrame([logic_row_05])], ignore_index=True)
df_05.to_csv('05_omegas.csv', index=False)

print("---")
print("🎯 PERFECTION: Worksheet 05 (Omegas) finalized with Gravity Compensation.")
print("---")
