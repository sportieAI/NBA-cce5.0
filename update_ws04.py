import pandas as pd
import os

# Exactly 10 columns as per the CCE Core project call
cols_04 = [
    "game_id", "DeltaW_Fund", "physics", "deterrence", "v_pos", "decay_x_z",
    "win_signal", "win_signal_adj", "signal_points", "alpha_used"
]

# Injecting the Logic, Formulas, and Sources into the first row
logic_row_04 = {
    "game_id": "LINK: 02_games_master.csv",
    "DeltaW_Fund": "FORMULA: netrtg_home - netrtg_away",
    "physics": "ALGO: 0.6*z(dNetRtg) + 0.25*(-z(eFG_gap)) + 0.15*z(TOV_rank)",
    "deterrence": "ALGO: 0.6*z(Det_Delta) + 0.25*(-z(Elasticity)) + 0.15*(-z(PaintWall))",
    "v_pos": "ALGO: z(V_Pos_raw) * (1 + 0.2 * z(Chaos_Integrity))",
    "decay_x_z": "ALGO: robust_z(Decay_X) from WS03 Pillars Context",
    "win_signal": "MATH: 0.30*physics + 0.30*deterrence + 0.25*v_pos + 0.15*decay_x",
    "win_signal_adj": "ALGO: IF(decay_x_raw < 0.85, 0.9 * win_signal, win_signal)",
    "signal_points": "FORMULA: alpha * win_signal_adj",
    "alpha_used": "PARAM: Global Alpha (Initial = 3.0)"
}

# Write to repository root
df_04 = pd.DataFrame(columns=cols_04)
df_04 = pd.concat([df_04, pd.DataFrame([logic_row_04])], ignore_index=True)
df_04.to_csv('04_cce_core.csv', index=False)

print("---")
print("✅ SUCCESS: Worksheet 04 (CCE Core) updated in root.")
print("Logic: HEVS-81 Pillar Weights (30/30/25/15) and Point Mapping injected.")
print("---")
