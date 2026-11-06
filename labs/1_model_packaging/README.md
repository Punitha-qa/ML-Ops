# Program 1: Model Packaging

Goal: train an SMS spam filter, save it using joblib, and load it in a separate Python process to predict a message.

## Before running

Complete the [root setup](../../README.md#setup). Run every command below from the repository root with your virtual environment activated. The prepared CSV files are already in `data/`.

## First: where do the imported tools come from?

Python gives us a standard library. We also install libraries written by others and use helpers written for this workshop.

| Import | Comes from | Job in Program 1 |
|---|---|---|
| `Path` from `pathlib` | Python standard library; used in the beginner example | Handle folder and file paths |
| `json` | Python standard library | Format metrics and predictions as JSON text |
| `datetime`, `timezone` from `datetime` | Python standard library | Record the model's creation time in UTC |
| `argparse` | Python standard library | Read the prediction message from the command line |
| `joblib` | Separately installed joblib library | Save and reload the trained pipeline |
| `TfidfVectorizer` from `sklearn.feature_extraction.text` | scikit-learn's text feature tools | Convert messages into numerical features |
| `LogisticRegression` from `sklearn.linear_model` | scikit-learn's model algorithms | Learn to classify messages as spam or ham |
| `Pipeline` from `sklearn.pipeline` | scikit-learn's pipeline tools | Connect the text converter and classifier in order |
| Helpers from `sms_mlops.common` | Our own code in `src/sms_mlops/common.py` | Read data, evaluate, save metadata and check/load artifacts |

**scikit-learn** is the library's installation name; **`sklearn`** is its Python import name. Despite its name, `LogisticRegression` performs classification here.

For example:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
```

Read this as: “From scikit-learn's text feature tools, bring `TfidfVectorizer` into my program.”

`TfidfVectorizer`, `LogisticRegression` and `Pipeline` are classes: reusable definitions for creating objects. Writing `TfidfVectorizer()` creates a converter object. Creating the pipeline does not train it; `model.fit(train_text, train_labels)` trains its steps using our labeled examples.

For the small six-message walkthrough, start with [the beginner example](../../videos/program-1/example.py). It includes explanations beside every import.

## What the program does

1. `train.py` reads labeled training messages and the separate baseline evaluation set.
2. `TfidfVectorizer` learns a vocabulary and converts text into numbers using the training set.
3. `LogisticRegression` learns how those features relate to `spam` or `ham`.
4. A scikit-learn `Pipeline` keeps both fitted steps together.
5. The script evaluates the pipeline on baseline messages that it did not train on.
6. `joblib.dump` saves the whole pipeline to disk, along with a separate metadata JSON file.
7. `predict.py` starts another Python process, loads the artifact, and predicts a new message without calling `fit`.

While a program runs, the fitted objects live in its memory (RAM). A saved file remains on disk after the process exits. Loading recreates the fitted objects in memory so a new process can reuse them.

## Run

```bash
python labs/1_model_packaging/train.py
python labs/1_model_packaging/predict.py "Can we meet for lunch at one?"
python labs/1_model_packaging/predict.py "Congratulations! Claim your free prize now by calling us"
```

## Expected results

Training prints evaluation metrics and creates:

```text
artifacts/sms-spam-1.0.0.joblib
artifacts/sms-spam-1.0.0.metadata.json
```

Prediction prints JSON with `label` and `model_version`. For example:

```json
{"label": "ham", "model_version": "1.0.0"}
```

The model can make mistakes on new messages. Try editing a message and explain why a different prediction might occur.

## Why the extra metadata matters

The JSON records the version, dependency versions, artifact hash, dataset hashes and baseline metrics. This helps identify which model is running and reconstruct its environment. This workshop deliberately rejects a mismatched loading environment. Changing a dependency requires retraining the artifact in that environment.

Only load joblib artifacts from a trusted training process. Loading can execute Python code. A matching checksum detects accidental changes but does not establish that an unknown file is trustworthy. The project ignores generated artifacts in Git so students train their own rather than downloading an executable serialized object.

The teaching version stays at `1.0.0`; rerunning training replaces that local artifact. A production workflow would assign a new version and retain approved older releases.

## Review and continue

Open [the Program 1 group quiz](../../quiz/program-1-packaging.html) locally in a browser, then continue to [Program 2](../2_model_deployment/README.md).

Reference: [scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html).
