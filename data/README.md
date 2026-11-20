# Data

The data files are produced by the notebooks and are not stored in this folder by default.
After running the pipeline, copy these files here from the downloaded zip archives:

| File | Produced by | Contents |
|---|---|---|
| `benign_pool.csv` | `02_benign_pool.ipynb` | 2,000 clean reviews from 100 products (20 each) |
| `hard_benign_extra.csv` | `02_benign_pool.ipynb` | 300 extra hard-benign reviews from other products |
| `payload_pool.csv` | `03_build_dataset.ipynb` | 1,250 curated payloads with source, goal and split |
| `dataset_v1.csv` | `03_build_dataset.ipynb` | Final dataset: 2,200 reviews (1,200 benign, 1,000 injected) |
| `relevance_labels.csv` | `05_annotation.ipynb` | Computed topic and direction labels for the injected reviews |
| `results_detection.csv`, `results_breakdown.csv`, `predictions.csv` | `04_detectors.ipynb` | Detector results and per-review predictions |

Do **not** add `annotation_key_DO_NOT_SHARE.csv` or `annotation_row_key_DO_NOT_SHARE.csv`. They contain the answers for the
human annotation and are excluded by `.gitignore`.

## Schema of `dataset_v1.csv`

| Column | Meaning |
|---|---|
| `review_id` | Unique ID (`R`/`H` = benign, `I` = injected) |
| `carrier_review_id` | For injected rows, the ID the clean review had in the benign pool |
| `source_row_id` | Row number in the original Amazon file |
| `product_id` | Amazon `parent_asin` |
| `review_text` | Final text (benign or injected) |
| `original_text` | Clean text before injection |
| `rating` | Original star rating |
| `is_injection` | 1 = injected, 0 = benign |
| `hard_benign` | 1 = genuine review that looks instruction-like |
| `attack_goal` | promote, demote, suppress, insert, disrupt, other |
| `embedding_strategy` | append, prepend, mid_insertion, delimiter_spoofing, semantic_camouflage |
| `obfuscation` | none, typo, unicode, encoding |
| `position` | beginning, middle, end |
| `payload_id`, `payload_source` | Payload identifier and source corpus |
| `target_span`, `span_start`, `span_end` | Exact inserted text and its character offsets |
| `split` | train, validation, test |

## Sources and licenses

| Source | License | Use |
|---|---|---|
| [jhan21/amazon-beauty-reviews-dataset](https://huggingface.co/datasets/jhan21/amazon-beauty-reviews-dataset) | CC0-1.0 | Benign reviews |
| [microsoft/BIPIA](https://github.com/microsoft/BIPIA) (commit a004b69) | MIT, Copyright (c) Microsoft Corporation | Payloads |
| [deepset/prompt-injections](https://huggingface.co/datasets/deepset/prompt-injections) | Apache-2.0 | Payloads (30 hand-picked) |
| [Lakera/gandalf_ignore_instructions](https://huggingface.co/datasets/Lakera/gandalf_ignore_instructions) | MIT | Payloads |
| `review_specific_v1` | Written for this project | Payloads |
| [deadbits/vigil-llm](https://github.com/deadbits/vigil-llm) (commit f2b4c134) | Apache-2.0 | Rules used by the `heuristic_vigil` detector |

Redistributed payloads keep the licenses of their original sources.
