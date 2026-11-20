# Project Specification

**Project:** Detecting Indirect Prompt Injection in LLM-Based Product Review Summarization
**Author:** Muhammed Nazmul Arefin (202416760)
**Version:** 1.2, 11 November 2026 (payload sources changed after the data audit; deepset curated by hand)

This file is the single reference for the project. Where the proposal, the literature review, the Bangla workflow manual, or the A-Z guideline disagree with it, this file wins. It is also the `01_specification.md` output that Step 0 of the workflow manual asks for.

## 1. Task in one sentence

Detect whether a product review contains an instruction intended to change an LLM-generated product summary, and measure whether that instruction actually changes the summary.

## 2. Decisions taken

| Point | Decision | Decided by |
|---|---|---|
| Contribution | Two contributions of equal weight: the dataset and the detector benchmark | You, 10 Nov |
| Payload source | Hybrid: three existing corpora plus review-specific payloads written for this project | You, 11 Nov (replaces "corpora only" from 10 Nov) |
| Detector set | Heuristic, TF-IDF + logistic regression, embedding + XGBoost, fine-tuned transformer, LLM judge | You, 10 Nov |
| Application | Review summarizer (recommendation and ranking are out of scope for the first study) | Default, workflow Step 0 |
| Unit of detection | One review; multi-review contexts are used for the impact experiment | Default, workflow Step 0 |
| Language | English only; the mixed-language test (A-Z experiment E6) is dropped | Default |
| Hybrid detector, internal-state detector | Dropped | Follows from the detector decision |

The rows marked "Default" are my choices where the documents left room. Change any of them and I will update the rest of the file to match.

## 3. Research questions

| RQ | Question | Contribution |
|---|---|---|
| RQ1 | Which injection strategies and attacker goals can be embedded into real product reviews so that the result is varied, realistic, and clearly labeled? | Dataset |
| RQ2 | Do the injected reviews change LLM-generated summaries, and how does this depend on strategy, goal, number of injected reviews, and position? | Dataset |
| RQ3 | How well do representative detectors separate injected from clean reviews, and how does performance differ across strategies and held-out payload sources? | Benchmark |

## 4. Data sources

| Role | Source | License | Audit result |
|---|---|---|---|
| Benign reviews | `jhan21/amazon-beauty-reviews-dataset` | CC0 | 701,528 reviews; 3,206 products have at least 20 clean reviews |
| Payloads | BIPIA text attacks (`microsoft/BIPIA`, pinned commit) | MIT | 150 generic payloads; 3 categories dropped (malware, scam, misinformation) |
| Payloads | `deepset/prompt-injections` (label 1 only) | Apache-2.0 | 263 label-1 rows; 30 kept after reading all candidates by hand (political or offensive content, non-English text and spliced sentences removed) |
| Payloads | `Lakera/gandalf_ignore_instructions` | MIT | 1,000 "ignore instructions" prompts |
| Payloads | `review_specific_v1`, written for this project | Own | 160 payloads: 40 each for promote, demote, suppress, insert |

Rejected after the audit: PromptShield (full prompts with no separable payload and no source column), `zachz/promptinjectionbenchmark` (not found), InjecAgent and LLMail-Inject (tool-action attacks, which mean nothing to a summarizer without tools), HackAPrompt (gated).

The four payload sources make leave-one-dataset-out possible.

## 5. Unified taxonomy

The three documents used three different taxonomies. This one replaces them. Each injected review gets one value on each of four independent axes.

| Axis | Values | Replaces |
|---|---|---|
| `attack_goal` | promote, demote, suppress, insert, disrupt, other | Review's 3 goals, workflow's 5, A-Z's 7 |
| `embedding_strategy` | append, prepend, mid_insertion, delimiter_spoofing, semantic_camouflage | Proposal's strategies; "fake authority" in A-Z is delimiter_spoofing; "camouflaged" is semantic_camouflage |
| `obfuscation` | none, typo, unicode, encoding | Workflow Step 4; "obfuscated" type in A-Z |
| `payload_source` | name of the corpus the payload came from | New; needed for leave-one-dataset-out |

Rating, ranking, and sentiment manipulation from the A-Z guideline all map to **promote** or **demote**. Task redirection and override map to **disrupt**.

**Source and goal are confounded.** The promote, demote and suppress goals come only from `review_specific_v1`, and the corpora supply only disrupt, insert and other. Holding out `review_specific_v1` in leave-one-dataset-out therefore tests transfer from generic attacks to review-specific ones, which is a result worth reporting, but a difference between sources cannot be separated from a difference between goals. State this as a limitation.

**Injected rows per source:** 500 from `review_specific_v1` (125 per goal), 205 BIPIA, 205 Gandalf, 90 deepset. The deepset fold of leave-one-dataset-out is small (30 distinct payloads), so report it with that caveat.

