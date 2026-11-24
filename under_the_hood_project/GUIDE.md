# Under the hood - project guide

## Folder (what you submit)
```
Cristina_Kennedy.Code.py
Cristina_Kennedy.Data.csv     <- your hospital_readmissions.csv, renamed
Cristina_Kennedy.Paper.pdf    <- written by you, separate from the ZIP
Output/                       <- created by the script (do not zip, or do - harmless)
```
ZIP = the .py + the .csv. Put the PDF and the ZIP on Google Drive/OneDrive with "anyone with the link" access
and paste both links into the Conclusions section of the online quiz.

## Run it
1. `pip install numpy pandas scikit-learn matplotlib`
2. `python Cristina_Kennedy.Code.py --quick`   (about 30 s, checks everything works)
3. `python Cristina_Kennedy.Code.py`            (full run; 300 models, 200 iterations)
4. Optional: `--model mlp` for the neural network. Compare both - the assignment suggests trying several types.
5. If it is slow, lower `N_MODELS` or raise `PLOT_EVERY` (e.g. 10) at the top of the script.

## What to look at in Output/
| File | Use |
|---|---|
| `all_plots/` | Open in thumbnail view and eyeball for odd shapes (the instructor's method) |
| `flagged/<type>/` | Auto-picked best examples: ideal, diverging, polarity_flip, bimodal |
| `summary_figure.png` | 2x2 figure ready for the Results section |
| `disagreement_map.png` | Where patients with unstable predictions sit |
| `observation_scores.csv` | Numbers per patient (use to describe them: age, prior inpatient visits, ...) |
| `model_accuracies.csv` | Accuracy of every model (report mean/min/max in the Dataset or Results section) |

**Important:** the flags are only a shortcut. Open the images yourself and choose examples that are
really convincing. If a category is empty, say so honestly - the instructor notes that not every
dataset/model shows these problems. Try the other model type or a different `MASTER_SEED`.

## Paper outline (PDF; title + your name at the top)
1. **Dataset** - source (Kaggle link), 25,000 patients, target = readmitted within 30 days, features used,
   preprocessing (diabetes flag, encodings), class balance, accuracy range of your models and which models were kept.
2. **Results (Illustrations)** - method in 3-4 sentences (N models x 200 iterations, different seeds/splits,
   hyperparameters tuned once then frozen); then 3-4 figures with captions: one ideal case, then each BB pattern you found.
   Name the patient #, and say what is special about them (use observation_scores.csv + the CSV rows).
3. **Conclusions** - ONE paragraph explaining why the BB happens (see ideas below), then the two shared links.
4. **References** - Kaggle dataset, scikit-learn, any paper/article you cite.

## Ideas for the "why" paragraph (pick what your plots support)
- The patient sits near the decision boundary (probability ~0.5), so tiny differences between models flip the outcome.
- Readmission is noisy and weakly predictable (accuracy ~0.6): features carry little signal, so each seed fits different noise.
- Overfitting: with more iterations the model memorises its own training split, and predictions for patients
  not in that split diverge - check whether divergent patients mostly have rare feature combinations.
- Different train/test splits expose different training patients, so models disagree about unusual patients.
- Boosting adds trees sequentially: early trees capture broad trends, later trees chase residuals - this can move a
  patient's prediction up first, then down (polarity flip).
- Bimodal clusters: two plausible "explanations" of the patient depending on which neighbours were in the training set.

## Questions to confirm with your instructor
- Are numpy / pandas / scikit-learn / matplotlib allowed as "no external dependencies"?
- Is the due date Dec 7, 2025 (as printed) or a 2026 date?
- Is the accuracy ~0.8 cutoff mandatory, or is a relative cutoff OK for this dataset (the script keeps the top 75% by default)?
