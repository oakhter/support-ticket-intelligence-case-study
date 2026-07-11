# Technical Overview

This document summarizes the private implementation without exposing internal source code,
customer data, company names, case identifiers, or proprietary taxonomy content.

## Pipeline tracks

The system had two deliberately separate tracks.

### Benchmark track

```text
ingest → sample → human review → validate → gold → classify → score → benchmark
```

This path produced human-reviewed labels and measured model output against those labels.

### Bulk track

```text
ingest → bulk_classify → enriched CSV + distribution report
```

This path classified every ingested record but did not calculate accuracy, because the full
population was not manually labeled.

## Three-field classification contract

Every classified ticket produced exactly three model fields:

- `llm_product_area`
- `llm_feature_workflow`
- `llm_issue_type`

The matching human benchmark fields were:

- `human_product_area_l1`
- `human_feature_workflow_l1`
- `issue_type`

The synthetic examples in this repository preserve that same three-field structure.

## Input modes

The private pipeline supported:

- `first_email_only`: subject, description, and first inbound customer message
- `full_thread`: cleaned conversation thread plus a resolution proxy

The benchmark used `first_email_only` so reviewers and the model judged the same intake
information and did not use hindsight from the eventual resolution.

## Taxonomy system

The private taxonomy was an XLSX file with three sheets:

1. `taxonomy`: one column per classification field
2. `decision_rules`: per-value adjudication guidance
3. `synonyms`: approved spelling and terminology mappings

Before classification, a preflight check rejected missing required columns, duplicate values,
near-duplicate spellings, and dangling synonym targets. Decision rules were rendered into the
model prompt so the human labeling guide and the model instructions came from the same source.

A sanitized example is available at
[`examples/sample_taxonomy.xlsx`](../examples/sample_taxonomy.xlsx).

## Call modes

- `per_field`: three API calls per ticket, one for each field
- `combined`: one JSON response containing all three fields

The combined mode was validated on the same gold sample before it was treated as equivalent for
the full-population run.

## Scoring

The evaluator calculated:

- Per-field exact-match agreement
- Aggregate agreement across all three field decisions
- Strict all-three-fields exact match for each ticket
- Distribution overlap for each field and overall

The public script in `scripts/score_example.py` implements these core formulas against synthetic
gold and prediction CSVs.

## Run integrity and provenance

Each report recorded the model, call mode, prompt version, taxonomy filename and hash, sample seed,
input mode, cleaning version, and row counts. Run state was designed to record only stages that
actually executed.

## Reliability boundaries

The private implementation was a production-style internal prototype, not a deployed multi-user
service. Known gaps included incomplete automated test coverage, imperfect PII detection, and
unpopulated database tables for some derived artifacts. These limitations are intentionally not
hidden in the case study.
