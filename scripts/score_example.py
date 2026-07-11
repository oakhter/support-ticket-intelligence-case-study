#!/usr/bin/env python3
"""Compute three-field benchmark metrics from the synthetic example files."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"

FIELD_MAP = {
    "human_product_area_l1": "llm_product_area",
    "human_feature_workflow_l1": "llm_feature_workflow",
    "issue_type": "llm_issue_type",
}

DISPLAY_NAMES = {
    "human_product_area_l1": "product_area",
    "human_feature_workflow_l1": "feature_workflow",
    "issue_type": "issue_type",
}


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def distribution_overlap(
    gold_values: Iterable[str], predicted_values: Iterable[str]
) -> Tuple[int, int, float]:
    gold_counts = Counter(gold_values)
    predicted_counts = Counter(predicted_values)
    labels = gold_counts.keys() | predicted_counts.keys()
    hits = sum(min(gold_counts[label], predicted_counts[label]) for label in labels)
    total = sum(gold_counts.values())
    return hits, total, hits / total if total else 0.0


def main() -> None:
    gold = read_csv(EXAMPLES / "synthetic_gold.csv")
    predictions = read_csv(EXAMPLES / "synthetic_predictions.csv")
    pred_by_id = {row["case_id"]: row for row in predictions}

    joined = [
        (row, pred_by_id[row["case_id"]])
        for row in gold
        if row["case_id"] in pred_by_id
    ]
    if not joined:
        raise RuntimeError("No matching case_id values found.")

    field_correct_total = 0
    overlap_hits_total = 0
    field_decisions = len(joined) * len(FIELD_MAP)

    print(f"rows scored: {len(joined)}")
    print("fields: product_area, feature_workflow, issue_type\n")

    for gold_field, prediction_field in FIELD_MAP.items():
        correct = sum(
            gold_row[gold_field] == pred_row[prediction_field]
            for gold_row, pred_row in joined
        )
        field_correct_total += correct

        hits, total, rate = distribution_overlap(
            (gold_row[gold_field] for gold_row, _ in joined),
            (pred_row[prediction_field] for _, pred_row in joined),
        )
        overlap_hits_total += hits

        print(
            f"{DISPLAY_NAMES[gold_field]:<18} "
            f"accuracy={correct}/{len(joined)} ({correct / len(joined):.1%})  "
            f"distribution_overlap={hits}/{total} ({rate:.1%})"
        )

    strict_correct = sum(
        all(gold_row[g] == pred_row[p] for g, p in FIELD_MAP.items())
        for gold_row, pred_row in joined
    )

    print("\nheadline metrics")
    print(
        f"aggregate field accuracy : {field_correct_total}/{field_decisions} "
        f"({field_correct_total / field_decisions:.1%})"
    )
    print(
        f"strict all-three match   : {strict_correct}/{len(joined)} "
        f"({strict_correct / len(joined):.1%})"
    )
    print(
        f"distribution overlap     : {overlap_hits_total}/{field_decisions} "
        f"({overlap_hits_total / field_decisions:.1%})"
    )


if __name__ == "__main__":
    main()
