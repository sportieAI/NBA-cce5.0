"""
#!/usr/bin/env python3
"""
# agent_training_grad_es.py — Archon gradient agent with early stopping (validation set)

# Adds early-stopping to the gradient-based training loop:
# - Monitor validation loss (MSE) computed on matchups found in the master + validation actuals.
# - Stop training when validation loss hasn't improved by `min_delta` for `patience` consecutive epochs.
# - Saves the best-found per-team parameters and global params and restores them before final save (if --restore-best).

# Usage (train with early stopping):
#   python agent_training_grad_es.py train --master archon_master_data_normalized.csv \
#     --coach archon_coach_iq.csv --stadium archon_stadium_entropy.csv \
#     --actuals train_actuals.csv --val val_actuals.csv --epochs 50 \
#     --lr-coach 0.05 --lr-entropy 0.02 --online --patience 5 --min-delta 1e-3

# Notes:
# - Validation actuals CSV must have columns: Matchup,Actual_Spread
# - Master CSV must contain Team_A_Key, Team_B_Key, Delta_W_Final
# - The script overwrites coach & stadium CSVs with the best parameters (unless you change the save paths)

from __future__ import annotations
import argparse
import logging
import os
import sys
from copy import deepcopy
from datetime import datetime
from typing import Dict, Optional, Tuple

import pandas as pd
import numpy as np

LOG = logging.getLogger("archon_agent_grad_es")
LOG.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
LOG.addHandler(ch)


