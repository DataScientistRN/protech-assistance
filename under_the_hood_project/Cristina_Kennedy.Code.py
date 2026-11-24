"""
Cristina Kennedy
Graduate Research Project: "Under the hood"
Health Analytics - model behavior during training

WHAT THIS SCRIPT DOES
---------------------
1. Loads the hospital readmissions dataset (binary target: readmitted within 30 days)
   and prepares it exactly as in my earlier CSCI E-83 project.
2. Tunes a few hyperparameters ONCE on a handful of sampled models, then freezes them.
3. Trains N_MODELS model instances (different random seeds -> different train/test
   split and different internal randomness). For every instance it records the
   predicted probability of "readmitted" for a fixed set of tracked patients after
   EVERY training iteration (1..N_ITERS).
4. Keeps only the top-quality models (by test accuracy).
5. For each tracked patient, draws one "trajectory plot" with all models overlaid,
   saves them as PNGs, and automatically flags patients showing "bad behavior" (BB):
   diverging, polarity flip, bimodal (split into sub-clusters), or ideal (converged).
6. Writes everything to the Output/ subfolder (created if missing).

HOW TO RUN
----------
    python Cristina_Kennedy.Code.py            # full run
    python Cristina_Kennedy.Code.py --quick    # tiny run to check that it works
    python Cristina_Kennedy.Code.py --model mlp   # neural network instead of boosting

Needs: Python 3.9+, numpy, pandas, scikit-learn, matplotlib.
Data: Cristina_Kennedy.Data.csv (or hospital_readmissions.csv) in the SAME folder as this file.
Data source: https://www.kaggle.com/datasets/dubradave/hospital-readmissions
"""

import argparse
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # no display needed: figures are only saved to files
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------------
# SETTINGS (change here)
# ----------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILES = ["Cristina_Kennedy.Data.csv", "hospital_readmissions.csv"]
OUT_DIR = os.path.join(HERE, "Output")

TARGET = "readmitted"
N_MODELS = 300          # model instances (instructor used 2000; 200-500 is enough to see patterns)
N_ITERS = 200           # training iterations tracked (1..200)
PLOT_EVERY = 1          # use 10 to plot every 10th iteration if things are slow
N_TRACKED = 1000        # number of patients (observations) whose trajectories are stored
N_PLOT_ALL = 300        # how many of those get a plot in Output/all_plots/
N_FLAGGED_PER_TYPE = 12 # best examples per BB category saved in Output/flagged/
TEST_SIZE = 0.4         # same 60/40 split as in my earlier project
KEEP_TOP_FRAC = 0.75    # keep the top 75% of models by test accuracy ("top quality only")
ACC_FLOOR = 0.0         # optional absolute accuracy floor (instructor suggests ~0.8 when the
                        # dataset allows; readmission data tops out near 0.6-0.65, so 0 here)
MASTER_SEED = 665
N_JOBS = -1             # all CPU cores


# ----------------------------------------------------------------------------
# 1. DATA (same preparation as my earlier project)
# ----------------------------------------------------------------------------
def load_data():
    path = next((os.path.join(HERE, f) for f in DATA_FILES if os.path.exists(os.path.join(HERE, f))), None)
    if path is None:
        sys.exit("Data file not found. Put one of %s next to this script." % DATA_FILES)
    df = pd.read_csv(path)
    print("Loaded %s  shape=%s" % (os.path.basename(path), df.shape))

    # diabetes flag from the three diagnosis columns
    df["diabetes"] = ((df["diag_1"] == "Diabetes") | (df["diag_2"] == "Diabetes")
                      | (df["diag_3"] == "Diabetes")).astype(int)
    df = df.drop(columns=["medical_specialty", "diag_1", "diag_2", "diag_3"])

    # yes/no columns -> 1/0
    for col in ["change", "diabetes_med", "readmitted"]:
        df[col] = df[col].map({"yes": 1, "no": 0})

    # ordinal encodings
    age_ord = {"[40-50)": 1, "[50-60)": 2, "[60-70)": 3, "[70-80)": 4, "[80-90)": 5, "[90-100)": 6}
    df["age"] = df["age"].map(age_ord)
    tests = {"no": 0, "normal": 1, "high": 2}
    df["glucose_test"] = df["glucose_test"].map(tests)
    df["A1Ctest"] = df["A1Ctest"].map(tests)

    df = df.dropna().reset_index(drop=True)
    X = df.drop(columns=[TARGET])
    y = df[TARGET].astype(int)
    print("Prepared: %d patients, %d features, readmission rate %.3f" % (len(X), X.shape[1], y.mean()))
    return X, y


