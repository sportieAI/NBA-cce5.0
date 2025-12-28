import pandas as pd
import os

cols_07 = [
    "game_id", "player_id", "team", "minutes_proj", "usage_proj", 
    "epm_player", "usage_vacuum", "lineup_exposure", "points_proj", 
    "rebounds_proj", "assists_proj", "prop_confidence", "imputed_flag"
]

# Finalized Logic Row with Spacing Gravity
logic_row_07 = {
    "game_id": "LINK: 02_games_master.csv",
    "player_id": "SOURCE: Roster Feed",
    "team": "SOURCE: Roster Feed",
    "minutes_proj": "ALGO: baseline + replacement + foul_risk_adj",
    "usage_proj": "ALGO: baseline * (1 + synergy_factor)",
    "epm_player": "SOURCE: EPM Feed",
    "usage_vacuum": "ALGO: DISTRIBUTE(missing_star_usage) -> active_starters",
    "lineup_exposure": "GRAVITY: +1.2 scale if 2+ Elite Spacers on floor",
    "points_proj": "MODEL: XGBoost(gravity_delta, usage_vacuum, rest)",
    "rebounds_proj": "MODEL: XGBoost(positional_contested_rate)",
    "assists_proj": "MODEL: XGBoost(potential_assists_converted)",
    "prop_confidence": "ALGO: f(sample_size, spacing_certainty)",
    "imputed_flag": "BOOL: True if spacing/gravity is estimated"
}

df_07 = pd.DataFrame(columns=cols_07)
df_07 = pd.concat([df_07, pd.DataFrame([logic_row_07])], ignore_index=True)
df_07.to_csv('07_player_props.csv', index=False)

print("---")
print("👑 CROWN JEWEL: Worksheet 07 (Player Props) is finalized in root.")
print("Logic: Spacing Gravity and Synergy Multipliers are locked in.")
print("---")
