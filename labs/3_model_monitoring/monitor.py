"""Program 3: compare baseline and new labeled data and recommend investigation."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sms_mlops.common import ROOT, assert_disjoint, evaluate, file_hash, load_artifact, read_messages, save_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--new-data", type=Path, default=ROOT / "data/new_messages.csv")
    parser.add_argument("--max-recall-drop", type=float, default=0.10,
                        help="Absolute recall drop, e.g. 0.10 means 10 percentage points")
    parser.add_argument("--min-precision", type=float, default=0.90)
    parser.add_argument("--min-rows", type=int, default=30)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/monitoring.json")
    args = parser.parse_args()
    if not 0 <= args.max_recall_drop <= 1 or not 0 <= args.min_precision <= 1 or args.min_rows < 1:
        parser.error("Metric thresholds must be between 0 and 1; min-rows must be positive.")

    model, metadata = load_artifact()
    baseline_path = ROOT / "data/baseline.csv"
    train_path = ROOT / "data/train.csv"
    if file_hash(baseline_path) != metadata["baseline_data_sha256"] or file_hash(train_path) != metadata["training_data_sha256"]:
        raise ValueError("Training/baseline data changed since packaging. Restore the split or retrain.")
    train_text, _ = read_messages(train_path)
    original_text, original_labels = read_messages(baseline_path)
    new_text, new_labels = read_messages(args.new_data)
    assert_disjoint(train_text, new_text)
    assert_disjoint(original_text, new_text)
    original = evaluate(model, original_text, original_labels)
    new = evaluate(model, new_text, new_labels)
    recall_drop = original["spam_recall"] - new["spam_recall"]
    reasons = []
    if recall_drop > args.max_recall_drop:
        reasons.append(f"Spam recall dropped by {recall_drop * 100:.1f} percentage points.")
    if new["spam_precision"] < args.min_precision:
        reasons.append(f"New spam precision {new['spam_precision']:.1%} is below {args.min_precision:.1%}.")
    if len(new_labels) < args.min_rows:
        decision = "INSUFFICIENT_DATA"
    elif reasons:
        decision = "INVESTIGATE_AND_CONSIDER_RETRAINING"
    else:
        decision = "NO_THRESHOLD_ALERT"
    next_steps = {
        "INSUFFICIENT_DATA": "Collect more trusted labeled examples and check counts per class before deciding.",
        "INVESTIGATE_AND_CONSIDER_RETRAINING": "Investigate data and labels. Evaluate a retrained candidate on held-out data before promotion.",
        "NO_THRESHOLD_ALERT": "Continue monitoring. No teaching threshold was crossed in this sample.",
    }
    report = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "model_version": metadata["model_version"], "new_data_file": str(args.new_data),
        "new_data_sha256": file_hash(args.new_data),
        "baseline": original, "new": new, "recall_drop": recall_drop,
        "thresholds": {"max_recall_drop": args.max_recall_drop,
                       "min_precision": args.min_precision, "min_rows": args.min_rows},
        "decision": decision, "reasons": reasons,
        "next_step": next_steps[decision],
        "limitations": "Teaching thresholds, small samples and synthetic shift. No automatic retraining or deployment.",
    }
    save_json(args.output, report)
    print(json.dumps(report, indent=2))
    print(f"Saved report: {args.output}")


if __name__ == "__main__":
    main()
