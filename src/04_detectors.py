# %% [markdown]
# # Step 6 - Detector benchmark (no API needed)
#
# **Before running:** Runtime > Change runtime type > **T4 GPU** > Save.
#
# 1. Click **Runtime > Run all**.
# 2. When the upload button appears, choose **`step3_outputs.zip`**.
# 3. It takes roughly 10-20 minutes. `step4_outputs.zip` downloads at the end.
#    Send back only **`04_detector_report.md`**; keep the zip.
#
# Detectors: two heuristics (independent published rules, and dataset-informed rules), TF-IDF + logistic regression,
# embeddings + XGBoost, and a fine-tuned transformer. They
# are evaluated in seven settings: in-distribution, leave-one-dataset-out (4 folds),
# held-out strategy, and held-out obfuscation.

# %%
!pip install -q sentence-transformers xgboost

# %%
import os, re, time, random, zipfile, traceback
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve, roc_curve

SEED = 42
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FT_MODEL = "distilroberta-base"        # fine-tuned transformer
FT_EPOCHS, FT_LR, FT_BATCH, FT_MAXLEN = 3, 3e-5, 16, 256
RUN_TRANSFORMER_WITHOUT_GPU = False    # on CPU the transformer is very slow, so it is skipped by default

SEEN_STRATEGIES = ["append", "prepend", "mid_insertion"]
HELD_STRATEGIES = ["delimiter_spoofing", "semantic_camouflage"]

report = []
def log(s=""):
    print(s); report.append(s)

