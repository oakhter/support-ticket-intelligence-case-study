# Technical overview

This document summarizes the private implementation without exposing internal code, customer
data, proprietary taxonomy values, or company identifiers.

## Pipeline tracks

### Benchmark track

```text
ingest → sample → human review → validate → gold → classify → score → benchmark
```

The benchmark path produced a human-labeled evaluation set and compared model predictions against
that set.

### Bulk track

```text
ingest → cost estimate → explicit confirmation → classify all → enriched CSV → distribution report
```

The bulk path classified the full ingested population but did not calculate full-population
accuracy because those records were not manually labeled.

## Major components

- **Adapter and ingest:** normalize exported CRM records, identify merged duplicates, parse email
  threads, and build classification-ready records
- **Cleaning:** remove quoted history, boilerplate, signatures, and known empty-message patterns
- **PII scrubbing:** Microsoft Presidio applied before model classification
- **Run store:** PostgreSQL tables for runs, cases, and stage state
- **Taxonomy service:** load values, rules, and synonyms; validate before use
- **Classifier:** support per-field and combined JSON call modes
- **Evaluator:** exact-match accuracy, strict all-three match, and distribution overlap
- **Bulk runner:** explicit cost confirmation, retries, flagged degradation, and drift reporting
- **Interface:** FastAPI + HTMX for stage execution, run status, previews, and exports

## Three-field classification contract

Model fields:

- `llm_product_area`
- `llm_feature_workflow`
- `llm_issue_type`

Human benchmark fields:

- `human_product_area_l1`
- `human_feature_workflow_l1`
- `issue_type`

A taxonomy missing any required field failed preflight.

## Input modes

- `first_email_only`: subject, description, and first inbound customer message
- `full_thread`: cleaned thread plus resolution proxy

The benchmark used `first_email_only` so reviewers and the model saw the same intake evidence.

## Taxonomy system

The private XLSX taxonomy contained:

- `taxonomy`
- `decision_rules`
- `synonyms`

Validation checked required columns, empty columns, duplicate values, conflicting canonical
spellings, and invalid synonym mappings. Rules were rendered directly into both per-field and
combined prompts.

## Call modes

### Per-field

Three model calls per ticket, one for each classification field.

### Combined

One JSON response containing all three fields. Defensive parsing and taxonomy-conformance checks
could flag a row without terminating the run.

## Scoring

The evaluator reported:

- Per-field exact-match accuracy
- Aggregate field accuracy
- Strict exact match across all three fields
- Distribution overlap by field and overall
- Scored and excluded row counts

## Provenance

Benchmark reports recorded:

- Model and prompt version
- Call mode
- Taxonomy filename and SHA-256 hash
- Gold and scored row counts
- Input mode
- Sample seed
- Cleaning version
- Flagged and empty-case exclusions

## Reliability boundaries

The system was a production-style internal prototype, not a hardened multi-user service. Known
gaps included incomplete automated tests, imperfect PII detection, manual export-based ingestion,
and some derived artifacts remaining file-based rather than fully persisted in the database.
