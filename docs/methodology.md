# Methodology — the full measurement story

Numbers below are verified results from the private project; identifying details have been
genericized. Synthetic files in this repository demonstrate structure and formulas only.

## 1. Dataset and preparation

The analysis covered a two-month CRM export:

- **854 raw records**
- **138 merged-case duplicates identified**
- **716 distinct cases**
- **701 cases with usable classification text**

The public repository contains no production ticket text.

## 2. Taxonomy from clustering-assisted discovery

HDBSCAN over locally computed sentence embeddings grouped roughly 550 tickets into 31 semantic
clusters, while a large share remained unclustered. That long tail was treated as evidence for a
legitimate `Other` category rather than a reason to force every ticket into a named cluster.

Clusters plus expert review became a versioned taxonomy with:

- 24 product areas
- 24 feature workflows
- 14 issue types

The private taxonomy file contained three sheets:

1. `taxonomy` — one column per classification field
2. `decision_rules` — per-value adjudication guidance
3. `synonyms` — approved terminology mappings

A preflight validator rejected duplicates, near-duplicate spellings, missing required columns,
and dangling synonym targets. Decision rules rendered into the prompt so the labeling guide and
model instructions came from the same source.

## 3. Gold data

A seeded random sample of 100 tickets was manually labeled against the written rules using
`first_email_only` input.

Labeling conventions that mattered:

- Label the customer’s stated problem, not support’s eventual action
- Use `Other` for genuine one-offs rather than forcing the closest named category
- Reserve `Insufficient Information` for cases that cannot be classified from the available
  intake text
- Do not adjudicate defect versus user error from a first email, because root cause is usually a
  resolution fact

## 4. Metrics

### Per-field agreement

The percentage of scored tickets where the model and reviewer selected the same label for one
field.

### Aggregate field agreement

```text
correct individual field assignments / all scored field assignments
```

With three fields, 93 scored rows produced 279 individual decisions.

### Strict all-three match

A ticket counted as correct only when product area, feature workflow, and issue type all matched
the human labels.

### Distribution overlap

For each field and label:

```text
sum(min(human_count, model_count)) / total human labels
```

This measures whether the overall category mix is similar. It does not establish that the correct
label was attached to the correct ticket.

## 5. Benchmark lineage

| Iteration | Aggregate field agreement | What it taught |
|---|---:|---|
| v1 | 67.7% | The model never selected `Other`; one instruction forced the closest named label |
| v2 | 66.3% | A note rendered into the wrong field produced illegal values and exclusions |
| v3 | 64.6% | The fixed result remained statistically indistinguishable at the available sample size |
| Combined format | 64.2% | One response per ticket preserved performance while cutting calls by two-thirds |

The approximate margin of error was ±9 percentage points. By a decision rule agreed in advance,
prompt-wording iteration stopped. Further improvement would require more gold labels, richer input
context, a model change, or a hybrid method.

## 6. Validated combined-call result

The final combined-call benchmark produced:

- Product area: **75.3%**
- Feature workflow: **64.5%**
- Issue type: **52.7%**
- Aggregate field agreement: **64.2%**
- Strict all-three match: **33.3%**
- Distribution overlap: **81.0%**
- 93 scored rows
- 4 empty cases dropped
- 7 flagged rows excluded

## 7. Cost validation before scale

The per-field design required three calls per ticket. The combined format returned all three
labels in one JSON response.

For 701 tickets:

- Per-field design: 2,103 calls
- Combined design: 701 calls
- Reduction: **67%**

The combined format was benchmarked against the same gold sample before it was accepted for the
full-population run.

## 8. Scale replication

The full-population run classified 701 tickets:

- Approximately **$2** in model usage
- Zero API failures
- 33 rows flagged by automatic output checks
- 10.7% assigned insufficient-information labels, consistent with the sample’s 10–12% rate

That 10.7% result is a consistency check, not human verification of all 701 records.

## 9. Reliability lessons

- **Stage metadata records execution, never intent**
- **Paid or destructive verification uses fixtures unless explicitly approved**
- **Cleaning changes are versioned and can invalidate comparability**
- **Exclusions and failures are counted rather than silently removed**
- **Known limitations belong in the executive deliverable**

A long-standing text-cleaning bug that removed subject lines was discovered during the project.
Earlier runs were declared non-comparable instead of being silently mixed with the corrected
pipeline.

## 10. Interpretation

The system was strongest for:

- Aggregate volume intelligence
- Product-area classification
- Selected high-volume categories
- Taxonomy and reason-code discovery

It was not positioned for unattended per-ticket automation. One important confusion involved
access requests being interpreted as unexpected behavior. The combined volume of the two
categories was more dependable than the exact split.