# ----------------------------------------------------------------------------
# 2. MODELS
# ----------------------------------------------------------------------------
def make_model(kind, seed, params):
    if kind == "gbm":
        # subsample<1 makes boosting stochastic, so every seed gives a different trajectory
        return GradientBoostingClassifier(n_estimators=N_ITERS, subsample=0.5,
                                          random_state=seed, **params)
    return MLPClassifier(hidden_layer_sizes=(32,), solver="adam", batch_size=256,
                         random_state=seed, **params)


def trajectories(kind, seed, params, X_train, y_train, X_test, y_test, X_obs):
    """Return (trajectory array [N_ITERS, n_obs], final test accuracy).

    'Training with nIter = 1, 2, 3, ... restarting each time with identical settings'
    gives the same predictions as training once and reading the model after every step:
      * boosting: staged_predict_proba() returns the ensemble after 1, 2, ... trees
      * neural net: partial_fit() runs one more epoch (same seed, same shuffling stream)
    so we use these exact shortcuts instead of re-training 200 times.
    """
    model = make_model(kind, seed, params)
    if kind == "gbm":
        model.fit(X_train, y_train)
        traj = np.array([p[:, 1] for p in model.staged_predict_proba(X_obs)], dtype=np.float32)
    else:
        traj = np.empty((N_ITERS, len(X_obs)), dtype=np.float32)
        for it in range(N_ITERS):
            model.partial_fit(X_train, y_train, classes=[0, 1])
            traj[it] = model.predict_proba(X_obs)[:, 1]
    acc = float((model.predict(X_test) == y_test).mean())
    return traj, acc


def one_run(kind, seed, params, X, y, obs_idx, scale):
    Xv = X.values.astype(np.float64)
    if scale:
        Xv = StandardScaler().fit_transform(Xv)
    Xtr, Xte, ytr, yte = train_test_split(Xv, y.values, test_size=TEST_SIZE, random_state=seed, stratify=y.values)
    return trajectories(kind, seed, params, Xtr, ytr, Xte, yte, Xv[obs_idx])


def tune(kind, X, y, obs_idx, scale, rng):
    """Tune hyperparameters on a few sampled models, then freeze them for all runs."""
    grid = ([dict(max_depth=2, learning_rate=0.1), dict(max_depth=3, learning_rate=0.1),
             dict(max_depth=3, learning_rate=0.05)] if kind == "gbm" else
            [dict(learning_rate_init=0.01, alpha=1e-4), dict(learning_rate_init=0.003, alpha=1e-3),
             dict(learning_rate_init=0.001, alpha=1e-2)])
    seeds = rng.integers(0, 10**6, size=3)
    best, best_acc = None, -1
    for params in grid:
        accs = [one_run(kind, int(s), params, X, y, obs_idx[:5], scale)[1] for s in seeds]
        print("  tuning %s -> mean accuracy %.4f" % (params, np.mean(accs)))
        if np.mean(accs) > best_acc:
            best, best_acc = params, float(np.mean(accs))
    print("Chosen hyperparameters:", best)
    return best


