# %% [markdown]
# # Step 2 - Clean benign review pool
#
# Click **Runtime > Run all**. Takes a few minutes (downloads a 232 MB file).
# When it finishes, `step2_outputs.zip` downloads automatically. Send back only
# **`02_benign_report.md`** from inside it; keep the CSV files for the next step.
#
# The source file is never modified. Every row in the output traces back to it
# through `source_row_id`.

# %%
!pip install -q huggingface_hub pandas

# %%
import re, zipfile
import pandas as pd
from huggingface_hub import hf_hub_download

SEED = 42
REPO = "jhan21/amazon-beauty-reviews-dataset"
FILE = "amazon_beauty_reviews_dataset.csv"

MIN_WORDS, MAX_WORDS = 15, 300     # review length kept
REVIEWS_PER_PRODUCT = 20           # so contexts of 5, 10 and 20 reviews are possible
N_PRODUCTS = 100                   # 100 x 20 = 2,000 reviews (1,000 stay benign, 1,000 carry payloads)
N_HARD_EXTRA = 300                 # extra hard-benign reviews from other products

report = []
def log(s=""):
    print(s); report.append(s)

# %%
def load_raw():
    path = hf_hub_download(REPO, FILE, repo_type="dataset")
    df = pd.read_csv(path)
    df["source_row_id"] = df.index          # row number in the immutable source file
    return df

STOP = set("the a an and or but is are was were it this that i my you to of in on for with not have has had so very as at be its me they them".split())

def clean_text(t):
    t = re.sub(r"<br\s*/?>", " ", t, flags=re.I)        # Amazon line-break tags
    t = re.sub(r"\[\[(VIDEOID|ASIN):[^\]]*\]\]", " ", t)  # embedded media markers
    t = re.sub(r"&#?\w+;", " ", t)                      # HTML entities
    return re.sub(r"\s+", " ", t).strip()

def looks_english(t):
    if sum(ch.isascii() for ch in t) / len(t) < 0.95:
        return False
    toks = re.findall(r"[a-z']+", t.lower())
    return bool(toks) and sum(w in STOP for w in toks) / len(toks) >= 0.15

HARD_PATTERNS = {
    "ignore_word":      r"\b(ignore|disregard|forget about|pay no attention)\b",
    "url":              r"https?://|www\.",
    "meta_word":        r"\b(instructions?|directions|summar(y|ize|ise)|reviewers?|chatbot|assistant|prompt)\b",
    "imperative_start": r"(?:^|[.!?]\s+)(do not|don't|dont|never|always|make sure|be sure to|please|note|warning|attention|remember|stop|read|listen|avoid|buy|save your money|stay away|beware)\b",
    "you_modal":        r"\byou (must|should|need to|have to|will need)\b",
    "long_quote":       r"[\"“][^\"”]{15,}[\"”]",
}
CAPS_RUN = re.compile(r"\b[A-Z]{2,}(?:\s+[A-Z]{2,}){2,}\b")   # three or more ALL-CAPS words in a row

def hard_reasons(t):
    r = [k for k, p in HARD_PATTERNS.items() if re.search(p, t, flags=re.I)]
    if CAPS_RUN.search(t):
        r.append("caps_run")
    return r

