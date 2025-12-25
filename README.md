# Archon — NBA Prediction & Learning Pipeline

A compact end-to-end pipeline for producing NBA matchup predictions, performing metric-driven learning, and debugging parameter trajectories.  
This project implements a lightweight "Archon" engine that:

- Fetches live NBA team stats and today's schedule (optional, via `nba_api`)
- Builds a normalized master dataset
- Applies per-team intelligence layers (coach EVA scalars and stadium entropy)
- Produces nightly predictions
- Trains via gradient updates (per-team + optional global params)
- Supports early stopping using a validation set
- Produces parameter trajectory plots for debugging

This README explains the structure, CSV schemas, how to run the pipeline, training, and plotting.

---

## Table of contents

- Project summary
- Requirements
- Key scripts
- CSV schemas
- Quickstart examples
- Training & early stopping
- Plotting parameter trajectories
- Tips, caveats, and troubleshooting
- License

---

## Project summary

This project focuses on a transparent, linear prediction model:

prediction = base_spread + coach_weight * (c_a - c_b) + entropy_multiplier * ent_a

Where:
- base_spread — fundamental anchor from live API or master CSV (Delta_W_Final)
- c_a / c_b — per-team coach EVA_Scalar
- ent_a — home-team Entropy_Alpha
- coach_weight, entropy_multiplier — global weights

Training adjusts per-team parameters (EVA_Scalar and Entropy_Alpha) using SGD on squared error loss. Optionally the global weights can be updated. The training loop supports early stopping on a validation set and generates plots of parameter trajectories during training.

---

## Requirements

- Python 3.8+
- Recommended packages:
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - nba_api (optional — only for live fetch)
- Install with pip:
  ```
  pip install pandas numpy matplotlib seaborn
  pip install nba_api          # optional (for --fetch)
  ```

---

## Key scripts

- `run_archon.py`  
  Minimal CLI: fetch master (optional), run engine, save predictions.

- `agent_training.py`  
  Metric-based recalibration script (not gradient-based).

- `agent_training_grad.py`  
  Gradient-based training (per-team SGD-style updates).

- `agent_training_grad_es.py`  
  Gradient training with early stopping on a validation set.

- `agent_training_with_plots.py`  
  Gradient training + early stopping + automatic plotting (checkpoint plotting).

- `plot_param_trajectories.py`  
  Standalone plotting tool (reads training ledger CSV).

Note: example file names used by scripts:
- master CSV: `archon_master_data_normalized.csv`
- coach intelligence: `archon_coach_iq.csv`
- stadium intelligence: `archon_stadium_entropy.csv`
- predictions output: `archon_final_predictions.csv`
- training ledger: e.g. `archon_learning_ledger_grad_es.csv`

---

## CSV schemas

1. archon_master_data_normalized.csv (master)
- Required columns:
  - Date, Team_A, Team_B, NetRtg_A, NetRtg_B, Delta_W_Final, Team_A_Key, Team_B_Key
- `Team_A_Key` / `Team_B_Key` must match short keys used in intelligence CSVs (e.g., `Lakers`, `Nuggets`).

2. archon_coach_iq.csv (coach intelligence)
- Header:
  ```
  Team,EVA_Scalar
  ```
- Example:
  ```
  Lakers,0.35
  Nuggets,0.10
  ```

3. archon_stadium_entropy.csv (stadium intelligence)
- Header:
  ```
  Team,Entropy_Alpha
  ```
- Example:
  ```
  Lakers,1.2
  Nuggets,0.6
  ```

4. actual_results.csv (post-game actuals for training/validation)
- Header:
  ```
  Matchup,Actual_Spread
  ```
- `Matchup` must match prediction format `"{TeamA} vs {TeamB}"` where Team names are short keys.
- Example:
  ```
  Lakers vs Nuggets,3.0
  ```

---

## Quickstart

1. Fetch live master data (requires `nba_api`):
   ```
   python run_archon.py --fetch
   ```
   This creates `archon_master_data_normalized.csv`.

2. Provide intelligence CSVs:
   - `archon_coach_iq.csv`
   - `archon_stadium_entropy.csv`
   If these files are missing, the engine assumes zeros for missing teams (safe fallback).

