"""
#!/usr/bin/env python3
"""
# run_archon.py — Minimal Archon NBA prediction pipeline

# - Fetches live NBA stats and today's schedule (optional; requires `nba_api`)
# - Loads intelligence layers (archon_coach_iq.csv, archon_stadium_entropy.csv)
# - Produces archon_final_predictions.csv
# - Optionally validates predictions with a provided actual_results.csv -> archon_learning_ledger.csv

# Usage:
#     python run_archon.py --fetch
#     python run_archon.py --master path/to/archon_master_data_normalized.csv
#     python run_archon.py --master master.csv --coach archon_coach_iq.csv --stadium archon_stadium_entropy.csv
#     python run_archon.py --master master.csv --validate actual_results.csv

# Dependencies:
#     pip install pandas numpy
#     pip install nba_api   # only if you use --fetch

"""
import argparse
import os
import sys
import logging
from datetime import datetime

import pandas as pd
import numpy as np

# Optional import for live fetch
try:
    from nba_api.stats.endpoints import leaguedashteamstats, scoreboardv2
    NBA_API_AVAILABLE = True
except Exception:
    NBA_API_AVAILABLE = False

LOG = logging.getLogger("archon")
LOG.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
LOG.addHandler(handler)

# ---------- Team name normalization map (short keys) ----------
TEAM_SHORT_MAP = {
    "Atlanta Hawks": "Hawks",
    "Boston Celtics": "Celtics",
    "Brooklyn Nets": "Nets",
    "Charlotte Hornets": "Hornets",
    "Chicago Bulls": "Bulls",
    "Cleveland Cavaliers": "Cavaliers",
    "Dallas Mavericks": "Mavericks",
    "Denver Nuggets": "Nuggets",
    "Detroit Pistons": "Pistons",
    "Golden State Warriors": "Warriors",
    "Houston Rockets": "Rockets",
    "Indiana Pacers": "Pacers",
    "Los Angeles Clippers": "Clippers",
    "Los Angeles Lakers": "Lakers",
    "Memphis Grizzlies": "Grizzlies",
    "Miami Heat": "Heat",
    "Milwaukee Bucks": "Bucks",
    "Minnesota Timberwolves": "Timberwolves",
    "New Orleans Pelicans": "Pelicans",
    "New York Knicks": "Knicks",
    "Oklahoma City Thunder": "Thunder",
    "Orlando Magic": "Magic",
    "Philadelphia 76ers": "76ers",
    "Phoenix Suns": "Suns",
    "Portland Trail Blazers": "Trail Blazers",
    "Sacramento Kings": "Kings",
    "San Antonio Spurs": "Spurs",
    "Toronto Raptors": "Raptors",
    "Utah Jazz": "Jazz",
    "Washington Wizards": "Wizards"
}

# ---------- CSV filenames (defaults) ----------
DEFAULT_MASTER = "archon_master_data_normalized.csv"
DEFAULT_COACH = "archon_coach_iq.csv"
DEFAULT_STADIUM = "archon_stadium_entropy.csv"
DEFAULT_OUTPUT = "archon_final_predictions.csv"
DEFAULT_LEDGER = "archon_learning_ledger.csv"

# ---------- Functions ----------

def fetch_live_master(save_path=DEFAULT_MASTER, game_date=None):
    """
    Fetch league stats and today's schedule via nba_api and produce a normalized master CSV.
    Returns DataFrame or None if fetch failed.
    """
    if not NBA_API_AVAILABLE:
        LOG.error("nba_api is not available. Install it (pip install nba_api) or provide a master CSV.")
        return None

    date_str = (game_date or datetime.utcnow().strftime("%Y-%m-%d"))
    LOG.info(f"Fetching NBA stats and schedule for {date_str}...")

    try:
        stats = leaguedashteamstats.LeagueDashTeamStats()
        df_stats = stats.get_data_frames()[0]
    except Exception as e:
        LOG.exception("Failed to fetch league stats from nba_api: %s", e)
        return None

    # choose proxies for net rating and pace
    net_col = None
    for c in ["NET_RATING", "NETRTG", "NET_RATING", "W_PCT"]:
        if c in df_stats.columns:
            net_col = c
            break
    pace_col = None
    for c in ["PACE", "PTS"]:
        if c in df_stats.columns:
            pace_col = c
            break

    if net_col is None:
        LOG.warning("No net rating-like column found; using zeros for net proxy.")
    else:
        LOG.info("Using %s as net proxy.", net_col)
    if pace_col:
        LOG.info("Using %s as pace proxy.", pace_col)

    ratings_map = {}
    for _, r in df_stats.iterrows():
        team_id = r.get("TEAM_ID")
        team_name = r.get("TEAM_NAME")
        net_val = float(r.get(net_col)) if net_col and pd.notna(r.get(net_col)) else 0.0
        pace_val = float(r.get(pace_col)) if pace_col and pd.notna(r.get(pace_col)) else 0.0
        ratings_map[team_id] = {"TEAM_NAME": team_name, "NET_PROXY": net_val, "PACE_PROXY": pace_val}

    try:
        board = scoreboardv2.ScoreboardV2(game_date=date_str)
        games = board.get_data_frames()[0]
    except Exception as e:
        LOG.exception("Failed to fetch scoreboard: %s", e)
        return None

    rows = []
    for _, g in games.iterrows():
        home_id = g.get("HOME_TEAM_ID")
        vis_id = g.get("VISITOR_TEAM_ID")
        if home_id not in ratings_map or vis_id not in ratings_map:
            continue
        home = ratings_map[home_id]
        vis = ratings_map[vis_id]
        team_a = home["TEAM_NAME"]
        team_b = vis["TEAM_NAME"]
        net_a = home["NET_PROXY"]
        net_b = vis["NET_PROXY"]
        delta_w_final = (net_a - net_b) + 2.5  # baseline home court advantage

        rows.append({
            "Date": date_str,
            "Team_A": team_a,
            "Team_B": team_b,
            "NetRtg_A": net_a,
            "NetRtg_B": net_b,
            "Delta_W_Final": delta_w_final,
            "Venue": "Home",
            "Notes": "Live API Data"
        })

    df_live = pd.DataFrame(rows)
    if df_live.empty:
        LOG.warning("No matchups found for %s", date_str)
        return None

    # normalize keys
    df_live["Team_A_Key"] = df_live["Team_A"].map(TEAM_SHORT_MAP).fillna(df_live["Team_A"])
    df_live["Team_B_Key"] = df_live["Team_B"].map(TEAM_SHORT_MAP).fillna(df_live["Team_B"])

    df_live.to_csv(save_path, index=False)
    LOG.info("Saved master data to %s (%d matchups).", save_path, len(df_live))
    return df_live


def load_master(path=DEFAULT_MASTER):
    if not os.path.exists(path):
        LOG.error("Master file not found: %s", path)
        return None
    df = pd.read_csv(path)
    required_cols = {"Team_A_Key", "Team_B_Key", "Delta_W_Final"}
    if not required_cols.issubset(set(df.columns)):
        LOG.error("Master file %s missing required columns. Expected at least: %s", path, required_cols)
        return None
    LOG.info("Loaded master file %s (%d rows).", path, len(df))
    return df


def load_intelligence(coach_path=DEFAULT_COACH, stadium_path=DEFAULT_STADIUM):
    if os.path.exists(coach_path):
        df_coach = pd.read_csv(coach_path)
        LOG.info("Loaded coach IQ: %s (%d rows).", coach_path, len(df_coach))
    else:
        LOG.warning("Coach IQ file not found (%s). Defaulting to zero for all teams.", coach_path)
        df_coach = pd.DataFrame(columns=["Team", "EVA_Scalar"])

    if os.path.exists(stadium_path):
        df_stadium = pd.read_csv(stadium_path)
        LOG.info("Loaded stadium entropy: %s (%d rows).", stadium_path, len(df_stadium))
    else:
        LOG.warning("Stadium entropy file not found (%s). Defaulting to zero for all teams.", stadium_path)
        df_stadium = pd.DataFrame(columns=["Team", "Entropy_Alpha"])

    return df_coach, df_stadium


def run_engine(df_master, df_coach, df_stadium, output_path=DEFAULT_OUTPUT):
    results = []
    for _, row in df_master.iterrows():
        team_a = row["Team_A_Key"]
        team_b = row["Team_B_Key"]
        base_spread = float(row["Delta_W_Final"])

        # Coaching IQ lookup
        try:
            c_a = float(df_coach.loc[df_coach["Team"] == team_a, "EVA_Scalar"].values[0])
        except Exception:
            c_a = 0.0
        try:
            c_b = float(df_coach.loc[df_coach["Team"] == team_b, "EVA_Scalar"].values[0])
        except Exception:
            c_b = 0.0
        coaching_adj = (c_a - c_b) * 3.0

        # Stadium entropy lookup (home team = Team_A)
        try:
            ent_a = float(df_stadium.loc[df_stadium["Team"] == team_a, "Entropy_Alpha"].values[0])
        except Exception:
            ent_a = 0.0
        entropy_adj = ent_a * -1.5

        final_spread = base_spread + coaching_adj + entropy_adj
        winner = team_a if final_spread > 0 else team_b
        margin = abs(final_spread)
        confidence = "High" if margin > 3.0 else "Volatile"

        results.append({
            "Matchup": f"{team_a} vs {team_b}",
            "Archon_Spread": round(final_spread, 2),
            "Base_Model": round(base_spread, 2),
            "Coaching_Adj": round(coaching_adj, 2),
            "Entropy_Adj": round(entropy_adj, 2),
            "Winner_Pick": winner,
            "Win_Margin": round(margin, 1),
            "Confidence": confidence
        })

    df_out = pd.DataFrame(results)
    df_out.to_csv(output_path, index=False)
    LOG.info("Saved predictions to %s (%d rows).", output_path, len(df_out))
    return df_out


def validate_predictions(pred_path=DEFAULT_OUTPUT, actuals_path=None, ledger_path=DEFAULT_LEDGER):
    if not os.path.exists(pred_path):
        LOG.error("Predictions file not found: %s", pred_path)
        return None
    if not actuals_path or not os.path.exists(actuals_path):
        LOG.error("Actual results file not found: %s", actuals_path)
        return None

    df_preds = pd.read_csv(pred_path)
    df_act = pd.read_csv(actuals_path)
    ledger = []
    for _, p in df_preds.iterrows():
        matchup = p["Matchup"]
        pred = float(p["Archon_Spread"])
        act_row = df_act.loc[df_act["Matchup"] == matchup]
        if act_row.empty:
            continue
        actual = float(act_row["Actual_Spread"].values[0])
        error = abs(pred - actual)
        recalibration = "None"
        note = "Model stable."
        if error > 3.0:
            note = "High deviation."
            if abs(p.get("Coaching_Adj", 0)) > 0.5:
                recalibration = "Decay Coaching weight by 5%"
            else:
                recalibration = "Increase Entropy alpha by 10%"

        ledger.append({
            "Matchup": matchup,
            "Predicted": pred,
            "Actual": actual,
            "Error_Margin": round(error, 2),
            "Audit_Status": note,
            "Recalibration": recalibration
        })
    df_ledger = pd.DataFrame(ledger)
    df_ledger.to_csv(ledger_path, index=False)
    LOG.info("Saved learning ledger to %s (%d rows).", ledger_path, len(df_ledger))
    return df_ledger

# ---------- CLI ----------
def main(argv=None):
    parser = argparse.ArgumentParser(description="Archon NBA prediction pipeline")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fetch", action="store_true", help="Fetch live NBA master data (requires nba_api)")
    group.add_argument("--master", type=str, help=f"Path to existing master CSV (default: {DEFAULT_MASTER})")
    parser.add_argument("--date", type=str, help="Date for scoreboard fetch (YYYY-MM-DD). Defaults to today (UTC).")
    parser.add_argument("--coach", type=str, default=DEFAULT_COACH, help=f"Coach IQ CSV (default: {DEFAULT_COACH})")
    parser.add_argument("--stadium", type=str, default=DEFAULT_STADIUM, help=f"Stadium entropy CSV (default: {DEFAULT_STADIUM})")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT, help=f"Output predictions CSV (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--validate", type=str, metavar="ACTUALS_CSV", help="Path to actual_results.csv to run validation and produce a ledger")
    args = parser.parse_args(argv)

    if args.fetch:
        df_master = fetch_live_master(save_path=DEFAULT_MASTER, game_date=args.date)
        if df_master is None:
            LOG.error("Failed to fetch master data. Exiting.")
            sys.exit(2)
    else:
        df_master = load_master(args.master)
        if df_master is None:
            LOG.error("Failed to load master file. Exiting.")
            sys.exit(2)

    df_coach, df_stadium = load_intelligence(args.coach, args.stadium)
    df_preds = run_engine(df_master, df_coach, df_stadium, output_path=args.output)
    print("\n--- Predictions Preview ---")
    print(df_preds.head(10).to_string(index=False))

    if args.validate:
        df_ledger = validate_predictions(pred_path=args.output, actuals_path=args.validate)
        if df_ledger is not None:
            print("\n--- Learning Ledger Preview ---")
            print(df_ledger.head(20).to_string(index=False))

if __name__ == "__main__":
    main()
