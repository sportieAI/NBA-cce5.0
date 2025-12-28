import pandas as pd
import os

# Exactly 13 columns as per project call
cols_07 = [
    "game_id", "player_id", "team", "minutes_proj", "usage_proj", 
    "epm_player", "usage_vacuum", "lineup_exposure", "points_proj", 
    "rebounds_proj", "assists_proj", "prop_confidence", "imputed_flag"
]

# Defining the Formula/Algorithm and Source row for your keeping
logic_row = {
    "game_id": "LINK: Games Master",
    "player_id": "SOURCE: Roster Feed",
    "team": "SOURCE: Roster Feed",
    "minutes_proj": "FORMULA: baseline + replacement_adj",
    "usage_proj": "FORMULA: baseline * minutes_proj_scale",
    "epm_player": "SOURCE: RAPM/EPM Feed",
    "usage_vacuum": "ALGO: SUM(missing_usage_from_injuries)",
    "lineup_exposure": "SOURCE: CTG / Lineup Data",
    "points_proj": "MODEL: Ridge/XGB(usage, mins, epm)",
    "rebounds_proj": "MODEL: Ridge/XGB(usage, mins, epm)",
    "assists_proj": "MODEL: Ridge/XGB(usage, mins, epm)",
    "prop_confidence": "ALGO: f(imputed_count, lineup_certainty)",
    "imputed_flag": "TYPE: Boolean (True if any imputed)"
}

# Create, append logic row, and save to root
df_07 = pd.DataFrame(columns=cols_07)
df_07 = pd.concat([df_07, pd.DataFrame([logic_row])], ignore_index=True)
df_07.to_csv('07_player_props.csv', index=False)

print("---")
print("VERIFICATION: 07_player_props.csv created in root with Formulas & Sources.")
print("---")
