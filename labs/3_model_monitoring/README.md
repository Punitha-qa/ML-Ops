# Program 3: Model Monitoring

Goal: compare the packaged model's performance on its original baseline and new labeled messages, then document whether a team should investigate and consider retraining.

## Before running

Complete [Program 1](../1_model_packaging/README.md). Program 2 introduces serving, but its API can be stopped while this batch evaluation runs. Run commands from the repository root with the virtual environment activated.

## What is monitored

This lab evaluates the saved model on two labeled CSV files. It is a batch model evaluation exercise, not a live traffic monitoring platform. It needs the true `spam` or `ham` label for each evaluated message.

- **Spam precision:** among messages predicted as spam, the fraction that really are spam. Low precision means more ordinary messages are flagged.
- **Spam recall:** among actual spam messages, the fraction caught by the model. Low recall means more spam is missed.
- **Confusion matrix:** rows are actual labels and columns are predicted labels, in `[ham, spam]` order. The four entries are `[[correct ham, ham flagged as spam], [missed spam, correct spam]]`.

Accuracy alone can hide missed spam when most messages are ham. The report includes accuracy, precision, recall and F1 along with class counts.

## Run the shift scenario

```bash
python labs/3_model_monitoring/monitor.py
```

The program compares `data/baseline.csv` with `data/new_messages.csv`, prints a report and writes `reports/monitoring.json`.

The new sample contains 40 synthetic teaching messages with newer phishing scenarios and a different class balance. It deliberately differs from the historical corpus. It is not actual future traffic and does not prove production drift. Precision is also affected by class balance. See [data documentation](../../data/README.md).

## Run a control comparison

```bash
python labs/3_model_monitoring/monitor.py --new-data data/new_same_distribution.csv --output reports/control.json
```

This uses a separate held-out sample from the same UCI source. It is a control, not the same messages as the baseline. Small metric changes are normal between samples.

## Read the decision

Default teaching policy:

- `INSUFFICIENT_DATA` if the new file has fewer than 30 rows.
- Otherwise, `INVESTIGATE_AND_CONSIDER_RETRAINING` if spam recall drops by **more than 0.10** (10 percentage points) or new precision is below **0.90**.
- Otherwise, `NO_THRESHOLD_ALERT`.

Example: baseline recall 0.95 and new recall 0.80 means a drop of 0.15, or 15 percentage points. It exceeds the default recall threshold. An alert supports investigation; it does not prove that retraining is the only remedy. No alert does not establish statistical equivalence or guarantee future performance.

Thresholds are configurable:

```bash
python labs/3_model_monitoring/monitor.py --max-recall-drop 0.05 --min-precision 0.95 --min-rows 30
```

The minimum row count is a simple classroom guard. A production policy needs adequate counts per class, uncertainty estimates and business costs. The script verifies training/baseline hashes and rejects new messages that overlap the training or baseline sets.

## When retraining is appropriate

Investigate data quality and label quality first. If new, correctly labeled patterns explain the errors, train a candidate on suitable new training examples. Compare it with the existing model on a separate held-out dataset. Promote a new version only if it meets agreed requirements, and retain a rollback path. The monitoring script does not automatically retrain or deploy a model.

Do not add this lab's evaluation examples to training and then claim improved performance on those same examples.

## Review

Open [the Program 3 group quiz](../../quiz/program-3-monitoring.html). Explain your retraining recommendation using the report's metrics and limitations.

Reference: [scikit-learn model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html).
