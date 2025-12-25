#!/usr/bin/env python3
"""
Plotting helpers for parameter trajectories and loss curves.

This module provides functions to create readable plots using matplotlib + seaborn.

Functions:
    - plot_trajectories(npz_path, save_path, top_k=6) -> saves an image with multiple parameter trajectories
    - plot_loss_from_ledger(ledger_csv, save_path) -> plots train/val loss curves

The trajectory plot will take the first few dimensions from the saved parameter vectors to visualize trends.
"""

from __future__ import annotations

import argparse
import os
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set(style="whitegrid")


def plot_loss_from_ledger(ledger_csv: str, save_path: str, figsize=(8, 5)) -> None:
    if not os.path.exists(ledger_csv):
        raise FileNotFoundError(f"Ledger not found: {ledger_csv}")
    df = pd.read_csv(ledger_csv)
    if df.empty:
        raise ValueError("Ledger is empty")

    plt.figure(figsize=figsize)
    plt.plot(df["epoch"], df["train_loss"], label="train_loss", marker="o")
    if "val_loss" in df.columns:
        plt.plot(df["epoch"], df["val_loss"], label="val_loss", marker="o")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Validation Loss")
    plt.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    plt.savefig(save_path)
    plt.close()


def plot_trajectories(npz_path: str, save_path: str, top_k: int = 6, figsize=(10, 6)) -> None:
    if not os.path.exists(npz_path):
        raise FileNotFoundError(f"Param file not found: {npz_path}")
    data = np.load(npz_path)
    # data is a mapping name -> (epochs x param_count)
    # We'll pick up to top_k param-array entries, and within each pick up to 3 elements to visualize
    keys = list(data.files)
    if not keys:
        raise ValueError("No parameter arrays saved in npz")

    # Build a long-form dataframe for seaborn lineplot
    records = []
    for k in keys:
        arr = data[k]  # shape: (epochs, param_count)
        if arr.ndim == 1:
            # maybe stored as flattened single epoch or empty
            arr = arr.reshape((-1, 1))
        epochs = arr.shape[0]
        if epochs == 0:
            continue
        # We'll sample up to 3 indices from the flattened param vector for each parameter tensor
        param_count = arr.shape[1]
        n_samples = min(3, param_count)
        # use evenly spaced indices
        indices = np.linspace(0, param_count - 1, n_samples, dtype=int)
        for idx in indices:
            series = arr[:, idx]
            for e, v in enumerate(series, start=1):
                records.append({"param": f"{k}[{idx}]", "epoch": e, "value": float(v)})

    if not records:
        raise ValueError("No trajectory data available to plot")

    df = pd.DataFrame.from_records(records)

    # Reduce to top_k distinct param series (by appearance order)
    distinct = df["param"].unique()[:top_k]
    df = df[df["param"].isin(distinct)].copy()

    plt.figure(figsize=figsize)
    sns.lineplot(data=df, x="epoch", y="value", hue="param", marker="o")
    plt.title("Parameter Trajectories (selected elements)")
    plt.xlabel("Epoch")
    plt.ylabel("Parameter value")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()


def _cli_plot_trajectories():
    p = argparse.ArgumentParser()
    p.add_argument("npz", type=str, help="Path to param_trajectories.npz")
    p.add_argument("out", type=str, help="Image output path")
    p.add_argument("--top-k", type=int, default=6)
    args = p.parse_args()
    plot_trajectories(args.npz, args.out, top_k=args.top_k)


def _cli_plot_loss():
    p = argparse.ArgumentParser()
    p.add_argument("ledger", type=str, help="Path to training_ledger.csv")
    p.add_argument("out", type=str, help="Image output path")
    args = p.parse_args()
    plot_loss_from_ledger(args.ledger, args.out)


if __name__ == "__main__":
    # Simple CLI which can call either of the plotting functions based on argv
    import sys
    if len(sys.argv) >= 2 and sys.argv[1].endswith(".npz"):
        _cli_plot_trajectories()
    else:
        _cli_plot_loss()
