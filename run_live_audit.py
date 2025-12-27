import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
import datetime
from cycle_engine import run_historical_cycle_upgraded
from open_mic_bridge import generate_narrative_payloads

class ArchonStandardAgent:
    version = "Archon_v1.0_Live"
    def predict(self, row):
        net_rtg_diff = row.get('NetRtg_Diff', 0.0)
        return {
            "predicted_margin": net_rtg_diff * 0.5,
            "confidence": 0.8,
            "ora_used": False,
            "signal_density": 5
        }

def fetch_yesterdays_games():
    print("⛽ Connecting to NBA API...")
    # --- FIX: Capital 'B' in ScoreBoard ---
    board = scoreboard.ScoreBoard() 
    games = board.games.get_dict()
    
    if not games:
        print("⚠️ No live games. Using Mock Data.")
        return pd.DataFrame([
            {"game_id": "MOCK_1", "matchup": "LAL vs BOS", "Actual_Margin": -12, "NetRtg_Diff": 5.0},
            {"game_id": "MOCK_2", "matchup": "NYK vs MIA", "Actual_Margin": 5, "NetRtg_Diff": 4.0}
        ])

    game_rows = []
    for game in games:
        margin = game['homeTeam']['score'] - game['awayTeam']['score']
        game_rows.append({
            "game_id": game['gameId'],
            "Actual_Margin": margin,
            "NetRtg_Diff": margin * 0.8 
        })
    print(f"⛽ Pumped {len(game_rows)} games.")
    return pd.DataFrame(game_rows)

if __name__ == "__main__":
    df = fetch_yesterdays_games()
    print("\n🔥 Firing Signal Engine...")
    agent = ArchonStandardAgent()
    run_historical_cycle_upgraded(df, agent, cycle_id="LIVE_AUDIT_001")
    print("\n🎙️ Activating Open Mic Bridge...")
    generate_narrative_payloads()
    print("\n✅ LIVE CYCLE COMPLETE.")