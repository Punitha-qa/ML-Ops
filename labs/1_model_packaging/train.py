"""Program 1: train one pipeline, evaluate it, then package it with joblib.

Import guide: Python's standard library comes with Python. joblib and
scikit-learn are installed dependencies; scikit-learn is imported as sklearn.
sms_mlops is our own workshop package, stored in src/sms_mlops/.
"""
# json (standard library): format the printed metrics as JSON text.
import json
# datetime (standard library): record when the model was created, in UTC.
from datetime import datetime, timezone

# joblib (installed library): save the fitted pipeline with joblib.dump.
import joblib
# scikit-learn's text tools: convert messages into numerical features.
from sklearn.feature_extraction.text import TfidfVectorizer
# scikit-learn's linear models: learn to classify those features as spam or ham.
# LogisticRegression performs classification here, despite its name.
from sklearn.linear_model import LogisticRegression
# scikit-learn's pipeline tools: connect the converter and classifier in order.
# These three classes create objects with (); model.fit below trains them.
from sklearn.pipeline import Pipeline

# Our workshop helpers: paths, CSV reading, split checks, evaluation, hashes,
# dependency versions and saving metadata. These are functions/constants we wrote.
from sms_mlops.common import (
    ROOT, DEFAULT_MODEL, assert_disjoint, evaluate, file_hash,
    read_messages, runtime_versions, save_json,
)


def main():
    train_path = ROOT / "data/train.csv"
    baseline_path = ROOT / "data/baseline.csv"
    train_text, train_labels = read_messages(train_path)
    baseline_text, baseline_labels = read_messages(baseline_path)
    assert_disjoint(train_text, baseline_text)

    # fit learns vocabulary/weights using training data only.
    model = Pipeline([
        ("text", TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=2)),
        ("classifier", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
    ])
    model.fit(train_text, train_labels)
    metrics = evaluate(model, baseline_text, baseline_labels)

    DEFAULT_MODEL.parent.mkdir(parents=True, exist_ok=True)
    # This single file contains BOTH the fitted vectorizer and classifier.
    joblib.dump(model, DEFAULT_MODEL, compress=3)
    metadata = {
        "model_version": "1.0.0", "created_at": datetime.now(timezone.utc).isoformat(),
        "runtime": runtime_versions(), "artifact_sha256": file_hash(DEFAULT_MODEL),
        "training_data_sha256": file_hash(train_path),
        "baseline_data_sha256": file_hash(baseline_path),
        "training_rows": len(train_text), "baseline_metrics": metrics,
        "source": "UCI SMS Spam Collection, deduplicated, stratified split seed 42",
    }
    save_json(DEFAULT_MODEL.with_suffix(".metadata.json"), metadata)
    print(f"Saved: {DEFAULT_MODEL}")
    print(json.dumps(metrics, indent=2))
    print("Next: run predict.py in a NEW Python process.")


if __name__ == "__main__":
    main()
