"""Figures for the term paper, drawn from data/results_detection.csv and data/results_breakdown.csv."""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA, OUT = sys.argv[1], sys.argv[2]
res = pd.read_csv(f"{DATA}/results_detection.csv")
brk = pd.read_csv(f"{DATA}/results_breakdown.csv")

# fixed colour per detector (categorical slots 1-4, in order); validated with the dataviz palette script
DET = [("finetuned_transformer", "Fine-tuned transformer", "#2a78d6"),
       ("heuristic_dataset_informed", "Dataset-informed rules", "#eb6834"),
       ("tfidf_logreg", "TF-IDF + LR", "#1baf7a"),
       ("embedding_xgboost", "Embedding + XGBoost", "#eda100")]
LIGHT, DARK = "#86b6ef", "#1c5cab"          # two steps of the blue ramp for paired conditions
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
SETTINGS = [("in_distribution", "In-dist."), ("lodo:bipia", "LODO\nBIPIA"), ("lodo:deepset", "LODO\ndeepset"),
            ("lodo:gandalf", "LODO\nGandalf"), ("lodo:review_specific_v1", "LODO\nRev.-spec."),
            ("heldout_strategy", "Held-out\nstrategy"), ("heldout_obfuscation", "Held-out\nobfusc.")]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False})

def style(ax, ylabel):
    ax.set_ylim(0, 1.0); ax.set_ylabel(ylabel)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", length=0)

def grouped(ax, groups, series, width_total=0.82, gap=0.02):
    """series: list of (label, colour, values). Bars separated by a small surface gap."""
    n = len(series); w = width_total / n
    x = np.arange(len(groups))
    for i, (label, colour, vals) in enumerate(series):
        ax.bar(x - width_total / 2 + w * (i + 0.5), vals, width=w - gap, color=colour, label=label, linewidth=0)
    ax.set_xticks(x); ax.set_xticklabels(groups)

def save(fig, name):
    fig.savefig(f"{OUT}/{name}.pdf", bbox_inches="tight")
    fig.savefig(f"{OUT}/{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

# Figure 1: F1 in every setting
f1 = res.pivot(index="detector", columns="setting", values="f1")
fig, ax = plt.subplots(figsize=(6.6, 2.9))
grouped(ax, [s[1] for s in SETTINGS], [(lab, col, f1.loc[d, [s[0] for s in SETTINGS]].values) for d, lab, col in DET])
style(ax, "F1 on the test set")
ax.legend(ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8, handlelength=1.2, columnspacing=1.2)
save(fig, "fig_f1_settings")

# Figure 2: in-distribution recall by embedding strategy
STRAT = [("append", "Append"), ("prepend", "Prepend"), ("mid_insertion", "Mid-\ninsertion"),
         ("delimiter_spoofing", "Delimiter\nspoofing"), ("semantic_camouflage", "Semantic\ncamouflage")]
st = brk[brk.attribute == "embedding_strategy"].pivot(index="detector", columns="value", values="recall")
fig, ax = plt.subplots(figsize=(6.6, 2.7))
grouped(ax, [s[1] for s in STRAT], [(lab, col, st.loc[d, [s[0] for s in STRAT]].values) for d, lab, col in DET])
style(ax, "Recall (in-distribution)")
ax.legend(ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8, handlelength=1.2, columnspacing=1.2)
save(fig, "fig_recall_strategy")

# Figure 3: two panels - strict operating point, and false alarms on hard-benign reviews
ORDER = [("finetuned_transformer", "Fine-tuned\ntransformer"), ("heuristic_dataset_informed", "Dataset-informed\nrules"),
         ("tfidf_logreg", "TF-IDF\n+ LR"), ("embedding_xgboost", "Embedding\n+ XGBoost"), ("heuristic_vigil", "Vigil\nrules")]
tpr = res.pivot(index="detector", columns="setting", values="tpr_at_1pct_fpr")
fpr = brk[brk.attribute == "benign_type"].pivot(index="detector", columns="value", values="recall")
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.9), gridspec_kw={"hspace": 0.55})
grouped(a1, [o[1] for o in ORDER], [("In-distribution", LIGHT, tpr.loc[[o[0] for o in ORDER], "in_distribution"].values),
                                    ("Review-specific payloads held out", DARK, tpr.loc[[o[0] for o in ORDER], "lodo:review_specific_v1"].values)])
style(a1, "Recall at\n1% FPR"); a1.set_title("(a) Recall when false alarms must stay below 1%", fontsize=9, loc="left")
a1.legend(loc="upper right", fontsize=8, handlelength=1.2)
ord_v = fpr.loc[[o[0] for o in ORDER], "ordinary"].values; hard_v = fpr.loc[[o[0] for o in ORDER], "hard_benign"].values
grouped(a2, [o[1] for o in ORDER], [("Ordinary benign (n=149)", LIGHT, ord_v), ("Hard-benign (n=31)", DARK, hard_v)])
style(a2, "False-positive\nrate"); a2.set_ylim(0, 0.3)
a2.set_title("(b) False alarms on genuine reviews (in-distribution)", fontsize=9, loc="left")
a2.legend(loc="upper left", fontsize=8, handlelength=1.2)
w = 0.82 / 2                                    # mark zero-height bars so they are not read as missing
for i, (o, h) in enumerate(zip(ord_v, hard_v)):
    for j, v in enumerate((o, h)):
        if v == 0:
            a2.text(i - 0.41 + w * (j + 0.5), 0.004, "0", ha="center", va="bottom", fontsize=7.5, color=INK2)
save(fig, "fig_strict_and_false_alarms")
print("done")