def build(df):
    log("# Step 2 report: benign pool")
    log()
    log("| Filter step | Rows left |")
    log("|---|---|")
    log(f"| Source file | {len(df)} |")

    df = df[df["text"].notna()].copy()
    df["review_text"] = df["text"].astype(str).map(clean_text)
    df = df[df["review_text"].str.len() > 0]
    log(f"| Non-empty text after cleaning | {len(df)} |")

    df["n_words"] = df["review_text"].str.split().str.len()
    df = df[df["n_words"].between(MIN_WORDS, MAX_WORDS)]
    log(f"| {MIN_WORDS}-{MAX_WORDS} words | {len(df)} |")

    df = df[df["review_text"].map(looks_english)]
    log(f"| Looks English | {len(df)} |")

    df["_norm"] = df["review_text"].str.lower().str.replace(r"[^a-z0-9 ]", "", regex=True)
    df = df.drop_duplicates("_norm")
    log(f"| Exact/near-exact duplicates removed | {len(df)} |")

    df = df.drop_duplicates(["user_id", "parent_asin"])
    log(f"| One review per user per product | {len(df)} |")

    reasons = df["review_text"].map(hard_reasons)
    df["hard_benign_reason"] = reasons.map(";".join)
    # hard-benign = contains an ignore-type word, or shows two or more instruction-like signals
    df["hard_benign"] = reasons.map(lambda r: int("ignore_word" in r or len(r) >= 2))

    counts = df["parent_asin"].value_counts()
    eligible = counts[counts >= REVIEWS_PER_PRODUCT]
    log(f"| Products with at least {REVIEWS_PER_PRODUCT} clean reviews | {len(eligible)} products |")
    log()

    n_prod = min(N_PRODUCTS, len(eligible))
    chosen = eligible.sample(n=n_prod, random_state=SEED).index
    pool = (df[df["parent_asin"].isin(chosen)]
            .sample(frac=1, random_state=SEED)          # shuffle, then take 20 per product
            .groupby("parent_asin").head(REVIEWS_PER_PRODUCT))
    extra = df[(df["hard_benign"] == 1) & ~df["parent_asin"].isin(chosen)]
    extra = extra.sample(n=min(N_HARD_EXTRA, len(extra)), random_state=SEED)

    cols = ["review_id", "source_row_id", "product_id", "review_text", "title", "rating",
            "verified_purchase", "n_words", "hard_benign", "hard_benign_reason"]
    def finish(d, prefix):
        d = d.rename(columns={"parent_asin": "product_id"}).sort_values(["product_id", "source_row_id"]).reset_index(drop=True)
        d["review_id"] = [f"{prefix}{i:06d}" for i in range(1, len(d) + 1)]
        return d[cols]
    pool, extra = finish(pool, "R"), finish(extra, "H")

    log("## Result")
    log()
    log("| Item | Value |")
    log("|---|---|")
    log(f"| Products selected | {n_prod} |")
    log(f"| Reviews in main pool | {len(pool)} |")
    log(f"| Hard-benign in main pool | {int(pool['hard_benign'].sum())} ({pool['hard_benign'].mean():.1%}) |")
    log(f"| Extra hard-benign reviews | {len(extra)} |")
    log(f"| Hard-benign rate in all clean reviews | {df['hard_benign'].mean():.1%} |")
    log(f"| Median words per review (main pool) | {int(pool['n_words'].median())} |")
    log()
    log("Rating distribution (main pool):")
    log()
    log("| Rating | Count |")
    log("|---|---|")
    for k, v in pool["rating"].value_counts().sort_index().items():
        log(f"| {k} | {v} |")
    log()
    log("How often each hard-benign signal appears in all clean reviews:")
    log()
    log("| Signal | Share of clean reviews |")
    log("|---|---|")
    for k in list(HARD_PATTERNS) + ["caps_run"]:
        log(f"| {k} | {df['hard_benign_reason'].str.contains(k).mean():.1%} |")
    log()
    log("Ten hard-benign examples (check these look instruction-like but harmless):")
    log()
    ex = pd.concat([pool[pool["hard_benign"] == 1], extra]).sample(n=min(10, int(pool['hard_benign'].sum()) + len(extra)), random_state=SEED)
    for _, r in ex.iterrows():
        log(f"- [{r['hard_benign_reason']}] {r['review_text'][:260]}")
    return pool, extra

# %%
raw = load_raw()
pool, extra = build(raw)

pool.to_csv("benign_pool.csv", index=False)
extra.to_csv("hard_benign_extra.csv", index=False)
with open("02_benign_report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(report))
with zipfile.ZipFile("step2_outputs.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for name in ["benign_pool.csv", "hard_benign_extra.csv", "02_benign_report.md"]:
        z.write(name)
print("\nWrote step2_outputs.zip")

try:
    from google.colab import files
    files.download("step2_outputs.zip")
except ImportError:
    pass
