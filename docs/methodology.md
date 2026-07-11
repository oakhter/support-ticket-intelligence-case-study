# Methodology

## Dataset and scope

The private analysis covered a two-month CRM export:

- 854 raw records
- 138 merged duplicates identified
- 716 distinct cases
- 701 cases containing usable classification text

No private ticket text is included in this repository.

## Taxonomy discovery

Sentence embeddings and HDBSCAN were used to surface repeated themes. Clustering was treated as
a discovery aid rather than a final classifier. A large unclustered tail supported a legitimate
`Other` category rather than forcing every ticket into a named group.

The final measured model classified three dimensions:

1. Product area
2. Feature workflow
3. Issue type

## Human benchmark

A seeded sample of 100 tickets was manually labeled using the same first-email input shown to the
model. The benchmark measured agreement separately for all three fields.

## Metrics

### Aggregate field accuracy

Correct individual field assignments divided by all scored field assignments.

### Strict exact match

The percentage of tickets where product area, feature workflow, and issue type all matched the human reviewer.

### Distribution overlap

For every field and label, the smaller of the human and model counts was summed and divided by the human-label total. This measures similarity of the overall category mix, not ticket-level
correctness.

## Measured outcome

The validated combined-call format produced:

- Product area: 75.3%
- Feature workflow: 64.5%
- Issue type: 52.7%
- Aggregate field agreement: 64.2%
- Strict all-three match: 33.3%
- Distribution overlap: 81.0%

The model was therefore positioned for aggregate support-volume intelligence rather than unattended per-ticket automation.

## Cost optimization

The consolidated format reduced model calls from 2,103 to 701 for the full population. Its benchmark result differed by only 0.4 percentage points from the per-field format.
