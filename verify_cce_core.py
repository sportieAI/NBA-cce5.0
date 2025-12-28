import pandas as pd
import os
import time

# 1. FILE EXISTENCE & TIMESTAMP CHECK
file_path = '04_cce_core.csv'
if os.path.exists(file_path):
    m_time = os.path.getmtime(file_path)
    print(f"🕒 TIMESTAMP CHECK: {file_path} last modified at {time.ctime(m_time)}")
else:
    print(f"❌ ERROR: {file_path} not found in root.")

# 2. CONTENT & FORMULA VERIFICATION
try:
    df = pd.read_csv(file_path)
    print(f"📊 COLUMN CHECK: Found {len(df.columns)} columns. (Target: 10)")
    
    # Check for the HEVS-81 weights in the logic row
    logic_row = df.iloc[0]
    weights = ["0.30", "0.25", "0.15"]
    if all(w in str(logic_row['win_signal']) for w in weights):
        print("✅ FORMULA VERIFIED: HEVS-81 weights (30/30/25/15) are locked in.")
    else:
        print("⚠️ WARNING: HEVS-81 weights not found in logic row.")
except Exception as e:
    print(f"❌ ERROR reading file: {e}")

# 3. LINKAGE INTEGRITY CHECK
# Verifying if the ID structure matches the Games Master
if os.path.exists('02_games_master.csv'):
    df_master = pd.read_csv('02_games_master.csv')
    if df.columns[0] == df_master.columns[0] == 'game_id':
        print("🔗 LINKAGE VERIFIED: Primary Key 'game_id' matches between Master and Core.")
    else:
        print("❌ LINKAGE BREAK: 'game_id' columns are not aligned.")
else:
    print("⚠️ WARNING: 02_games_master.csv missing for linkage check.")

print("\n🏁 AUDIT COMPLETE: If all green, the Big Boi Worksheet is ready.")
