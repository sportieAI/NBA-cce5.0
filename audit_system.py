import os
import pandas as pd
import datetime

SCHEMA_DIR = "schema"
expected_files = [
    "01_data_inventory.csv",
    "02_games_master.csv",
    "03_pillars_context.csv",
    "04_cce_core.csv"
]

print("\n🔍 ARCHON SYSTEM AUDIT (Phase 1: Foundation)")
print("=" * 60)
print(f"{'WORKSHEET':<25} | {'STATUS':<10} | {'ROWS':<5} | {'COLS':<5} | {'SIZE (KB)':<10}")
print("-" * 60)

all_safe = True

for filename in expected_files:
    path = os.path.join(SCHEMA_DIR, filename)
    
    if os.path.exists(path):
        try:
            # Read the file to check contents
            df = pd.read_csv(path)
            file_size = os.path.getsize(path) / 1024 # KB
            
            # Status Logic
            status = "✅ SAFE"
            if df.empty:
                status = "⚠️ EMPTY"
                all_safe = False
            
            print(f"{filename:<25} | {status:<10} | {len(df):<5} | {len(df.columns):<5} | {file_size:.2f}")
            
        except Exception as e:
            print(f"{filename:<25} | ❌ CORRUPT | -     | -     | -")
            all_safe = False
    else:
        print(f"{filename:<25} | ❌ MISSING | -     | -     | -")
        all_safe = False

print("=" * 60)

if all_safe:
    print("\n🏆 SYSTEM GREEN. All 4 Foundation Sheets are Saved & Populated.")
    print("   You are cleared to proceed to Worksheet 05 (Omegas).")
else:
    print("\n🛑 SYSTEM RED. Do not proceed. Re-run the builder for the missing sheet.")
