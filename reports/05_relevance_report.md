# Step 7 report: relevance of the injected instruction to its review

These labels are computed from columns already in `dataset_v1.csv`; the dataset is unchanged.

## Topic relevance

`on_topic` = the instruction is about the product, the reviews or the summary (the review-specific payloads).
`off_topic` = generic instructions from the three corpora.

| topic_relevance | bipia | deepset | gandalf | review_specific_v1 |
|---|---|---|---|---|
| off_topic | 205 | 90 | 205 | 0 |
| on_topic | 0 | 0 | 0 | 500 |

## Direction match (promote, suppress and demote attacks only)

`consistent` = the attack pushes the same way as the reviewer's star rating (for example a promote attack in a 4-5 star review).
`contradictory` = it pushes the opposite way (for example a promote attack in a 1-2 star review).

| attack_goal | consistent | contradictory | neutral_review | not_applicable |
|---|---|---|---|---|
| demote | 26 | 86 | 13 | 0 |
| disrupt | 0 | 0 | 0 | 244 |
| insert | 0 | 0 | 0 | 176 |
| other | 0 | 0 | 0 | 205 |
| promote | 84 | 28 | 13 | 0 |
| suppress | 87 | 26 | 12 | 0 |

Among directional attacks in non-neutral reviews, 58.5% are consistent with the review.

## Annotation sample

200 rows: 100 injected (20 per strategy), 40 hard-benign, 60 ordinary benign, shuffled.

Injected rows in the sample, by computed relevance (the annotators' Q3 and Q4 answers will be compared with these):

| topic_relevance | consistent | contradictory | neutral_review | not_applicable |
|---|---|---|---|---|
| off_topic | 0 | 0 | 0 | 46 |
| on_topic | 20 | 17 | 2 | 15 |
