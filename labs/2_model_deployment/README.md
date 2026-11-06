# Program 2: Model Deployment

Goal: reuse Program 1's model in a FastAPI service and call it through an API and a simple webpage.

## Before running

Finish [Program 1](../1_model_packaging/README.md). Run commands from the repository root with the same virtual environment activated.

## Request flow

The browser collects text and sends JSON to `POST /predict`. FastAPI validates the input, calls the pipeline already loaded in memory, and returns its label and version. The webpage displays that response.

The `lifespan` function loads the model once when each server process starts. Missing or incompatible artifacts stop startup with a clear error. Prediction does not train the model or reload it on every request.

## Run locally

```bash
uvicorn app:app --app-dir labs/2_model_deployment --host 127.0.0.1 --port 8000
```

Keep the terminal running and open:

- Webpage: <http://127.0.0.1:8000>
- Interactive API documentation: <http://127.0.0.1:8000/docs>
- Readiness response: <http://127.0.0.1:8000/health>

Open the webpage through this server. Double-clicking this lab's HTML file will not connect it to the API.

## Make a request

In a second terminal:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"message":"Can we meet for lunch at one?"}'
```

In Windows PowerShell use `curl.exe`, or use `/docs` to send the JSON request. Expected response shape:

```json
{"label":"ham","model_version":"1.0.0"}
```

The request must contain a string named `message` with 1–2000 characters and some non-whitespace text. Blank messages, numeric values and unexpected fields return HTTP 422. Check `/docs` for the request and response schema.

`GET /health` means the application completed startup. It cannot tell you whether the classifier is accurate. That is the purpose of Program 3's evaluation.

## Deployment practices

This demo serves the page and API from the same origin. It does not store or log raw SMS text. It is a teaching service without authentication or rate limiting; production deployment also needs access control, observability, resource limits and a release process.

For optional container and cloud instructions, use [Cloud deployment](CLOUD.md). Local work does not need a cloud account.

## Review and continue

Open [the Program 2 group quiz](../../quiz/program-2-deployment.html), then continue to [Program 3](../3_model_monitoring/README.md). Stop the local server with Ctrl+C when finished.

References: [FastAPI request bodies](https://fastapi.tiangolo.com/tutorial/body/) and [model loading with lifespan](https://fastapi.tiangolo.com/advanced/events/).