# ---------- I/O helpers ----------
def load_master(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Master CSV not found: {path}")
    df = pd.read_csv(path)
    required = {"Team_A_Key", "Team_B_Key", "Delta_W_Final"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"Master CSV missing required columns, expected at least: {required}")
    return df.copy()


def load_coach(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "Team" not in df.columns or "EVA_Scalar" not in df.columns:
            raise ValueError("Coach CSV must contain columns: Team,EVA_Scalar")
        return df.copy()
    else:
        LOG.warning("Coach CSV not found (%s). Creating empty coach frame.", path)
        return pd.DataFrame(columns=["Team", "EVA_Scalar"])


def load_stadium(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        df = pd.read_csv(path)
        if "Team" not in df.columns or "Entropy_Alpha" not in df.columns:
            raise ValueError("Stadium CSV must contain columns: Team,Entropy_Alpha")
        return df.copy()
    else:
        LOG.warning("Stadium CSV not found (%s). Creating empty stadium frame.", path)
        return pd.DataFrame(columns=["Team", "Entropy_Alpha"])


def ensure_team_in_df(df: pd.DataFrame, team: str, col: str, default: float = 0.0) -> pd.DataFrame:
    """Ensure there is a row for team in df with column col. Return possibly modified df (copy)."""
    if team not in df["Team"].values:
        df = pd.concat([df, pd.DataFrame([{"Team": team, col: default}])], ignore_index=True)
    return df


def get_team_value(df: pd.DataFrame, team: str, col: str, default: float = 0.0) -> float:
    vals = df.loc[df["Team"] == team, col].values
    if len(vals) == 0 or pd.isna(vals[0]):
        return float(default)
    return float(vals[0])


def set_team_value(df: pd.DataFrame, team: str, col: str, value: float) -> None:
    idx = df.index[df["Team"] == team].tolist()
    if len(idx) == 0:
        # append
        df.loc[len(df)] = { "Team": team, col: value }
    else:
        df.at[idx[0], col] = value


# ---------- Agent with gradient updates ----------
class GradArchonAgent:
    def __init__(self,
                 coach_df: pd.DataFrame,
                 stadium_df: pd.DataFrame,
                 coach_weight: float = 3.0,
                 entropy_multiplier: float = -1.5,
                 home_court_adv: float = 2.5,
                 clip_coach: Tuple[float, float] = (-5.0, 5.0),
                 clip_entropy: Tuple[float, float] = (-5.0, 5.0),
                 clip_global: Tuple[float, float] = (-10.0, 10.0)):
        # Keep mutable dataframes
        self.coach_df = coach_df.copy().reset_index(drop=True)
        self.stadium_df = stadium_df.copy().reset_index(drop=True)
        self.coach_weight = float(coach_weight)
        self.entropy_multiplier = float(entropy_multiplier)
        self.home_court_adv = float(home_court_adv)

        # clipping ranges to keep parameters stable
        self.clip_coach = clip_coach
        self.clip_entropy = clip_entropy
        self.clip_global = clip_global

    def predict_single(self, team_a: str, team_b: str, base_spread: float) -> Tuple[float, float, float]:
        """Return (pred, coaching_adj, entropy_adj)"""
        # ensure teams exist (so we can update later)
        self.coach_df = ensure_team_in_df(self.coach_df, team_a, "EVA_Scalar", default=0.0)
        self.coach_df = ensure_team_in_df(self.coach_df, team_b, "EVA_Scalar", default=0.0)
        self.stadium_df = ensure_team_in_df(self.stadium_df, team_a, "Entropy_Alpha", default=0.0)

        c_a = get_team_value(self.coach_df, team_a, "EVA_Scalar", 0.0)
        c_b = get_team_value(self.coach_df, team_b, "EVA_Scalar", 0.0)
        ent_a = get_team_value(self.stadium_df, team_a, "Entropy_Alpha", 0.0)

        coaching_adj = (c_a - c_b) * self.coach_weight
        entropy_adj = ent_a * self.entropy_multiplier
        pred = base_spread + coaching_adj + entropy_adj
        return float(pred), float(coaching_adj), float(entropy_adj)

    def predict_df(self, df_master: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, r in df_master.iterrows():
            team_a = r["Team_A_Key"]
            team_b = r["Team_B_Key"]
            base = float(r["Delta_W_Final"])
            pred, coaching_adj, entropy_adj = self.predict_single(team_a, team_b, base)
            rows.append({
                "Matchup": f"{team_a} vs {team_b}",
                "Team_A": team_a,
                "Team_B": team_b,
                "Base_Model": round(base, 6),
                "Coaching_Adj": round(coaching_adj, 6),
                "Entropy_Adj": round(entropy_adj, 6),
                "Archon_Spread": round(pred, 6)
            })
        return pd.DataFrame(rows)

    def apply_gradients(self,
                        team_a: str,
                        team_b: str,
                        base_spread: float,
                        pred: float,
                        actual: float,
                        lr_coach: float = 0.01,
                        lr_entropy: float = 0.01,
                        lr_global: float = 0.001,
                        update_global: bool = False,
                        regularization: Optional[float] = None) -> Dict:
        """
        Compute gradients for squared error L = 0.5*(pred - actual)^2 and perform SGD updates.

        Model: pred = base + coach_weight*(c_a - c_b) + entropy_multiplier*ent_a
        """
        # ensure existence
        self.coach_df = ensure_team_in_df(self.coach_df, team_a, "EVA_Scalar", 0.0)
        self.coach_df = ensure_team_in_df(self.coach_df, team_b, "EVA_Scalar", 0.0)
        self.stadium_df = ensure_team_in_df(self.stadium_df, team_a, "Entropy_Alpha", 0.0)

        c_a = get_team_value(self.coach_df, team_a, "EVA_Scalar", 0.0)
        c_b = get_team_value(self.coach_df, team_b, "EVA_Scalar", 0.0)
        ent_a = get_team_value(self.stadium_df, team_a, "Entropy_Alpha", 0.0)

        dL_dpred = (pred - actual)  # derivative of 0.5*(pred-actual)^2 is (pred-actual)
        # Parameter gradients
        grad_c_a = dL_dpred * self.coach_weight
        grad_c_b = dL_dpred * (-self.coach_weight)
        grad_ent_a = dL_dpred * self.entropy_multiplier
        grad_coach_weight = dL_dpred * (c_a - c_b)
        grad_entropy_mult = dL_dpred * ent_a

        # Apply updates
        new_c_a = c_a - lr_coach * grad_c_a
        new_c_b = c_b - lr_coach * grad_c_b
        new_ent_a = ent_a - lr_entropy * grad_ent_a

        # Optional regularization (L2) applied to per-team params after update
        if regularization:
            new_c_a = new_c_a * (1.0 - lr_coach * regularization)
            new_c_b = new_c_b * (1.0 - lr_coach * regularization)
            new_ent_a = new_ent_a * (1.0 - lr_entropy * regularization)

        # Clip per-team params
        new_c_a = float(np.clip(new_c_a, self.clip_coach[0], self.clip_coach[1]))
        new_c_b = float(np.clip(new_c_b, self.clip_coach[0], self.clip_coach[1]))
        new_ent_a = float(np.clip(new_ent_a, self.clip_entropy[0], self.clip_entropy[1]))

        set_team_value(self.coach_df, team_a, "EVA_Scalar", new_c_a)
        set_team_value(self.coach_df, team_b, "EVA_Scalar", new_c_b)
        set_team_value(self.stadium_df, team_a, "Entropy_Alpha", new_ent_a)

        global_updates = {}
        if update_global:
            old_cw = self.coach_weight
            old_em = self.entropy_multiplier
            self.coach_weight = float(np.clip(self.coach_weight - lr_global * grad_coach_weight, self.clip_global[0], self.clip_global[1]))
            self.entropy_multiplier = float(np.clip(self.entropy_multiplier - lr_global * grad_entropy_mult, self.clip_global[0], self.clip_global[1]))
            global_updates = {"old_coach_weight": old_cw, "new_coach_weight": self.coach_weight,
                              "old_entropy_multiplier": old_em, "new_entropy_multiplier": self.entropy_multiplier}

        # Return diagnostics for ledger
        return {
            "pred": float(pred),
            "actual": float(actual),
            "error": float(abs(pred - actual)),
            "grad_c_a": float(grad_c_a),
            "grad_c_b": float(grad_c_b),
            "grad_ent_a": float(grad_ent_a),
            "updated_c_a": new_c_a,
            "updated_c_b": new_c_b,
            "updated_ent_a": new_ent_a,
            **global_updates
        }

    def save_intel(self, coach_path: str, stadium_path: str) -> None:
        # Save dataframes (ensure columns are correct order)
        if "Team" not in self.coach_df.columns or "EVA_Scalar" not in self.coach_df.columns:
            # reorder/rename if needed
            self.coach_df = self.coach_df.rename(columns={self.coach_df.columns[0]: "Team"})
        if "Team" not in self.stadium_df.columns or "Entropy_Alpha" not in self.stadium_df.columns:
            self.stadium_df = self.stadium_df.rename(columns={self.stadium_df.columns[0]: "Team"})
        self.coach_df.to_csv(coach_path, index=False)
        self.stadium_df.to_csv(stadium_path, index=False)
        LOG.info("Saved coach intelligence -> %s (%d rows)", coach_path, len(self.coach_df))
        LOG.info("Saved stadium intelligence -> %s (%d rows)", stadium_path, len(self.stadium_df))


# ---------- Validation & training loop (with early stopping) ----------
def compute_validation_loss(agent: GradArchonAgent, df_master: pd.DataFrame, df_val_actuals: pd.DataFrame) -> Optional[float]:
    """
    Compute mean squared error on validation set using matchups found in master + validation actuals.
    Returns MSE or None if no overlapping matchups.
    """
    # build a map of actuals
    val_map = {r["Matchup"]: float(r["Actual_Spread"]) for _, r in df_val_actuals.iterrows()}
    errors = []
    for _, r in df_master.iterrows():
        matchup = f"{r['Team_A_Key']} vs {r['Team_B_Key']}"
        if matchup not in val_map:
            continue
        base = float(r["Delta_W_Final"])
        pred, _, _ = agent.predict_single(r["Team_A_Key"], r["Team_B_Key"], base)
        err = (pred - val_map[matchup]) ** 2
        errors.append(err)
    if len(errors) == 0:
        return None
    return float(np.mean(errors))


def training_loop_grad_es(agent: GradArchonAgent,
                          df_master: pd.DataFrame,
                          df_actuals: pd.DataFrame,
                          df_val_actuals: Optional[pd.DataFrame] = None,
                          epochs: int = 1,
                          lr_coach: float = 0.01,
                          lr_entropy: float = 0.01,
                          lr_global: float = 0.001,
                          update_global: bool = False,
                          online: bool = True,
                          regularization: Optional[float] = None,
                          ledger_path: str = "archon_learning_ledger_grad.csv",
                          patience: int = 5,
                          min_delta: float = 1e-4,
                          restore_best: bool = True) -> pd.DataFrame:
    """
    Train with gradient updates and early stopping on validation set.

    If df_val_actuals is provided, early-stopping monitors validation MSE.
    """
    actual_map = {r["Matchup"]: float(r["Actual_Spread"]) for _, r in df_actuals.iterrows()}
    ledger_rows = []

    best_val_loss = np.inf
    best_state = None
    wait = 0

    for ep in range(epochs):
        LOG.info("Epoch %d/%d start", ep + 1, epochs)
        # shuffle for SGD
        master_shuffled = df_master.sample(frac=1.0, random_state=np.random.randint(0, 2**31)).reset_index(drop=True)

        # For batch accumulation
        accum_coach_grads: Dict[str, float] = {}
        accum_entropy_grads: Dict[str, float] = {}
        accum_global_grad_coach_weight = 0.0
        accum_global_grad_entropy_mult = 0.0
        accum_count = 0

        for _, r in master_shuffled.iterrows():
            team_a = r["Team_A_Key"]
            team_b = r["Team_B_Key"]
            base = float(r["Delta_W_Final"])
            matchup = f"{team_a} vs {team_b}"

            if matchup not in actual_map:
                ledger_rows.append({
                    "epoch": ep + 1,
                    "timestamp": datetime.utcnow().isoformat(),
                    "Matchup": matchup,
                    "Predicted": None,
                    "Actual": None,
                    "Error": None,
                    "UpdateMode": "no_actual"
                })
                continue

            actual = actual_map[matchup]
            pred, coaching_adj, entropy_adj = agent.predict_single(team_a, team_b, base)

            if online:
                diag = agent.apply_gradients(team_a, team_b, base, pred, actual,
                                             lr_coach=lr_coach, lr_entropy=lr_entropy,
                                             lr_global=lr_global, update_global=update_global,
                                             regularization=regularization)
                ledger_rows.append({
                    "epoch": ep + 1,
                    "timestamp": datetime.utcnow().isoformat(),
                    "Matchup": matchup,
                    "Predicted": diag["pred"],
                    "Actual": diag["actual"],
                    "Error": diag["error"],
                    "grad_c_a": diag["grad_c_a"],
                    "grad_c_b": diag["grad_c_b"],
                    "grad_ent_a": diag["grad_ent_a"],
                    "updated_c_a": diag["updated_c_a"],
                    "updated_c_b": diag["updated_c_b"],
                    "updated_ent_a": diag["updated_ent_a"],
                    "coach_weight": agent.coach_weight,
                    "entropy_multiplier": agent.entropy_multiplier,
                })
            else:
                # accumulate grads for batch update
                dL_dpred = (pred - actual)
                agent.coach_df = ensure_team_in_df(agent.coach_df, team_a, "EVA_Scalar", 0.0)
                agent.coach_df = ensure_team_in_df(agent.coach_df, team_b, "EVA_Scalar", 0.0)
                agent.stadium_df = ensure_team_in_df(agent.stadium_df, team_a, "Entropy_Alpha", 0.0)

                c_a = get_team_value(agent.coach_df, team_a, "EVA_Scalar", 0.0)
                c_b = get_team_value(agent.coach_df, team_b, "EVA_Scalar", 0.0)
                ent_a = get_team_value(agent.stadium_df, team_a, "Entropy_Alpha", 0.0)

                grad_c_a = dL_dpred * agent.coach_weight
                grad_c_b = dL_dpred * (-agent.coach_weight)
                grad_ent_a = dL_dpred * agent.entropy_multiplier
                grad_coach_weight = dL_dpred * (c_a - c_b)
                grad_entropy_mult = dL_dpred * ent_a

                accum_coach_grads[team_a] = accum_coach_grads.get(team_a, 0.0) + grad_c_a
                accum_coach_grads[team_b] = accum_coach_grads.get(team_b, 0.0) + grad_c_b
                accum_entropy_grads[team_a] = accum_entropy_grads.get(team_a, 0.0) + grad_ent_a
                accum_global_grad_coach_weight += grad_coach_weight
                accum_global_grad_entropy_mult += grad_entropy_mult
                accum_count += 1

                ledger_rows.append({
                    "epoch": ep + 1,
                    "timestamp": datetime.utcnow().isoformat(),
                    "Matchup": matchup,
                    "Predicted": float(pred),
                    "Actual": float(actual),
                    "Error": float(abs(pred - actual)),
                    "UpdateMode": "batch_pending"
                })

        # If batch, apply accumulated gradients now
        if not online and accum_count > 0:
            for team, g in accum_coach_grads.items():
                old = get_team_value(agent.coach_df, team, "EVA_Scalar", 0.0)
                new = old - lr_coach * (g / accum_count)
                # optional regularization
                if regularization:
                    new = new * (1.0 - lr_coach * regularization)
                new = float(np.clip(new, agent.clip_coach[0], agent.clip_coach[1]))
                set_team_value(agent.coach_df, team, "EVA_Scalar", new)
                LOG.debug("Batch update coach %s: %f -> %f", team, old, new)

            for team, g in accum_entropy_grads.items():
                old = get_team_value(agent.stadium_df, team, "Entropy_Alpha", 0.0)
                new = old - lr_entropy * (g / accum_count)
                if regularization:
                    new = new * (1.0 - lr_entropy * regularization)
                new = float(np.clip(new, agent.clip_entropy[0], agent.clip_entropy[1]))
                set_team_value(agent.stadium_df, team, "Entropy_Alpha", new)
                LOG.debug("Batch update entropy %s: %f -> %f", team, old, new)

            if update_global:
                old_cw = agent.coach_weight
                old_em = agent.entropy_multiplier
                agent.coach_weight = float(np.clip(agent.coach_weight - lr_global * (accum_global_grad_coach_weight / max(accum_count, 1)), agent.clip_global[0], agent.clip_global[1]))
                agent.entropy_multiplier = float(np.clip(agent.entropy_multiplier - lr_global * (accum_global_grad_entropy_mult / max(accum_count, 1)), agent.clip_global[0], agent.clip_global[1]))
                LOG.debug("Batch update global: coach_weight %f -> %f, entropy_multiplier %f -> %f", old_cw, agent.coach_weight, old_em, agent.entropy_multiplier)

        LOG.info("Epoch %d complete: coach_weight=%.6f entropy_multiplier=%.6f", ep + 1, agent.coach_weight, agent.entropy_multiplier)

        # After epoch: compute validation loss if provided
        val_loss = None
        if df_val_actuals is not None:
            val_loss = compute_validation_loss(agent, df_master, df_val_actuals)
            if val_loss is None:
                LOG.warning("No overlapping matchups between master and validation actuals; early stopping not possible this epoch.")
            else:
                LOG.info("Epoch %d validation MSE: %.6f", ep + 1, val_loss)

                # Early stopping logic
                if val_loss + min_delta < best_val_loss:
                    # improvement
                    best_val_loss = val_loss
                    best_state = {
                        "coach_df": deepcopy(agent.coach_df),
                        "stadium_df": deepcopy(agent.stadium_df),
                        "coach_weight": agent.coach_weight,
                        "entropy_multiplier": agent.entropy_multiplier,
                        "epoch": ep + 1,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    wait = 0
                    LOG.info("Validation improved (%.6f). Saved best state (epoch %d).", val_loss, ep + 1)
                else:
                    wait += 1
                    LOG.info("No significant improvement (wait=%d/%d).", wait, patience)
                    if wait >= patience:
                        LOG.info("Early stopping triggered at epoch %d (no improvement for %d epochs).", ep + 1, patience)
                        # Optionally restore best state
                        if restore_best and best_state is not None:
                            LOG.info("Restoring best state from epoch %d.", best_state["epoch"])
                            agent.coach_df = deepcopy(best_state["coach_df"])
                            agent.stadium_df = deepcopy(best_state["stadium_df"])
                            agent.coach_weight = best_state["coach_weight"]
                            agent.entropy_multiplier = best_state["entropy_multiplier"]
                        # Save ledger and return
                        df_ledger = pd.DataFrame(ledger_rows)
                        df_ledger.to_csv(ledger_path, index=False)
                        LOG.info("Saved training ledger to %s (%d rows)", ledger_path, len(df_ledger))
                        return df_ledger

    # Training finished normally; if restore_best requested and best_state exists, restore
    if restore_best and best_state is not None:
        LOG.info("Training finished. Restoring best state from epoch %d.", best_state["epoch"])
        agent.coach_df = deepcopy(best_state["coach_df"])
        agent.stadium_df = deepcopy(best_state["stadium_df"])
        agent.coach_weight = best_state["coach_weight"]
        agent.entropy_multiplier = best_state["entropy_multiplier"]

    df_ledger = pd.DataFrame(ledger_rows)
    df_ledger.to_csv(ledger_path, index=False)
    LOG.info("Saved training ledger to %s (%d rows)", ledger_path, len(df_ledger))
    return df_ledger


# ---------- CLI ----------
def main(argv=None):
    parser = argparse.ArgumentParser(description="Archon gradient agent CLI with early stopping")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_pred = sub.add_parser("predict", help="Predict spreads from master + intelligence CSVs")
    p_pred.add_argument("--master", required=True, help="Master CSV (Team_A_Key,Team_B_Key,Delta_W_Final)")
    p_pred.add_argument("--coach", default="archon_coach_iq.csv", help="Coach CSV (Team,EVA_Scalar)")
    p_pred.add_argument("--stadium", default="archon_stadium_entropy.csv", help="Stadium CSV (Team,Entropy_Alpha)")
    p_pred.add_argument("--output", default="archon_final_predictions.csv", help="Output predictions CSV")

    p_train = sub.add_parser("train", help="Train with gradient updates using actuals and optional validation")
    p_train.add_argument("--master", required=True, help="Master CSV")
    p_train.add_argument("--coach", default="archon_coach_iq.csv", help="Coach CSV (Team,EVA_Scalar)")
    p_train.add_argument("--stadium", default="archon_stadium_entropy.csv", help="Stadium CSV (Team,Entropy_Alpha)")
    p_train.add_argument("--actuals", required=True, help="Training actuals CSV (Matchup,Actual_Spread)")
    p_train.add_argument("--val", required=False, help="Validation actuals CSV (Matchup,Actual_Spread) for early stopping")
    p_train.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    p_train.add_argument("--lr-coach", type=float, default=0.05, help="Learning rate for coach EVA_Scalar updates")
    p_train.add_argument("--lr-entropy", type=float, default=0.02, help="Learning rate for entropy alpha updates")
    p_train.add_argument("--lr-global", type=float, default=0.001, help="Learning rate for global params (coach_weight, entropy_multiplier)")
    p_train.add_argument("--update-global", action="store_true", help="Enable updates for global params")
    p_train.add_argument("--online", action="store_true", help="Apply updates online per-match (default: batch if not set)")
    p_train.add_argument("--regularization", type=float, default=0.0, help="L2 regularization coefficient (optional)")
    p_train.add_argument("--ledger", default="archon_learning_ledger_grad_es.csv", help="Training ledger CSV output path")
    p_train.add_argument("--save-coach", default="archon_coach_iq.csv", help="Path to save updated coach CSV (overwrites)")
    p_train.add_argument("--save-stadium", default="archon_stadium_entropy.csv", help="Path to save updated stadium CSV (overwrites)")
    p_train.add_argument("--patience", type=int, default=5, help="Early stopping patience (epochs)")
    p_train.add_argument("--min-delta", type=float, default=1e-4, help="Minimum validation loss improvement to reset patience")
    p_train.add_argument("--restore-best", action="store_true", help="Restore best parameters found on validation before saving")

    args = parser.parse_args(argv)

    if args.cmd == "predict":
        df_master = load_master(args.master)
        df_coach = load_coach(args.coach)
        df_stadium = load_stadium(args.stadium)
        agent = GradArchonAgent(df_coach, df_stadium)
        df_preds = agent.predict_df(df_master)
        df_preds.to_csv(args.output, index=False)
        LOG.info("Saved predictions to %s (%d rows)", args.output, len(df_preds))
        print(df_preds.head(20).to_string(index=False))

    elif args.cmd == "train":
        df_master = load_master(args.master)
        df_coach = load_coach(args.coach)
        df_stadium = load_stadium(args.stadium)
        df_actuals = pd.read_csv(args.actuals)
        if "Matchup" not in df_actuals.columns or "Actual_Spread" not in df_actuals.columns:
            raise ValueError("Training actuals CSV must contain 'Matchup' and 'Actual_Spread' columns")

        df_val_actuals = None
        if args.val:
            if not os.path.exists(args.val):
                raise FileNotFoundError(f"Validation actuals file not found: {args.val}")
            df_val_actuals = pd.read_csv(args.val)
            if "Matchup" not in df_val_actuals.columns or "Actual_Spread" not in df_val_actuals.columns:
                raise ValueError("Validation actuals CSV must contain 'Matchup' and 'Actual_Spread' columns")

        agent = GradArchonAgent(df_coach, df_stadium)
        df_ledger = training_loop_grad_es(agent, df_master, df_actuals,
                                         df_val_actuals=df_val_actuals,
                                         epochs=args.epochs,
                                         lr_coach=args.lr_coach,
                                         lr_entropy=args.lr_entropy,
                                         lr_global=args.lr_global,
                                         update_global=args.update_global,
                                         online=args.online,
                                         regularization=(args.regularization if args.regularization > 0 else None),
                                         ledger_path=args.ledger,
                                         patience=args.patience,
                                         min_delta=args.min_delta,
                                         restore_best=args.restore_best)
        # Save new intelligence (best restored if requested)
        agent.save_intel(args.save_coach, args.save_stadium)
        print(df_ledger.head(50).to_string(index=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
