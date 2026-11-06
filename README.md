# SMS Spam Filter: MLOps Labs

Build one Python project through three MLOps steps: save a trained model, serve it through an API and webpage, then monitor performance on new labeled examples. The model predicts `ham` (an ordinary message) or `spam`.

## Setup

Use **Python 3.12**. The labs have been run with Python 3.12 and the versions in `constraints.txt`. Run every command from the repository root.

```bash
git clone https://github.com/Punitha-qa/ML-Ops.git
cd ML-Ops
python3.12 -m venv .venv
```

Activate the environment on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell, create and activate it with:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Then install the project and pinned dependencies:

```bash
python -m pip install -c constraints.txt -e .
```

Internet is needed for initial package installation. Prepared CSVs are included, so training and monitoring work offline afterward. Cloud deployment is optional.

## Program flow

```text
Labeled SMS data
    ↓
1. Train text pipeline + classifier; save with joblib
    ↓
2. Load the artifact in FastAPI; call it from a webpage
    ↓
3. Compare baseline and new labeled data; review the monitoring decision
```

The saved pipeline includes text processing and the classifier so new messages go through the same fitted steps.

| Program | Guide | Main result |
| --- | --- | --- |
| 1 — Model Packaging | [Train, save and reload](labs/1_model_packaging/README.md) | A joblib artifact and metadata |
| 2 — Model Deployment | [Run the API and webpage](labs/2_model_deployment/README.md) | `/predict`, `/health`, `/docs` and a browser page |
| 3 — Model Monitoring | [Compare performance](labs/3_model_monitoring/README.md) | A JSON report and a retraining recommendation |

## Run the programs

```bash
python labs/1_model_packaging/train.py
python labs/1_model_packaging/predict.py "Can we meet for lunch at one?"
uvicorn app:app --app-dir labs/2_model_deployment --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000> while the server runs. Try `/docs` to call the API directly. Stop the server with Ctrl+C, then run:

```bash
python labs/3_model_monitoring/monitor.py
python labs/3_model_monitoring/monitor.py --new-data data/new_same_distribution.csv --output reports/control.json
```

The first monitoring command uses a deliberately different synthetic teaching sample. The second uses a separate held-out control sample from the original source. Each lab's guide explains its flow and expected output.

## Program 1 video

Watch [Program 1 explained](videos/program-1/program-1-explained.mp4) for a narrated walkthrough of the small beginner example, including training, saving, loading and prediction. [Video notes and captions](videos/program-1/README.md) are included. The full lab uses the larger dataset and additional evaluation checks.

## Group quizzes

After each program, download or clone the repository and open its HTML quiz in a browser:

- [Program 1 quiz](quiz/program-1-packaging.html)
- [Program 2 quiz](quiz/program-2-deployment.html)
- [Program 3 quiz](quiz/program-3-monitoring.html)

Each has six questions with explanations. With six groups, assign one question to each group. With five groups, use question six as a bonus. [The quiz hub](quiz/index.html) links them all. GitHub displays HTML as source unless you host it as a website; the quizzes run directly from the downloaded folder.

## Repository layout

```text
labs/1_model_packaging/   train.py, predict.py and guide
labs/2_model_deployment/  app.py, index.html and deployment guides
labs/3_model_monitoring/  monitor.py and guide
src/sms_mlops/           shared data, metrics and artifact helpers
data/                   prepared CSVs, provenance and attribution
quiz/                   three group quiz webpages
scripts/                data preparation and container entrypoint
tests/                  lifecycle verification
artifacts/              generated model and metadata (ignored by Git)
reports/                generated monitoring reports (ignored by Git)
```

## Data and scope

The project uses the historical [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection), attributed and documented in [data/README.md](data/README.md). Training, baseline and control sets are deduplicated and disjoint. The synthetic new-message sample demonstrates an evaluation alert; it does not establish real production drift.

This teaching implementation includes packaging and validation checks. A production system also needs an approved model registry, access control, operational monitoring and a release process. Use public or synthetic messages in this repository.

## Optional cloud deployment

Follow [Docker and cloud deployment instructions](labs/2_model_deployment/CLOUD.md) after the local API works. The guide includes prerequisites, public-access behavior, billing considerations and cleanup. Free compute does not guarantee signup without payment verification; check the provider's account requirements before the workshop.

## Verify the implementation

```bash
python -m pip install -c constraints.txt -e '.[test]'
python -m unittest discover -s tests -v
```

These checks train the pipeline, reload it in a new process, exercise API validation, detect a corrupt artifact and check monitoring decisions.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `python3.12` not found | Install Python 3.12, or use `py -3.12` on Windows. |
| `No module named sms_mlops` | Activate `.venv` and repeat installation from the repository root. |
| Missing artifact | Run Program 1's `train.py` first. |
| Runtime mismatch | Install using `constraints.txt`, then retrain in the environment used to serve the model. |
| Changed dataset hash | Restore the original splits or rerun training before monitoring. |
| Port 8000 is in use | Stop the old server or use `--port 8001`. |
| Page cannot reach `/predict` | Open the webpage through the running API's URL. |

## References

[Model persistence](https://scikit-learn.org/stable/model_persistence.html), [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/), and [classification metrics](https://scikit-learn.org/stable/modules/model_evaluation.html).
