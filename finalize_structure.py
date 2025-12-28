import pandas as pd
import os

# Create schema folder if it doesn't exist
if not os.path.exists('schema'):
    os.makedirs('schema')

# 1. Populate Master Agent (WS 00) with Mathematical Laws
laws = [
    {"field": "Fundamental Anchor Law", "value": "NetRtg_A - NetRtg_B is baseline truth", "section": "Governance"},
    {"field": "HEVS-81 Math", "value": "0.30*P + 0.30*D + 0.25*V + 0.15*X", "section": "Math"},
    {"field": "Integrity Constant (gamma)", "value": "0.05", "section": "Math"},
    {"field": "ORA Threshold (tau)", "value": "2.0", "section": "Executive"}
]
pd.DataFrame(laws).to_csv('schema/00_master_agent.csv', index=False)

# 2. Populate Data Inventory (WS 01)
sources = [
    {"source_id": "NBA_BOX", "source_name": "Box Score Feed", "type": "ETL", "endpoint_or_file": "nba_api / CTG"},
    {"source_id": "EPM_FEED", "source_name": "EPM Impact Feed", "type": "impact", "endpoint_or_file": "EPM source"}
]
pd.DataFrame(sources).to_csv('schema/01_data_inventory.csv', index=False)

print("---")
print("VERIFICATION: Files created on disk.")
print(f"WS 00 path: {os.path.abspath('schema/00_master_agent.csv')}")
print(f"WS 01 path: {os.path.abspath('schema/01_data_inventory.csv')}")
print("---")