3. Produce predictions:
   ```
   python run_archon.py --master archon_master_data_normalized.csv --coach archon_coach_iq.csv --stadium archon_stadium_entropy.csv --output archon_final_predictions.csv
   ```

4. Validate (after obtaining actual results):
   ```
   python run_archon.py --master archon_master_data_normalized.csv --coach archon_coach_iq.csv --stadium archon_stadium_entropy.csv --output archon_final_predictions.csv --validate actual_results.csv
   ```

---

## Training (gradient updates)

Use `agent_training_grad_es.py` (with early stopping) or `agent_training_with_plots.py` (with plotting):

Example (train with validation and early stopping):
```
python agent_training_grad_es.py train \
  --master archon_master_data_normalized.csv \
  --coach archon_coach_iq.csv \
  --stadium archon_stadium_entropy.csv \
  --actuals train_actuals.csv \
  --val val_actuals.csv \
  --epochs 50 \
  --lr-coach 0.05 \
  --lr-entropy 0.02 \
  --online \
  --patience 5 \
  --min-delta 1e-4
```

Example (train + automatic plots & early stopping):
```
python agent_training_with_plots.py train \
  --master archon_master_data_normalized.csv \
  --coach archon_coach_iq.csv \
  --stadium archon_stadium_entropy.csv \
  --actuals train_actuals.csv \
  --val val_actuals.csv \
  --outdir training_runs/run1 \
  --epochs 50 \
  --online \
  --plot-interval 5 \
  --restore-best
```

After training, the scripts overwrite the provided coach/stadium CSVs with updated parameters by default — keep backups if you want to compare pre/post.

---

## Plotting parameter trajectories (automatic)

- `agent_training_with_plots.py` will save plots under `<outdir>/plots` at checkpoints and on validation improvement.
- If you prefer to plot after training, use:
  ```
  python plot_param_trajectories.py --ledger training_runs/run1/ledger.csv --outdir debug_plots
  ```

Generated plot files:
- `global_params.png` — coach_weight and entropy_multiplier across epochs
- `coach_params_topK.png` — top-K coach EVA_Scalar trajectories
- `entropy_params_topK.png` — top-K entropy trajectories

---

## Recommended workflow

1. Use `run_archon.py --fetch` nightly to refresh `archon_master_data_normalized.csv`.
2. Maintain and update intelligence CSVs (`archon_coach_iq.csv`, `archon_stadium_entropy.csv`) or let training update them.
3. Run predictions with `run_archon.py` and save results with a timestamped filename for auditability.
4. Collect actual results nightly, run training (online or batch) with `agent_training_with_plots.py` to update intelligence and generate plots.
5. Inspect parameter plots to ensure reasonable behavior (convergence, no runaway values).

---

## Tips & caveats

- The model is intentionally simple and linear — good for transparency and quick debugging, not necessarily state-of-the-art predictive power.
- The notebook and scripts use proxies (e.g., W_PCT / PTS) if NET_RATING/PACE are not present in the API response. For best results supply appropriate features in the master CSV.
- Keep backups of intelligence CSVs before running training if you want to compare parameter evolution.
- Adjust learning rates conservatively. Start with small lr_coach (0.01-0.05) and lr_entropy (0.005-0.02).
- Use early stopping and validation to guard against overfitting to noisy actuals.

---

## Troubleshooting

- No nba_api or scoreboard fetch fails:
  - Ensure `nba_api` is installed and your environment has outbound network access.
  - Alternatively, provide a pre-built `archon_master_data_normalized.csv` and skip the `--fetch` step.

- Ledger missing expected columns for plotting:
  - Confirm you used the gradient training scripts in online mode (they emit `updated_c_a`, `updated_c_b`, and `updated_ent_a`).
  - If batch mode was used, ledger formats differ — use the training script's batch outputs or adapt the plotting script.

- Predictions inconsistent with expectations:
  - Check intelligence CSV formats and short team keys match `Team_A_Key`/`Team_B_Key`.
  - Inspect global weights printed in the ledger; they may require tuning/regularization.

---

## License

MIT License — adapt and reuse as needed.

---

If you'd like, I can:
- Produce example CSVs (small master + coach + stadium + actuals) so you can run the pipeline end-to-end locally, or
- Add a simple Dockerfile or GitHub Actions workflow to run nightly predictions and save artifacts. Which would you prefer?# NBA-cce5.0