def md_table(df):
    log("| " + " | ".join(str(c) for c in df.columns) + " |")
    log("|" + "---|" * len(df.columns))
    for row in df.itertuples(index=False):
        log("| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in row) + " |")
    log()

def set_seed(s=SEED):
    random.seed(s); np.random.seed(s)
    try:
        import torch
        torch.manual_seed(s); torch.cuda.manual_seed_all(s)
    except ImportError:
        pass

# %% [markdown]
# ## Evaluation settings
# Every setting gives three row sets: train, validation (used only to pick the threshold) and test.

# %%
def make_settings(d):
    ben, inj = d[d.is_injection == 0], d[d.is_injection == 1]
    def part(injected_rows, split):
        return pd.concat([ben[ben.split == split], injected_rows])
    S = {}
    S["in_distribution"] = (d[d.split == "train"], d[d.split == "validation"], d[d.split == "test"])
    for src in sorted(inj.payload_source.unique()):
        rest = inj[inj.payload_source != src]
        S[f"lodo:{src}"] = (part(rest[rest.split == "train"], "train"),
                            part(rest[rest.split == "validation"], "validation"),
                            part(inj[inj.payload_source == src], "test"))      # every row of the held-out source
    seen = inj[inj.embedding_strategy.isin(SEEN_STRATEGIES)]
    held = inj[inj.embedding_strategy.isin(HELD_STRATEGIES)]
    S["heldout_strategy"] = (part(seen[seen.split == "train"], "train"),
                             part(seen[seen.split == "validation"], "validation"),
                             part(held[held.split == "test"], "test"))
    plain, obf = inj[inj.obfuscation == "none"], inj[inj.obfuscation != "none"]
    S["heldout_obfuscation"] = (part(plain[plain.split == "train"], "train"),
                                part(plain[plain.split == "validation"], "validation"),
                                part(obf[obf.split == "test"], "test"))
    return S

def best_f1_threshold(y, s):
    p, r, t = precision_recall_curve(y, s)
    f1 = 2 * p[:-1] * r[:-1] / np.maximum(p[:-1] + r[:-1], 1e-12)
    return float(t[int(np.argmax(f1))])

def metrics(y, s, thr):
    y, s = np.asarray(y), np.asarray(s)
    pred = (s >= thr).astype(int)
    tp, fp = int(((pred == 1) & (y == 1)).sum()), int(((pred == 1) & (y == 0)).sum())
    fn, tn = int(((pred == 0) & (y == 1)).sum()), int(((pred == 0) & (y == 0)).sum())
    prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
    fpr_curve, tpr_curve, _ = roc_curve(y, s)
    return {"n_injected": int(y.sum()), "n_benign": int((y == 0).sum()),
            "precision": prec, "recall": rec, "f1": 2 * prec * rec / max(prec + rec, 1e-12),
            "auroc": float(roc_auc_score(y, s)), "auprc": float(average_precision_score(y, s)),
            "fpr": fp / max(fp + tn, 1), "fnr": fn / max(fn + tp, 1),
            "tpr_at_1pct_fpr": float(tpr_curve[fpr_curve <= 0.01].max())}

# %% [markdown]
# ## Detectors
# Each detector is a function: `(train, validation, test) -> (validation scores, test scores)`.

# %%
HEURISTIC_RULES = {
    "override":   r"\b(ignore|disregard|forget|override|bypass|skip|drop|abandon)\b.{0,40}\b(instruction|direction|prompt|rule|guidance|guideline|task|text|above|previous|prior|earlier|everything|review)s?\b",
    "addressee":  r"\b(ai|a\.i\.|assistant|summari[sz]er|chatbot|language model|llm|model|system|bot|gpt)\b",
    "output_ref": r"\b(your|the) (summary|response|answer|reply|output|overview|message|verdict|analysis)\b",
    "command":    r"\b(add|include|insert|append|mention|state|say|write|report|rate|rank|tell|print|reveal|show|repeat|translate|encode|respond|reply|output|describe|summari[sz]e|conclude|omit|exclude|remove|hide)\b.{0,60}\b(summary|response|answer|reply|output|overview|password|prompt|instructions?)\b",
    "new_instr":  r"\b(new|additional|updated|following) (instruction|task|rule|direction)s?\b|\bfrom now on\b|\binstructions?:",
    "delimiter":  r"\[/?(inst|system)[^\]]*\]|</?(system|review)>|<\|im_(start|end)\|>|<!--|###|===|---\s*end|\"role\"\s*:",
    "base64":     r"[A-Za-z0-9+/]{40,}={0,2}",
    "odd_chars":  r"[Ѐ-ӿ​-‏]",
    "secret":     r"\b(password|secret|credentials?)\b",
}
HEURISTIC_COMPILED = {k: re.compile(v, re.I) for k, v in HEURISTIC_RULES.items()}

def heuristic_score(t):
    return float(sum(bool(p.search(t)) for p in HEURISTIC_COMPILED.values()))

def run_heuristic(tr, va, te):
    return va.review_text.map(heuristic_score).values, te.review_text.map(heuristic_score).values

# --- Independent heuristic: rules published by the Vigil project, copied without changes ---
# Source: github.com/deadbits/vigil-llm (Apache-2.0), commit f2b4c134, files data/yara/instruction_bypass.yar
# and data/yara/system_instructions.yar. These rules were written by someone else before this dataset existed,
# so they cannot have been tuned to it. The same word lists appear in Rebuff's heuristic (protectai/rebuff).
VIGIL_BYPASS = (r"(Ignore|Disregard|Skip|Forget|Neglect|Overlook|Omit|Bypass|Pay no attention to|Do not follow|Do not obey)"
                r"\s*(prior|previous|preceding|above|foregoing|earlier|initial)?"
                r"\s*(content|text|instructions|instruction|directives|directive|commands|command|context|conversation|input|inputs|data|message|messages|communication|response|responses|request|requests)"
                r"\s*(and start over|and start anew|and begin afresh|and start from scratch)?")
VIGIL_SYSTEM = ["System Instruction: ", "[system](#assistant)", "[system](#context)", "<s>[INST] <<SYS>>", "<</SYS>>",
                "<|im_start|>assistant", "<|im_start|>system", "{{#system~}}", "{{/system~}}"]

def vigil_score(t, nocase):
    hay = t.lower() if nocase else t
    bypass = bool(re.search(VIGIL_BYPASS, t, re.I if nocase else 0))
    system = any((s.lower() if nocase else s) in hay for s in VIGIL_SYSTEM)
    return float(bypass) + float(system)

def run_vigil(tr, va, te):                 # exactly as published (case-sensitive)
    f = lambda t: vigil_score(t, False)
    return va.review_text.map(f).values, te.review_text.map(f).values

def run_vigil_nocase(tr, va, te):          # one change only: upper/lower case is ignored
    f = lambda t: vigil_score(t, True)
    return va.review_text.map(f).values, te.review_text.map(f).values

def run_tfidf(tr, va, te):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, lowercase=True)
    clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000, random_state=SEED)
    clf.fit(vec.fit_transform(tr.review_text), tr.is_injection)
    return (clf.predict_proba(vec.transform(va.review_text))[:, 1],
            clf.predict_proba(vec.transform(te.review_text))[:, 1])

EMB = {}                                   # review_id -> embedding, computed once
def embed_all(d):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBED_MODEL)
    vecs = model.encode(d.review_text.tolist(), batch_size=64, show_progress_bar=True, normalize_embeddings=True)
    EMB.update(dict(zip(d.review_id, vecs)))

def run_embedding(tr, va, te):
    from xgboost import XGBClassifier
    X = lambda df: np.stack([EMB[i] for i in df.review_id])
    clf = XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8,
                        random_state=SEED, n_jobs=4, eval_metric="logloss")
    clf.fit(X(tr), tr.is_injection.values)
    return clf.predict_proba(X(va))[:, 1], clf.predict_proba(X(te))[:, 1]

