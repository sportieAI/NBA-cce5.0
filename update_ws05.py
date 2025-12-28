import pandas as pd
import os

# Exactly 8 columns as per project call
cols_05 = [
    "game_id", "omega_gravity_epm", "omega_pc_d", "omega_venue", 
    "omega_loadgage", "omega_media_bias", "omega_other", "omega_sum"
]

# Injecting the Logic row (Gama Formulas + Sources)
# Formula: omega_sum = SUM(omega_*)
logic_row_05 = {
    "game_id": "LINK: 02_games_master.csv",
    "omega_gravity_epm": "FORMULA: IF(ABS(epmA-epmB)>2, (epmA-epmB)*1.3, 0)",
    "omega_pc_d": "ALGO: epm_loss_B - epm_loss_A (with gravity compensation)",
    "omega_venue": "VALUES: Home +2.5, Neutral 0, Pseudo 0.5-1.5",
    "omega_media_bias": "ALGO: clip((market_spread + DeltaW_Fund)/4, -1, 1)",
    "omega_loadgage": "VALUES: -0.5 first B2B, -1.5 second B2B or travel > 1500mi",
    "omega_other": "SOURCE: Coaching/Rest Modifiers",
    "omega_sum": "FORMULA: SUM of all omega columns"
}

# Write to repository root
df_05 = pd.DataFrame(columns=cols_05)
df_05 = pd.concat([df_05, pd.DataFrame([logic_row_05])], ignore_index=True)
df_05.to_csv('05_omegas.csv', index=False)

print("---")
print("✅ SUCCESS: Worksheet 05 (Omegas) updated in root.")
print("Logic: Volatility Engine Formulas (Gravity, PC-D, Load) injected.")
print("---")
