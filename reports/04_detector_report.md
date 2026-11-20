# Step 6 report: detector benchmark

GPU available: True

| Setting | Train rows | Validation rows | Test injected | Test benign |
|---|---|---|---|---|
| in_distribution | 1534 | 336 | 150 | 180 |
| lodo:bipia | 1389 | 307 | 205 | 180 |
| lodo:deepset | 1471 | 321 | 90 | 180 |
| lodo:gandalf | 1399 | 298 | 205 | 180 |
| lodo:review_specific_v1 | 1183 | 262 | 500 | 180 |
| heldout_strategy | 1256 | 267 | 53 | 180 |
| heldout_obfuscation | 1338 | 288 | 53 | 180 |

## Results by setting

Thresholds are chosen on validation data (best F1) and then applied to the test rows. The two `heuristic_vigil` rows are the exception: they flag a review whenever any published rule fires, with nothing tuned on this dataset.

### in_distribution  (test: 150 injected, 180 benign)

| detector | precision | recall | f1 | auroc | auprc | fpr | tpr_at_1pct_fpr |
|---|---|---|---|---|---|---|---|
| heuristic_vigil | 1.000 | 0.020 | 0.039 | 0.510 | 0.465 | 0.000 | 0.020 |
| heuristic_vigil_nocase | 1.000 | 0.027 | 0.052 | 0.513 | 0.469 | 0.000 | 0.027 |
| heuristic_dataset_informed | 0.967 | 0.793 | 0.872 | 0.891 | 0.876 | 0.022 | 0.447 |
| tfidf_logreg | 0.851 | 0.873 | 0.862 | 0.941 | 0.948 | 0.128 | 0.700 |
| embedding_xgboost | 0.820 | 0.667 | 0.735 | 0.863 | 0.860 | 0.122 | 0.327 |
| finetuned_transformer | 0.986 | 0.973 | 0.980 | 0.995 | 0.996 | 0.011 | 0.953 |

### lodo:bipia  (test: 205 injected, 180 benign)

| detector | precision | recall | f1 | auroc | auprc | fpr | tpr_at_1pct_fpr |
|---|---|---|---|---|---|---|---|
| heuristic_vigil | 1.000 | 0.010 | 0.019 | 0.505 | 0.537 | 0.000 | 0.010 |
| heuristic_vigil_nocase | 1.000 | 0.010 | 0.019 | 0.505 | 0.537 | 0.000 | 0.010 |
| heuristic_dataset_informed | 0.974 | 0.741 | 0.842 | 0.863 | 0.869 | 0.022 | 0.341 |
| tfidf_logreg | 0.901 | 0.668 | 0.768 | 0.856 | 0.898 | 0.083 | 0.502 |
| embedding_xgboost | 0.891 | 0.595 | 0.713 | 0.848 | 0.873 | 0.083 | 0.244 |
| finetuned_transformer | 0.979 | 0.893 | 0.934 | 0.980 | 0.986 | 0.022 | 0.863 |

### lodo:deepset  (test: 90 injected, 180 benign)

| detector | precision | recall | f1 | auroc | auprc | fpr | tpr_at_1pct_fpr |
|---|---|---|---|---|---|---|---|
| heuristic_vigil | 1.000 | 0.011 | 0.022 | 0.506 | 0.341 | 0.000 | 0.011 |
| heuristic_vigil_nocase | 1.000 | 0.011 | 0.022 | 0.506 | 0.341 | 0.000 | 0.011 |
| heuristic_dataset_informed | 0.944 | 0.756 | 0.840 | 0.871 | 0.817 | 0.022 | 0.400 |
| tfidf_logreg | 0.738 | 0.844 | 0.788 | 0.925 | 0.900 | 0.150 | 0.567 |
| embedding_xgboost | 0.693 | 0.778 | 0.733 | 0.879 | 0.831 | 0.172 | 0.411 |
| finetuned_transformer | 0.946 | 0.967 | 0.956 | 0.998 | 0.996 | 0.028 | 0.900 |