def run_transformer(tr, va, te, model_name=None):
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
    set_seed()
    name = model_name or FT_MODEL
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=2).to(dev)

    def batches(df, shuffle):
        idx = np.random.permutation(len(df)) if shuffle else np.arange(len(df))
        texts, labels = df.review_text.tolist(), df.is_injection.tolist()
        for i in range(0, len(idx), FT_BATCH):
            b = idx[i:i + FT_BATCH]
            enc = tok([texts[j] for j in b], truncation=True, max_length=FT_MAXLEN, padding=True, return_tensors="pt")
            yield {k: v.to(dev) for k, v in enc.items()}, torch.tensor([labels[j] for j in b]).to(dev)

    opt = torch.optim.AdamW(model.parameters(), lr=FT_LR, weight_decay=0.01)
    steps = FT_EPOCHS * int(np.ceil(len(tr) / FT_BATCH))
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    model.train()
    for _ in range(FT_EPOCHS):
        for enc, y in batches(tr, True):
            loss = model(**enc, labels=y).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); opt.zero_grad()

    def predict(df):
        model.eval(); out = []
        with torch.no_grad():
            for enc, _ in batches(df, False):
                out.append(torch.softmax(model(**enc).logits, dim=-1)[:, 1].float().cpu().numpy())
        return np.concatenate(out)
    scores = predict(va), predict(te)
    del model, opt
    if dev == "cuda":
        torch.cuda.empty_cache()
    return scores

# %% [markdown]
# ## Run

# %%
if not os.path.exists("dataset_v1.csv"):
    if not os.path.exists("step3_outputs.zip"):
        from google.colab import files
        print("Choose step3_outputs.zip (from the previous step)")
        files.upload()
    zipfile.ZipFile("step3_outputs.zip").extractall(".")
data = pd.read_csv("dataset_v1.csv")
settings = make_settings(data)

try:
    import torch
    HAS_GPU = torch.cuda.is_available()
except ImportError:
    HAS_GPU = False

DETECTORS = [("heuristic_vigil", run_vigil), ("heuristic_vigil_nocase", run_vigil_nocase),
             ("heuristic_dataset_informed", run_heuristic),
             ("tfidf_logreg", run_tfidf), ("embedding_xgboost", run_embedding)]
# Published rules are used as published: a review is flagged when any rule fires (no tuning on our data).
FIXED_THRESHOLD = {"heuristic_vigil": 1.0, "heuristic_vigil_nocase": 1.0}
if HAS_GPU or RUN_TRANSFORMER_WITHOUT_GPU:
    DETECTORS.append(("finetuned_transformer", run_transformer))

log("# Step 6 report: detector benchmark")
log()
log(f"GPU available: {HAS_GPU}")
if not (HAS_GPU or RUN_TRANSFORMER_WITHOUT_GPU):
    log()
    log("**The fine-tuned transformer was SKIPPED because no GPU was found. Set the runtime type to T4 GPU and run again.**")
log()
log("| Setting | Train rows | Validation rows | Test injected | Test benign |")
log("|---|---|---|---|---|")
for name, (tr, va, te) in settings.items():
    log(f"| {name} | {len(tr)} | {len(va)} | {int(te.is_injection.sum())} | {int((te.is_injection == 0).sum())} |")
log()

try:
    embed_all(data)
except Exception as e:
    log(f"**Embedding model failed to load: {e!r}**")

results, preds, failures = [], [], []
for det_name, fn in DETECTORS:
    for set_name, (tr, va, te) in settings.items():
        try:
            set_seed()
            t0 = time.time()
            s_va, s_te = fn(tr, va, te)
            secs = time.time() - t0
            thr = FIXED_THRESHOLD.get(det_name) or best_f1_threshold(va.is_injection.values, s_va)
            m = metrics(te.is_injection.values, s_te, thr)
            results.append({"detector": det_name, "setting": set_name, **m, "threshold": thr, "seconds_total": secs})
            preds.append(pd.DataFrame({"detector": det_name, "setting": set_name, "review_id": te.review_id.values,
                                       "score": s_te, "pred": (s_te >= thr).astype(int)}))
            print(f"{det_name:24s} {set_name:28s} F1={m['f1']:.3f} AUROC={m['auroc']:.3f}  ({secs:.0f}s)")
        except Exception as e:
            failures.append((det_name, set_name, repr(e), traceback.format_exc()[-800:]))
            print(f"FAILED {det_name} / {set_name}: {e!r}")
        pd.DataFrame(results).to_csv("results_detection.csv", index=False)      # saved after every run

res = pd.DataFrame(results)
pred = pd.concat(preds, ignore_index=True) if preds else pd.DataFrame()
pred.to_csv("predictions.csv", index=False)