## 6. Schema

One naming scheme, replacing `injection_label` (workflow) and the mixed names in the A-Z guideline.

| Field | Type | Rule |
|---|---|---|
| `review_id` | string | Unique, never reused |
| `source_row_id` | string | Traces to the immutable source file |
| `product_id` | string | Required for building contexts |
| `review_text` | string | Final text (benign or injected) |
| `original_text` | string | Clean text before injection; equals `review_text` for benign rows |
| `rating` | int | Original, never changed |
| `is_injection` | 0/1 | 0 benign, 1 injected |
| `hard_benign` | 0/1 | 1 for benign reviews with imperatives, quotes, "ignore", capitals, URLs |
| `attack_goal` | enum | Section 5; null for benign |
| `embedding_strategy` | enum | Section 5; null for benign |
| `obfuscation` | enum | Section 5; null for benign |
| `position` | enum | beginning, middle, end; null for benign |
| `payload_id` | string | ID of the curated payload; null for benign |
| `payload_source` | string | Corpus name; null for benign |
| `target_span` | string | Exact injected text |
| `span_start`, `span_end` | int | Character offsets of `target_span` in `review_text` |
| `split` | enum | train, validation, test |
| `carrier_review_id` | string | For injected rows, the `review_id` the clean text had in the benign pool |

Impact results live in a separate file keyed by `context_id`, with three fields kept apart as the A-Z guideline requires: `injection_present`, `injection_detected`, `injection_successful`.

## 7. Workflow changes

The ten steps of the workflow manual stand, with these changes.

| Step | Change |
|---|---|
| 3, Attack catalogue | Replaced by **payload curation**: pull payloads from the corpora, deduplicate, remove anything requesting real secrets or harmful actions, map each to an `attack_goal`, record `payload_source`, then run the goal coverage check from Section 5. The review-specific payloads are a fixed written set of 160, not templates. |
| 4, Injection generation | Unchanged in method. The "natural, disguised, obfuscated" difficulty levels become the `embedding_strategy` and `obfuscation` axes. |
| 7, Splits | See Section 8. |
| A-Z step G, Templates | Dropped (same reason as Step 3). |
| A-Z step S, Hybrid detector | Dropped. |

Hard-benign reviews stay at the workflow's ratio of at least 1 per 5 ordinary benign reviews.

## 8. Splits

| Split | Rule | Purpose |
|---|---|---|
| In-distribution | 70/15/15, grouped so that a source review and a payload never appear on both sides | Baseline |
| Leave-one-dataset-out | Train on all payload corpora but one, test on the held-out corpus; repeat per corpus | Main generalization test (RQ3) |
| Held-out strategy | Train on append, prepend, mid_insertion; test on delimiter_spoofing and semantic_camouflage | Strategy generalization |
| Held-out obfuscation | Train on `none`; test on typo, unicode, encoding | Obfuscation robustness |

This replaces the "unseen-attack" and "group" splits of the workflow and the seven test sets of the A-Z guideline. Cross-template splits no longer apply because there are no templates.

## 9. Detectors

| Detector | Configuration to record |
|---|---|
| Heuristic | Regex and trigger-phrase list |
| TF-IDF + logistic regression | n-gram range, min/max document frequency, class weighting, seed |
| Embedding + XGBoost | Embedding model, classifier hyperparameters, seed |
| Fine-tuned transformer | Model (DeBERTa or MiniLM class), sequence length, batch size, learning rate, epochs, seed, hardware |
| LLM judge | Model, prompt, temperature 0, zero-shot and few-shot variants |

Thresholds are chosen on validation data only.

## 10. Metrics

| Group | Metrics |
|---|---|
| Detection | Precision, recall, F1, AUROC, AUPRC, FPR, FNR, TPR at 1% FPR; each broken down by goal, strategy, obfuscation, and payload source |
| Impact | Attack success rate per goal, never pooled into one score; compared between no defense (pipeline A) and detector-then-summarizer (pipeline B) |
| Cost | Latency and cost per review |

Accuracy is never reported alone. Pipelines C (span removal) and D (spotlighting) from the A-Z guideline are optional extensions, not part of the first study.

## 11. First-study size

About 1,200 benign reviews (1,000 from the 100 selected products plus 200 extra hard-benign) and 1,000 injected reviews, 200 human-validated samples with two annotators and reported agreement, and contexts of 5, 10, and 20 reviews with 0, 1, or 2 injected. Scale to 5,000+ once the pipeline is verified.

## 12. Open items

| Item | Needed from |
|---|---|
| Second annotator for the 200-sample validation | You |
| Exact models for the summarizer and the LLM judge (OpenAI, Gemini and Claude are available; total budget 50 USD) | To fix when the impact experiment is built |
| Compute available for transformer fine-tuning | You |
