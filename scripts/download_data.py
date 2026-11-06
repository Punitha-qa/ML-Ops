"""Download the public UCI collection and make reproducible, disjoint splits."""
import io
import json
import urllib.request
import zipfile

from sklearn.model_selection import train_test_split

from sms_mlops.common import ROOT, assert_disjoint, file_hash, save_json, write_messages

URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"


def main():
    # Read named members instead of extracting untrusted ZIP paths.
    with urllib.request.urlopen(URL, timeout=60) as response:
        archive_bytes = response.read(5_000_001)
    if len(archive_bytes) > 5_000_000:
        raise ValueError("Unexpectedly large dataset download")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        raw = archive.read("SMSSpamCollection").decode("utf-8")
        original_readme = archive.read("readme").decode("latin-1")
    unique = {}
    raw_count = 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        label, text = line.split("\t", 1)
        text = text.strip()
        if label not in {"ham", "spam"} or not text:
            raise ValueError("Invalid UCI row")
        key = text.casefold()
        if key in unique and unique[key][1] != label:
            raise ValueError("Conflicting labels for a duplicate message")
        unique.setdefault(key, (text, label))
        raw_count += 1
    texts, labels = map(list, zip(*unique.values()))
    train_x, rest_x, train_y, rest_y = train_test_split(
        texts, labels, test_size=0.30, stratify=labels, random_state=42
    )
    baseline_x, control_x, baseline_y, control_y = train_test_split(
        rest_x, rest_y, test_size=0.50, stratify=rest_y, random_state=42
    )
    assert_disjoint(train_x, baseline_x)
    assert_disjoint(train_x, control_x)
    assert_disjoint(baseline_x, control_x)
    datasets = {
        "train.csv": (train_x, train_y),
        "baseline.csv": (baseline_x, baseline_y),
        "new_same_distribution.csv": (control_x, control_y),
    }
    manifest = {"source_url": URL, "random_seed": 42, "raw_rows": raw_count,
                "unique_messages": len(texts), "deduplication": "strip whitespace and casefold text", "files": {}}
    for filename, (x, y) in datasets.items():
        path = ROOT / "data" / filename
        write_messages(path, x, y)
        manifest["files"][filename] = {"rows": len(x), "spam_rows": y.count("spam"), "sha256": file_hash(path)}
    original_readme = "\n".join(line.rstrip() for line in original_readme.splitlines()) + "\n"
    (ROOT / "data/UCI-original-readme.txt").write_text(original_readme, encoding="utf-8")
    save_json(ROOT / "data/split_manifest.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