### lodo:gandalf  (test: 205 injected, 180 benign)

| detector | precision | recall | f1 | auroc | auprc | fpr | tpr_at_1pct_fpr |
|---|---|---|---|---|---|---|---|
| heuristic_vigil | 1.000 | 0.088 | 0.161 | 0.544 | 0.574 | 0.000 | 0.088 |
| heuristic_vigil_nocase | 1.000 | 0.112 | 0.202 | 0.556 | 0.585 | 0.000 | 0.112 |
| heuristic_dataset_informed | 0.979 | 0.902 | 0.939 | 0.947 | 0.949 | 0.022 | 0.624 |
| tfidf_logreg | 0.942 | 0.556 | 0.699 | 0.870 | 0.903 | 0.039 | 0.488 |
| embedding_xgboost | 0.865 | 0.717 | 0.784 | 0.877 | 0.896 | 0.128 | 0.224 |
| finetuned_transformer | 0.980 | 0.956 | 0.968 | 0.988 | 0.992 | 0.022 | 0.922 |

### lodo:review_specific_v1  (test: 500 injected, 180 benign)

| detector | precision | recall | f1 | auroc | auprc | fpr | tpr_at_1pct_fpr |
|---|---|---|---|---|---|---|---|
| heuristic_vigil | 1.000 | 0.030 | 0.058 | 0.515 | 0.743 | 0.000 | 0.030 |
| heuristic_vigil_nocase | 1.000 | 0.030 | 0.058 | 0.515 | 0.743 | 0.000 | 0.030 |
| heuristic_dataset_informed | 0.990 | 0.780 | 0.872 | 0.883 | 0.938 | 0.022 | 0.386 |
| tfidf_logreg | 0.951 | 0.510 | 0.664 | 0.818 | 0.932 | 0.072 | 0.378 |
| embedding_xgboost | 0.936 | 0.560 | 0.701 | 0.801 | 0.921 | 0.106 | 0.202 |
| finetuned_transformer | 0.984 | 0.882 | 0.930 | 0.967 | 0.989 | 0.039 | 0.756 |

### heldout_strategy  (test: 53 injected, 180 benign)

| detector | precision | recall | f1 | auroc | auprc | fpr | tpr_at_1pct_fpr |
|---|---|---|---|---|---|---|---|
| heuristic_vigil | 1.000 | 0.019 | 0.037 | 0.509 | 0.242 | 0.000 | 0.019 |
| heuristic_vigil_nocase | 1.000 | 0.038 | 0.073 | 0.519 | 0.257 | 0.000 | 0.038 |
| heuristic_dataset_informed | 0.929 | 0.981 | 0.954 | 0.988 | 0.969 | 0.022 | 0.755 |
| tfidf_logreg | 0.583 | 0.792 | 0.672 | 0.895 | 0.813 | 0.167 | 0.566 |
| embedding_xgboost | 0.582 | 0.736 | 0.650 | 0.893 | 0.782 | 0.156 | 0.283 |
| finetuned_transformer | 0.914 | 1.000 | 0.955 | 0.999 | 0.997 | 0.028 | 0.981 |

### heldout_obfuscation  (test: 53 injected, 180 benign)

| detector | precision | recall | f1 | auroc | auprc | fpr | tpr_at_1pct_fpr |
|---|---|---|---|---|---|---|---|
| heuristic_vigil | 1.000 | 0.019 | 0.037 | 0.509 | 0.242 | 0.000 | 0.019 |
| heuristic_vigil_nocase | 1.000 | 0.019 | 0.037 | 0.509 | 0.242 | 0.000 | 0.019 |
| heuristic_dataset_informed | 0.918 | 0.849 | 0.882 | 0.919 | 0.853 | 0.022 | 0.472 |
| tfidf_logreg | 0.791 | 0.642 | 0.708 | 0.888 | 0.797 | 0.050 | 0.377 |
| embedding_xgboost | 0.659 | 0.509 | 0.574 | 0.858 | 0.692 | 0.078 | 0.321 |
| finetuned_transformer | 0.939 | 0.868 | 0.902 | 0.986 | 0.974 | 0.017 | 0.792 |

