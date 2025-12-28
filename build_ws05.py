import pandas as pd
import os

# Ensure schema directory exists
os.makedirs('schema', exist_ok=True)

# Define Worksheet 05 Columns as per Agent Documentation
cols_05 = [
    "game_id", "omega_gravity_epm", "omega_pc_d", "omega_venue", 
    "omega_loadgage", "omega_media_bias", "omega_other", "omega_sum"
]

# Create the CSV with the correct structure
df_05 = pd.DataFrame(columns=cols_05)
df_05.to_csv('schema/05_omegas.csv', index=False)

print("---")
print("✅ SUCCESS: Worksheet 05 (Omegas) saved to disk.")
print(f"Path: {os.path.abspath('schema/05_omegas.csv')}")
print("---")
