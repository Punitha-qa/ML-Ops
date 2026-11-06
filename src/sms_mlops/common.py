"""Data, metrics and artifact checks shared by the labs.

Run lab commands from the repository root, or set WORKSHOP_ROOT explicitly.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import platform
from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

ROOT = Path(os.environ.get("WORKSHOP_ROOT", ".")).resolve()
DEFAULT_MODEL = ROOT / "artifacts" / "sms-spam-1.0.0.joblib"
LABELS = ["ham", "spam"]


def read_messages(path: Path) -> tuple[list[str], list[str]]:
    """Read a CSV, rejecting bad labels and blank messages before training."""
    messages, labels = [], []
    seen = set()
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["label", "message"]:
            raise ValueError(f"{path}: expected CSV header label,message")
        for line, row in enumerate(reader, start=2):
            if None in row or row.get("label") not in LABELS or not row.get("message", "").strip():
                raise ValueError(f"{path}:{line}: invalid label or message")
            key = row["message"].strip().casefold()
            if key in seen:
                raise ValueError(f"{path}:{line}: duplicate message text")
            seen.add(key)
            labels.append(row["label"])
            messages.append(row["message"].strip())
    if set(labels) != set(LABELS):
        raise ValueError(f"{path}: include labeled examples of both ham and spam")
    return messages, labels


def write_messages(path: Path, messages: list[str], labels: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["label", "message"])
        writer.writerows(zip(labels, messages))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_versions() -> dict[str, str]:
    return {
        "python": ".".join(platform.python_version_tuple()[:2]),
        **{name: importlib.metadata.version(name) for name in
           ["scikit-learn", "joblib", "numpy", "scipy"]},
    }


def evaluate(model, messages: list[str], labels: list[str]) -> dict:
    predictions = model.predict(messages)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average="binary", pos_label="spam", zero_division=0
    )
    return {
        "rows": len(labels), "spam_rows": labels.count("spam"),
        "accuracy": float(accuracy_score(labels, predictions)),
        "spam_precision": float(precision), "spam_recall": float(recall),
        "spam_f1": float(f1),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=LABELS).tolist(),
        "confusion_matrix_labels": LABELS,
    }


def save_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def load_artifact(path: Path = DEFAULT_MODEL):
    """Load ONLY artifacts created by a trusted training process.

    The checksum detects accidental changes. It does not make an untrusted
    joblib file safe: an attacker can also replace the metadata.
    """
    metadata_path = path.with_suffix(".metadata.json")
    if not path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError("Run Program 1 train.py first to create the artifact and metadata.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if file_hash(path) != metadata["artifact_sha256"]:
        raise ValueError("Artifact checksum mismatch. Restore or retrain the trusted artifact.")
    if runtime_versions() != metadata["runtime"]:
        raise ValueError("Training and loading environments differ. Recreate the training environment or retrain.")
    return joblib.load(path), metadata


def assert_disjoint(first: list[str], second: list[str]) -> None:
    overlap = {x.casefold().strip() for x in first} & {x.casefold().strip() for x in second}
    if overlap:
        raise ValueError(f"Data leakage: {len(overlap)} messages occur in both datasets.")
