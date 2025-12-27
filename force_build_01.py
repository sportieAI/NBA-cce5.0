import os

# 1. Define the Location
folder = "schema"
filename = "01_data_inventory.csv"
filepath = os.path.join(folder, filename)

# 2. Force Create the Directory
if not os.path.exists(folder):
    os.makedirs(folder)
    print(f"📂 Created folder: {os.path.abspath(folder)}")

# 3. Define the Exact Data (Savant, PBP, Vegas)
content = """source_id,source_name,type,endpoint_or_file,last_fetch,latency,key_numeric_fields,sample_path,notes
SRC_SAVANT_ADV,Savant / Advanced Stats Feed,box,raw_data/savant_stats.csv,2025-12-27T12:00:00,4.0,"epm_topA, epm_loss_B, paint_wall_pct, elasticity",raw_data/savant_sample.csv,"High-fidelity advanced metrics. Primary source for Omegas."
SRC_NBA_PBP,NBA Play-by-Play (History Runner),feed,nba_api.live.nba.endpoints.playbyplay,2025-12-27T12:00:00,0.5,"clock, period, score_margin",raw_data/pbp_sample.json,"Used for Garbage Time calculation and volatility checks."
SRC_BOX_SCORES,Official Box Scores,box,nba_api.stats.endpoints.boxscoretraditionalv2,2025-12-27T12:00:00,2.0,"PTS, REB, AST, TOV, FGA, FGM",raw_data/box_sample.json,"Foundational data for NetRtg and Fundamental Anchor."
SRC_ODDS_MKT,Vegas Market Data,market,the-odds-api.com,PENDING,1.0,"market_spread, closing_line_move, implied_prob",raw_data/odds_sample.json,"Critical for calculating Leverage Index and EV."
SRC_ROTOWIRE,Rotowire Injuries,feed,rotowire.com/feeds/nba,PENDING,15.0,"status_id, days_out",raw_data/injuries.csv,"Populates injury_flag_A/B and minutes_restriction fields."
"""

# 4. Write the File
with open(filepath, "w") as f:
    f.write(content)

# 5. Verify and Print Location
print(f"✅ SUCCESS: File created at: {os.path.abspath(filepath)}")
print("-" * 30)
with open(filepath, "r") as f:
    print(f.read())
print("-" * 30)