# %%
SHOW = ["detector", "precision", "recall", "f1", "auroc", "auprc", "fpr", "tpr_at_1pct_fpr"]
log("## Results by setting")
log()
log("Thresholds are chosen on validation data (best F1) and then applied to the test rows. The two `heuristic_vigil` rows are the exception: they flag a review whenever any published rule fires, with nothing tuned on this dataset.")
log()
for set_name in settings:
    sub = res[res.setting == set_name]
    if sub.empty:
        continue
    log(f"### {set_name}  (test: {int(sub.n_injected.iloc[0])} injected, {int(sub.n_benign.iloc[0])} benign)")
    log()
    md_table(sub[SHOW])

log("## F1 summary (rows = detector, columns = setting)")
log()
if not res.empty:
    piv = res.pivot(index="detector", columns="setting", values="f1").reindex(columns=list(settings)).reset_index()
    md_table(piv)
    log("## Recall summary")
    log()
    md_table(res.pivot(index="detector", columns="setting", values="recall").reindex(columns=list(settings)).reset_index())

# breakdown on the in-distribution test set
log("## In-distribution breakdown (recall on injected rows, by attribute)")
log()
ind = pred[pred.setting == "in_distribution"].merge(data, on="review_id") if not pred.empty else pd.DataFrame()
breakdown_rows = []
if not ind.empty:
    for col in ["attack_goal", "embedding_strategy", "obfuscation", "payload_source", "position"]:
        g = (ind[ind.is_injection == 1].groupby([col, "detector"])["pred"].agg(["mean", "size"]).reset_index())
        for r in g.itertuples(index=False):
            breakdown_rows.append({"attribute": col, "value": r[0], "detector": r[1], "recall": float(r[2]), "n": int(r[3])})
        t = g.pivot(index=col, columns="detector", values="mean").reset_index()
        t.insert(1, "n", g.groupby(col)["size"].first().reindex(t[col]).values)
        log(f"By `{col}`:")
        log()
        md_table(t)
    log("False-positive rate on benign rows (hard-benign vs ordinary):")
    log()
    b = ind[ind.is_injection == 0].copy()
    b["benign_type"] = b.hard_benign.map({1: "hard_benign", 0: "ordinary"})
    g = b.groupby(["benign_type", "detector"])["pred"].agg(["mean", "size"]).reset_index()
    t = g.pivot(index="benign_type", columns="detector", values="mean").reset_index()
    t.insert(1, "n", g.groupby("benign_type")["size"].first().reindex(t["benign_type"]).values)
    md_table(t)
    for r in g.itertuples(index=False):
        breakdown_rows.append({"attribute": "benign_type", "value": r[0], "detector": r[1], "recall": float(r[2]), "n": int(r[3])})
pd.DataFrame(breakdown_rows).to_csv("results_breakdown.csv", index=False)

log("## Time")
log()
if not res.empty:
    t = res[res.setting == "in_distribution"][["detector", "seconds_total"]].copy()
    t.columns = ["detector", "train_plus_predict_seconds"]
    md_table(t)
    log("Embedding time is not included for `embedding_xgboost` (embeddings are computed once for all rows).")
    log()

log("## Configuration")
log()
log("| Item | Value |")
log("|---|---|")
log(f"| Seed | {SEED} |")
log("| heuristic_vigil | Rules from github.com/deadbits/vigil-llm (commit f2b4c134), unchanged; written independently of this dataset |")
log("| heuristic_vigil_nocase | Same rules, ignoring upper/lower case; no other change |")
log(f"| heuristic_dataset_informed | {len(HEURISTIC_RULES)} regex rules written by the dataset builder with knowledge of the injection patterns; treat as an upper bound, not a fair baseline |")
log("| TF-IDF + LR | word 1-2 grams, min_df 2, sublinear tf, C=1.0, class_weight balanced |")
log(f"| Embedding + XGBoost | {EMBED_MODEL}; 300 trees, depth 4, lr 0.1, subsample 0.8 |")
log(f"| Fine-tuned transformer | {FT_MODEL}; {FT_EPOCHS} epochs, lr {FT_LR}, batch {FT_BATCH}, max length {FT_MAXLEN} |")
log()
if failures:
    log("## Failures")
    log()
    for d_, s_, e_, tb in failures:
        log(f"- **{d_} / {s_}**: {e_}")
        log("```"); log(tb); log("```")

with open("04_detector_report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(report))
with zipfile.ZipFile("step4_outputs.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for name in ["04_detector_report.md", "results_detection.csv", "results_breakdown.csv", "predictions.csv"]:
        if os.path.exists(name):
            z.write(name)
print("\nWrote step4_outputs.zip")

try:
    from google.colab import files
    files.download("step4_outputs.zip")
except ImportError:
    pass