# ----------------------------------------------------------------------------
# 3. BAD-BEHAVIOR (BB) DETECTION
# ----------------------------------------------------------------------------
def score_observations(T):
    """T has shape [models, iters, obs]. Returns a DataFrame with one row per tracked patient."""
    n_models, n_iters, n_obs = T.shape
    mean = T.mean(axis=0)                      # [iters, obs] average trajectory
    std = T.std(axis=0)
    early, mid, last = min(24, n_iters - 1), n_iters // 2, n_iters - 1

    final = T[:, last, :]                      # [models, obs]
    # bimodality coefficient of final predictions (>0.555 hints at two sub-clusters)
    z = (final - final.mean(0)) / (final.std(0) + 1e-9)
    skew, kurt = (z ** 3).mean(0), (z ** 4).mean(0)
    bimod = (skew ** 2 + 1) / (kurt + 1e-9)
    # share of models on each side of 0.5 at the end (a real split needs both sides populated)
    share_pos = (final > 0.5).mean(0)
    split = np.minimum(share_pos, 1 - share_pos)

    # polarity flip: average trajectory is on one side of 0.5 early/mid and the other side at the end
    pk_idx = np.abs(mean[:mid] - 0.5).argmax(0)
    peak = mean[pk_idx, np.arange(n_obs)]
    flip = (np.sign(peak - 0.5) != np.sign(mean[last] - 0.5)) & (np.abs(peak - 0.5) > 0.08)

    out = pd.DataFrame({
        "obs": np.arange(n_obs),
        "final_mean": mean[last], "final_std": std[last],
        "std_growth": std[last] / (std[early] + 1e-6),
        "bimodality": bimod, "split_share": split,
        "peak_mean": peak, "polarity_flip": flip,
    })
    out["type"] = "other"
    out.loc[out["final_std"] < 0.05, "type"] = "ideal"
    out.loc[(out["final_std"] > 0.12) & (out["std_growth"] > 1.5), "type"] = "diverging"
    out.loc[(out["bimodality"] > 0.6) & (out["split_share"] > 0.2) & (out["final_std"] > 0.12), "type"] = "bimodal"
    out.loc[out["polarity_flip"], "type"] = "polarity_flip"
    return out


# ----------------------------------------------------------------------------
# 4. PLOTS
# ----------------------------------------------------------------------------
def draw(ax, T_obs, iters, title):
    """T_obs: [models, iters] for one patient. One thin translucent line per model."""
    ax.plot(iters, T_obs[:, iters - 1].T, color="black", alpha=max(0.02, min(0.25, 20 / len(T_obs))), lw=0.6)
    ax.plot(iters, T_obs[:, iters - 1].mean(0), color="red", lw=1.2, label="mean")
    ax.axhline(0.5, color="gray", lw=0.6, ls="--")
    ax.set_ylim(0, 1)
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("model learning iterations")
    ax.set_ylabel("observation predictions")