## F1 summary (rows = detector, columns = setting)

| detector | in_distribution | lodo:bipia | lodo:deepset | lodo:gandalf | lodo:review_specific_v1 | heldout_strategy | heldout_obfuscation |
|---|---|---|---|---|---|---|---|
| embedding_xgboost | 0.735 | 0.713 | 0.733 | 0.784 | 0.701 | 0.650 | 0.574 |
| finetuned_transformer | 0.980 | 0.934 | 0.956 | 0.968 | 0.930 | 0.955 | 0.902 |
| heuristic_dataset_informed | 0.872 | 0.842 | 0.840 | 0.939 | 0.872 | 0.954 | 0.882 |
| heuristic_vigil | 0.039 | 0.019 | 0.022 | 0.161 | 0.058 | 0.037 | 0.037 |
| heuristic_vigil_nocase | 0.052 | 0.019 | 0.022 | 0.202 | 0.058 | 0.073 | 0.037 |
| tfidf_logreg | 0.862 | 0.768 | 0.788 | 0.699 | 0.664 | 0.672 | 0.708 |

## Recall summary

| detector | in_distribution | lodo:bipia | lodo:deepset | lodo:gandalf | lodo:review_specific_v1 | heldout_strategy | heldout_obfuscation |
|---|---|---|---|---|---|---|---|
| embedding_xgboost | 0.667 | 0.595 | 0.778 | 0.717 | 0.560 | 0.736 | 0.509 |
| finetuned_transformer | 0.973 | 0.893 | 0.967 | 0.956 | 0.882 | 1.000 | 0.868 |
| heuristic_dataset_informed | 0.793 | 0.741 | 0.756 | 0.902 | 0.780 | 0.981 | 0.849 |
| heuristic_vigil | 0.020 | 0.010 | 0.011 | 0.088 | 0.030 | 0.019 | 0.019 |
| heuristic_vigil_nocase | 0.027 | 0.010 | 0.011 | 0.112 | 0.030 | 0.038 | 0.019 |
| tfidf_logreg | 0.873 | 0.668 | 0.844 | 0.556 | 0.510 | 0.792 | 0.642 |

## In-distribution breakdown (recall on injected rows, by attribute)

By `attack_goal`:

| attack_goal | n | embedding_xgboost | finetuned_transformer | heuristic_dataset_informed | heuristic_vigil | heuristic_vigil_nocase | tfidf_logreg |
|---|---|---|---|---|---|---|---|
| demote | 19 | 0.632 | 0.947 | 0.842 | 0.000 | 0.000 | 0.947 |
| disrupt | 37 | 0.595 | 0.973 | 0.595 | 0.000 | 0.000 | 0.757 |
| insert | 24 | 0.583 | 1.000 | 0.917 | 0.000 | 0.000 | 0.958 |
| other | 32 | 0.781 | 1.000 | 0.938 | 0.094 | 0.125 | 0.906 |
| promote | 19 | 0.789 | 1.000 | 0.737 | 0.000 | 0.000 | 0.895 |
| suppress | 19 | 0.632 | 0.895 | 0.789 | 0.000 | 0.000 | 0.842 |

By `embedding_strategy`:

| embedding_strategy | n | embedding_xgboost | finetuned_transformer | heuristic_dataset_informed | heuristic_vigil | heuristic_vigil_nocase | tfidf_logreg |
|---|---|---|---|---|---|---|---|
| append | 32 | 0.562 | 0.906 | 0.875 | 0.031 | 0.031 | 0.906 |
| delimiter_spoofing | 27 | 0.852 | 1.000 | 1.000 | 0.037 | 0.037 | 0.889 |
| mid_insertion | 28 | 0.393 | 0.964 | 0.571 | 0.000 | 0.000 | 0.750 |
| prepend | 37 | 0.757 | 1.000 | 0.622 | 0.027 | 0.027 | 0.838 |
| semantic_camouflage | 26 | 0.769 | 1.000 | 0.962 | 0.000 | 0.038 | 1.000 |

