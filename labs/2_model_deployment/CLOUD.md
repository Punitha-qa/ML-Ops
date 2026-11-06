# Optional Docker and cloud deployment

Start with a working local API. These commands are an optional deployment exercise; running the Python labs does not create cloud resources.

## Container on your own computer

Install Docker from its official source and start its engine. From the repository root:

```bash
docker build -t sms-spam-workshop .
docker run --rm -p 8080:8080 sms-spam-workshop
```

Open <http://127.0.0.1:8080>. The Docker build trains a fresh model from the bundled public data inside the same pinned Python environment used to serve it. The local artifact is excluded from the image build. This avoids loading an artifact built with a different runtime.

In a production release, CI would normally package an approved model from an artifact registry rather than retrain during every image build.

## Render Free web service (may require card verification)

Render can build the root Dockerfile directly from the public GitHub repository. First ensure the repository contains `Dockerfile`, dependency files, `src/`, `data/`, `labs/` and `scripts/serve.py`.

During this workshop's setup, Render required adding a card even with Free compute selected. The dialog described a temporary US$1 authorization. Deployment was stopped before entering payment details. Use this route only if you accept the account's verification requirements; it is not a guaranteed card-free option.

1. Sign in at <https://dashboard.render.com/> and select **New Web Service**.
2. Choose **Public Git Repository** and enter `https://github.com/Punitha-qa/ML-Ops`.
3. Set the name to `sms-spam-workshop` (choose another name if unavailable), branch `main`, and language **Docker**.
4. Leave Root Directory empty and use the root `Dockerfile`. Keep the default Docker command so the image's `CMD` starts the server.
5. Select **Free ($0/month)** compute. Do not select a paid plan or add payment details for this workshop. Account verification requirements can vary; stop if payment is required.
6. Under Advanced, set the health check path to `/health` if available, then deploy.
7. Watch the build logs, then open the service URL. Check `/health`, `/docs` and a prediction from the homepage.

The image build trains and saves the model. Starting or waking the service loads that saved file; it does not retrain per request. The server binds to `0.0.0.0` and reads the `PORT` environment variable.

Free services sleep after 15 minutes without incoming traffic and can take about a minute to wake. Free instance hours, bandwidth and build minutes are limited. Without a payment method, exceeding applicable allowances can suspend services or builds. These limits suit a teaching demo, not production availability. Open the app before the classroom demo and keep the local lab ready as a fallback.

To stop hosting after the workshop, suspend the service in its settings. Delete it only when you no longer need the deployment. Public repository deployments may require a manual deploy to pick up later commits; check the dashboard.

References: [Docker on Render](https://render.com/docs/docker), [Free plan limits](https://render.com/docs/free), [Web services](https://render.com/docs/web-services).

## Google Cloud Run (alternative; billing setup required)

You need a Google Cloud project with billing enabled, the Google Cloud CLI, and permission to deploy source builds. Follow the [official prerequisites and IAM guidance](https://cloud.google.com/run/docs/deploying-source-code).

Cloud Run's free tier may cover a small demo, but it does not guarantee a zero bill. Cloud Build, Artifact Registry, networking and other services can add costs. Check [current pricing](https://cloud.google.com/run/pricing) and create a budget alert before the session. A budget alert does not impose a hard spending cap.

From the repository root, replace `YOUR_PROJECT_ID` with your own project ID:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud run deploy sms-spam-workshop \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --memory 512Mi \
  --cpu 1
```

The deployment uses the root Dockerfile and prints a service URL. `--allow-unauthenticated` makes that teaching webpage and API publicly callable. Use synthetic messages. The app listens on `0.0.0.0` and the `PORT` Cloud Run provides.

Open the printed URL and its `/docs` and `/health` paths. You can use the same `/predict` request as the local lab with the base URL replaced by the cloud URL. The first request after inactivity may take longer because the service can scale to zero.

If an organization policy blocks public access, keep the service private and follow your administrator's access policy. Avoid changing organization-wide permissions for this lab.

## Cleanup

Delete only the workshop service when finished:

```bash
gcloud run services delete sms-spam-workshop --region asia-south1
```

Source deployment also stores container images in Artifact Registry. In the Cloud Console, identify the images built for this workshop and remove them if no longer needed. Check the project's billing page for remaining resources. Deleting the service alone does not delete stored images.

References: [Cloud Run source deployment](https://cloud.google.com/run/docs/deploying-source-code), [container runtime contract](https://cloud.google.com/run/docs/container-contract), and [FastAPI Docker guidance](https://fastapi.tiangolo.com/deployment/docker/).