def save_single(T_obs, iters, title, path):
    fig, ax = plt.subplots(figsize=(5, 3.6))
    draw(ax, T_obs, iters, title)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def make_outputs(T, obs_idx, scores, kind):
    iters = np.arange(1, N_ITERS + 1)[::PLOT_EVERY]
    all_dir, flag_dir = os.path.join(OUT_DIR, "all_plots"), os.path.join(OUT_DIR, "flagged")
    os.makedirs(all_dir, exist_ok=True)

    # (a) plain browsable folder of plots - eyeball it as thumbnails
    for j in range(min(N_PLOT_ALL, T.shape[2])):
        save_single(T[:, :, j], iters, "Learning observation predictions # %d" % obs_idx[j],
                    os.path.join(all_dir, "obs_%05d.png" % obs_idx[j]))

    # (b) best examples per BB category + one summary figure for the paper
    summary_types = ["ideal", "diverging", "polarity_flip", "bimodal"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    for ax, typ in zip(axes.ravel(), summary_types):
        sub = scores[scores["type"] == typ]
        key = {"ideal": "final_std", "diverging": "final_std", "polarity_flip": "peak_mean",
               "bimodal": "bimodality"}[typ]
        asc = typ == "ideal"
        if typ == "polarity_flip":
            sub = sub.assign(k=(sub["peak_mean"] - 0.5).abs() + (sub["final_mean"] - 0.5).abs())
            sub = sub.sort_values("k", ascending=False)
        elif typ == "ideal":  # models agree AND land on a clear answer (far from 0.5)
            sub = sub.assign(k=sub["final_std"] - 0.5 * (sub["final_mean"] - 0.5).abs()).sort_values("k")
        else:
            sub = sub.sort_values(key, ascending=asc)
        os.makedirs(os.path.join(flag_dir, typ), exist_ok=True)
        for _, r in sub.head(N_FLAGGED_PER_TYPE).iterrows():
            j = int(r["obs"])
            save_single(T[:, :, j], iters, "%s - observation # %d" % (typ, obs_idx[j]),
                        os.path.join(flag_dir, typ, "obs_%05d.png" % obs_idx[j]))
        if len(sub):
            j = int(sub.iloc[0]["obs"])
            draw(ax, T[:, :, j], iters, "%s: observation # %d" % (typ, obs_idx[j]))
        else:
            ax.set_title("%s: none found" % typ, fontsize=9)
            ax.set_ylim(0, 1)
    fig.suptitle("Training trajectories of %d models (%s)" % (T.shape[0], kind), fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "summary_figure.png"), dpi=150)
    plt.close(fig)

    # (c) overall picture: spread of final predictions vs how much the models disagree
    fig, ax = plt.subplots(figsize=(6, 4.5))
    colors = {"ideal": "tab:green", "diverging": "tab:orange", "polarity_flip": "tab:red",
              "bimodal": "tab:purple", "other": "lightgray"}
    for typ, c in colors.items():
        s = scores[scores["type"] == typ]
        ax.scatter(s["final_mean"], s["final_std"], s=10, color=c, label="%s (%d)" % (typ, len(s)))
    ax.set_xlabel("mean final prediction")
    ax.set_ylabel("std of final prediction across models")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "disagreement_map.png"), dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    global N_MODELS, N_ITERS, N_TRACKED, N_PLOT_ALL, N_FLAGGED_PER_TYPE
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["gbm", "mlp"], default="gbm",
                    help="gbm = gradient boosting (default), mlp = small neural network")
    ap.add_argument("--quick", action="store_true", help="tiny run to test the pipeline")
    args = ap.parse_args()
    if args.quick:
        N_MODELS, N_ITERS, N_TRACKED, N_PLOT_ALL, N_FLAGGED_PER_TYPE = 12, 60, 150, 10, 3

    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    kind, scale = args.model, args.model == "mlp"
    rng = np.random.default_rng(MASTER_SEED)

    X, y = load_data()
    obs_idx = np.sort(rng.choice(len(X), size=min(N_TRACKED, len(X)), replace=False))

    print("\nTuning hyperparameters on a few sampled models ...")
    params = tune(kind, X, y, obs_idx, scale, rng)

    print("\nTraining %d model instances x %d iterations ..." % (N_MODELS, N_ITERS))
    seeds = rng.integers(0, 10**6, size=N_MODELS)
    res = Parallel(n_jobs=N_JOBS, verbose=5)(
        delayed(one_run)(kind, int(s), params, X, y, obs_idx, scale) for s in seeds)
    trajs = np.stack([r[0] for r in res])      # [models, iters, obs]
    accs = np.array([r[1] for r in res])
    print("Test accuracy over models: mean %.4f  min %.4f  max %.4f" % (accs.mean(), accs.min(), accs.max()))

    # keep top-quality models only
    cutoff = max(np.quantile(accs, 1 - KEEP_TOP_FRAC), ACC_FLOOR)
    keep = accs >= cutoff
    T = trajs[keep]
    print("Keeping %d of %d models (accuracy >= %.4f)" % (keep.sum(), N_MODELS, cutoff))

    scores = score_observations(T)
    scores["patient_row"] = obs_idx
    scores["actual_readmitted"] = y.values[obs_idx]
    scores.to_csv(os.path.join(OUT_DIR, "observation_scores.csv"), index=False)
    pd.DataFrame({"seed": seeds, "test_accuracy": accs, "kept": keep}).to_csv(
        os.path.join(OUT_DIR, "model_accuracies.csv"), index=False)

    print("\nBB category counts among %d tracked patients:" % len(scores))
    print(scores["type"].value_counts().to_string())

    print("\nDrawing plots ...")
    make_outputs(T, obs_idx, scores, "gradient boosting" if kind == "gbm" else "neural network")
    print("\nDone in %.1f min. Everything is in: %s" % ((time.time() - t0) / 60, OUT_DIR))


if __name__ == "__main__":
    main()