By `obfuscation`:

| obfuscation | n | embedding_xgboost | finetuned_transformer | heuristic_dataset_informed | heuristic_vigil | heuristic_vigil_nocase | tfidf_logreg |
|---|---|---|---|---|---|---|---|
| encoding | 13 | 1.000 | 0.923 | 1.000 | 0.000 | 0.000 | 1.000 |
| none | 97 | 0.588 | 0.979 | 0.763 | 0.021 | 0.031 | 0.876 |
| typo | 15 | 0.667 | 1.000 | 0.467 | 0.000 | 0.000 | 0.800 |
| unicode | 25 | 0.800 | 0.960 | 1.000 | 0.040 | 0.040 | 0.840 |

By `payload_source`:

| payload_source | n | embedding_xgboost | finetuned_transformer | heuristic_dataset_informed | heuristic_vigil | heuristic_vigil_nocase | tfidf_logreg |
|---|---|---|---|---|---|---|---|
| bipia | 31 | 0.613 | 1.000 | 0.645 | 0.000 | 0.000 | 0.742 |
| deepset | 12 | 0.583 | 0.917 | 0.583 | 0.000 | 0.000 | 0.833 |
| gandalf | 32 | 0.781 | 1.000 | 0.938 | 0.094 | 0.125 | 0.906 |
| review_specific_v1 | 75 | 0.653 | 0.960 | 0.827 | 0.000 | 0.000 | 0.920 |

By `position`:

| position | n | embedding_xgboost | finetuned_transformer | heuristic_dataset_informed | heuristic_vigil | heuristic_vigil_nocase | tfidf_logreg |
|---|---|---|---|---|---|---|---|
| beginning | 50 | 0.820 | 1.000 | 0.720 | 0.020 | 0.040 | 0.860 |
| end | 51 | 0.608 | 0.941 | 0.902 | 0.020 | 0.020 | 0.922 |
| middle | 49 | 0.571 | 0.980 | 0.755 | 0.020 | 0.020 | 0.837 |

False-positive rate on benign rows (hard-benign vs ordinary):

| benign_type | n | embedding_xgboost | finetuned_transformer | heuristic_dataset_informed | heuristic_vigil | heuristic_vigil_nocase | tfidf_logreg |
|---|---|---|---|---|---|---|---|
| hard_benign | 31 | 0.226 | 0.065 | 0.032 | 0.000 | 0.000 | 0.194 |
| ordinary | 149 | 0.101 | 0.000 | 0.020 | 0.000 | 0.000 | 0.114 |

## Time

| detector | train_plus_predict_seconds |
|---|---|
| heuristic_vigil | 0.005 |
| heuristic_vigil_nocase | 0.041 |
| heuristic_dataset_informed | 0.162 |
| tfidf_logreg | 0.642 |
| embedding_xgboost | 10.649 |
| finetuned_transformer | 99.560 |

Embedding time is not included for `embedding_xgboost` (embeddings are computed once for all rows).

## Configuration

| Item | Value |
|---|---|
| Seed | 42 |
| heuristic_vigil | Rules from github.com/deadbits/vigil-llm (commit f2b4c134), unchanged; written independently of this dataset |
| heuristic_vigil_nocase | Same rules, ignoring upper/lower case; no other change |
| heuristic_dataset_informed | 9 regex rules written by the dataset builder with knowledge of the injection patterns; treat as an upper bound, not a fair baseline |
| TF-IDF + LR | word 1-2 grams, min_df 2, sublinear tf, C=1.0, class_weight balanced |
| Embedding + XGBoost | sentence-transformers/all-MiniLM-L6-v2; 300 trees, depth 4, lr 0.1, subsample 0.8 |
| Fine-tuned transformer | distilroberta-base; 3 epochs, lr 3e-05, batch 16, max length 256 |
