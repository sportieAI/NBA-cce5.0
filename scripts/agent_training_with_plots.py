#!/usr/bin/env python3
"""
Agent training script with plotting, early stopping, and ledger creation.
Saves training ledger (CSV), parameter trajectory (numpy .npz), model checkpoint, and plots.

Usage:
    python -m scripts.agent_training_with_plots --epochs 100 --batch-size 64 --lr 1e-3

This script is intentionally self-contained and uses a toy dataset if no dataloader is provided.
"""

from __future__ import annotations

import argparse
import logging
import os
import random
from typing import List, Dict

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Import plotting helpers from our sibling script
try:
    from scripts.plot_param_trajectories import plot_trajectories, plot_loss_from_ledger
except Exception:
    # If run as a script from the same directory, allow direct import
    from plot_param_trajectories import plot_trajectories, plot_loss_from_ledger


LOG = logging.getLogger(__name__)


class SimpleAgent(nn.Module):
    """A small MLP to act as a placeholder agent model.

    Structure: input -> hidden -> hidden -> output
    """

    def __init__(self, input_dim: int = 20, hidden: int = 64, output_dim: int = 1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def make_toy_dataloaders(batch_size: int, input_dim: int = 20):
    # Simple regression toy data
    N_train = 2000
    N_val = 500
    X_train = np.random.randn(N_train, input_dim).astype(np.float32)
    w = np.random.randn(input_dim, 1).astype(np.float32)
    y_train = X_train.dot(w) + 0.1 * np.random.randn(N_train, 1).astype(np.float32)

    X_val = np.random.randn(N_val, input_dim).astype(np.float32)
    y_val = X_val.dot(w) + 0.1 * np.random.randn(N_val, 1).astype(np.float32)

    train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
    val_ds = TensorDataset(torch.from_numpy(X_val), torch.from_numpy(y_val))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader


def evaluate(model: nn.Module, dataloader: DataLoader, device: torch.device) -> float:
    model.eval()
    loss_fn = nn.MSELoss()
    total = 0.0
    n = 0
    with torch.no_grad():
        for xb, yb in dataloader:
            xb = xb.to(device)
            yb = yb.to(device)
            out = model(xb)
            loss = loss_fn(out, yb)
            batch_size = xb.shape[0]
            total += loss.item() * batch_size
            n += batch_size
    return total / max(1, n)


def train(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    device: torch.device,
    epochs: int,
    lr: float,
    early_stop_patience: int,
    save_dir: str,
    record_params_every: int = 1,
):
    os.makedirs(save_dir, exist_ok=True)

    model = model.to(device)
    opt = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    best_val = float("inf")
    best_epoch = -1
    stale = 0

    ledger_rows: List[Dict] = []

    # We'll store parameter trajectories as a dict: param_name -> list of flattened arrays over epochs
    param_trajectories: Dict[str, List[np.ndarray]] = {}
    param_names: List[str] = []

    # Initialize param names
    for name, p in model.named_parameters():
        param_names.append(name)
        param_trajectories[name] = []

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        n_samples = 0
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            opt.zero_grad()
            out = model(xb)
            loss = loss_fn(out, yb)
            loss.backward()
            opt.step()
            batch_size = xb.shape[0]
            epoch_loss += loss.item() * batch_size
            n_samples += batch_size
        train_loss = epoch_loss / max(1, n_samples)

        val_loss = evaluate(model, val_loader, device)

        LOG.info(f"Epoch {epoch:03d} | train_loss={train_loss:.6f} val_loss={val_loss:.6f}")

        # Record ledger row
        row = {
            "epoch": epoch,
            "train_loss": float(train_loss),
            "val_loss": float(val_loss),
        }
        ledger_rows.append(row)

        # Record parameters (flattened) every N epochs
        if (epoch - 1) % record_params_every == 0:
            for name, p in model.named_parameters():
                param_trajectories[name].append(p.detach().cpu().numpy().ravel().copy())

        # Check early stopping
        if val_loss < best_val - 1e-12:
            best_val = val_loss
            best_epoch = epoch
            stale = 0
            # save best model
            best_path = os.path.join(save_dir, "best_model.pth")
            torch.save(model.state_dict(), best_path)
        else:
            stale += 1

        if stale >= early_stop_patience:
            LOG.info("Early stopping triggered (patience=%d)." % early_stop_patience)
            break

    # After training save final model
    final_path = os.path.join(save_dir, "final_model.pth")
    torch.save(model.state_dict(), final_path)

    # Save ledger
    ledger_df = pd.DataFrame(ledger_rows)
    ledger_csv = os.path.join(save_dir, "training_ledger.csv")
    ledger_df.to_csv(ledger_csv, index=False)

    # Save parameter trajectories as npz (each param is an array epochs x param_size)
    param_arrays = {}
    for name in param_names:
        if len(param_trajectories[name]) == 0:
            param_arrays[name] = np.zeros((0,))
        else:
            param_arrays[name] = np.vstack(param_trajectories[name])
    traj_path = os.path.join(save_dir, "param_trajectories.npz")
    np.savez_compressed(traj_path, **param_arrays)

    LOG.info(f"Saved ledger to {ledger_csv} and param trajectories to {traj_path}")

    # Create plots
    try:
        plot_loss_from_ledger(ledger_csv, os.path.join(save_dir, "loss_curve.png"))
        # For trajectories, pick top-k smallest parameters (by size) to visualize or first few
        # We'll visualize up to 6 parameter vectors merged into a single plot by taking one element from each param's flattened vector
        plot_trajectories(traj_path, os.path.join(save_dir, "param_trajectories.png"))
    except Exception as e:
        LOG.exception("Plotting failed: %s", e)

    return {
        "ledger_csv": ledger_csv,
        "traj_path": traj_path,
        "best_model": best_path if best_epoch >= 0 else None,
        "final_model": final_path,
    }


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--early-stop-patience", type=int, default=10)
    p.add_argument("--save-dir", type=str, default="runs/agent_training")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--record-params-every", type=int, default=1)
    p.add_argument("--device", type=str, default=None)
    return p.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    set_seed(args.seed)

    device = torch.device(args.device if args.device is not None else ("cuda" if torch.cuda.is_available() else "cpu"))

    train_loader, val_loader = make_toy_dataloaders(args.batch_size)

    model = SimpleAgent(input_dim=20, hidden=128, output_dim=1)

    out = train(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        epochs=args.epochs,
        lr=args.lr,
        early_stop_patience=args.early_stop_patience,
        save_dir=args.save_dir,
        record_params_every=args.record_params_every,
    )

    LOG.info("Training finished. Artifacts: %s", out)


if __name__ == "__main__":
    main()
