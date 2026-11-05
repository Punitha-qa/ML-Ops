# SMS Spam Filter: MLOps Labs

This repository follows one Python project through three MLOps steps: package a trained model, serve it through an API, and monitor its performance. Use the labs in order; each one uses the artifact or service created by the previous lab.

## Project flow

```text
Labeled SMS data
    ↓
Train text-processing pipeline + classifier
    ↓
1. Package with joblib → saved model artifact
    ↓
2. Serve with FastAPI → prediction API → simple webpage
    ↓
3. Compare original and new labeled data → decide whether to retrain
```

The model predicts `ham` (ordinary message) or `spam`. The text-processing step and classifier are kept together so new messages are handled the same way as training messages.

## Labs

| Program | What it does | Main result |
| --- | --- | --- |
| **1 — Model Packaging** | Save the fitted text pipeline and classifier with `joblib`, load them in a fresh Python process, and predict on a new message. | A versioned model artifact, such as `sms-spam-1.0.0.joblib` |
| **2 — Model Deployment** | Load the artifact in a FastAPI app, accept a message through `POST /predict`, and display the response on a simple webpage. | A local API and webpage; an optional cloud deployment |
| **3 — Model Monitoring** | Compare precision and recall on the original and new labeled message sets, inspect changes, and decide whether retraining is warranted. | A monitoring report and a documented retraining decision |

Each lab folder will contain its own instructions and exact run commands. Start with Program 1, then continue to 2 and 3.

## Group quizzes

Use the [lab quiz hub](quiz/index.html) after each program. Each lab has six questions for group discussion, with feedback and explanations. Assign one question to each of six groups, or use the sixth question as a bonus with five groups. The quiz pages run locally in a browser and need no Python packages or account.

## Repository layout

```text
labs/
  1_model_packaging/
  2_model_deployment/
  3_model_monitoring/
```

The runnable files and lab-specific instructions will be added as the project is built.

## Setup

The required Python version, dependencies, and environment setup commands will be listed here once the lab code is finalized. Each lab's instructions will also show how to run it and confirm the expected result.

## Dataset

The project uses the public [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection), which contains messages labeled `ham` or `spam`. It is a historical teaching dataset, not a current production spam corpus. It is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); retain the dataset attribution when reusing it.

Do not add private or personal messages to this public repository.

## Cloud deployment

The API will run locally first. Cloud deployment is an optional extension in Program 2; the provider, setup steps, deployment commands, and cleanup steps will be documented in that lab. Check the provider's billing and free-tier terms before deploying.
