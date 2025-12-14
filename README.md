# 🚀 Newz AI – Automated Daily News Agent (Cloud Run + Scheduler + Vertex AI)

This project is a **serverless FastAPI application** deployed on **Google Cloud Run** and triggered **daily at 10 AM IST** by **Cloud Scheduler**.
It retrieves news from RSS feeds, processes it with **Vertex AI** wrapped by a **LangChain Agent**, and sends email updates using secrets stored in **Google Secret Manager**.

---

## 🔥 Features

* **FastAPI** backend deployed on Cloud Run
* **Automated daily job** via Cloud Scheduler
* **Secure secret injection** using Google Secret Manager
* **Dockerized deployment** via Cloud Build
* **OIDC-authenticated Cloud Scheduler calls**
* Uses **Vertex AI GenAI models + LangChain Agent framework**
* Sends email alerts (SMTP)

---

## 📁 Project Structure

```
project/
│
├── agents/
│   └── news_agent.py        # News + Vertex AI logic
│
├── app.py                   # FastAPI entrypoint (/news)
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

---

## 🧠 How It Works (Architecture)

```
Cloud Scheduler (10 AM IST)
        |
        v
Cloud Run URL (/news) ← OIDC identity token
        |
        v
FastAPI endpoint processes:
    - RSS / Custom Search
    - Vertex AI model reasoning
    - SMTP email sending
        |
        v
Returns success response
```

---

## 🛡 Security Model

### ✔ No `.env` or `cred.json` inside the container

All secrets come from **Google Secret Manager**, injected at runtime via:

* `GOOGLE_API_KEY`
* `GOOGLE_CSE_ID`
* `SMTP_EMAIL`
* `SMTP_PASSWORD`

### ✔ Cloud Run is **private**

`allow-unauthenticated = false`

Cloud Scheduler authenticates using **OIDC tokens** (JWTs) tied to a service account.

### ✔ No service account JSON needed

Cloud Run uses **Workload Identity**.

---

## 🐳 Local Development

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run FastAPI locally

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8080
```

### 3. Set local secrets manually

```bash
export GOOGLE_API_KEY="your-key"
export GOOGLE_CSE_ID="your-id"
export SMTP_EMAIL="your-email"
export SMTP_PASSWORD="your-password"
```

---

# 🐳 Docker Build (Local)

```bash
docker build -t newz-fastapi .
docker run -p 8080:8080 newz-fastapi
```

---

## 🚀 Deploying to Cloud Run

### Build the container with Cloud Build

```bash
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/<project-id>/<repo-name>/<image-name> .
```

### Deploy to Cloud Run

```bash
gcloud run deploy <service-name> \
  --image=us-central1-docker.pkg.dev/<project-id>/<repo-name>/<image-name> \
  --service-account=<service-account>@<project-id>.iam.gserviceaccount.com \
  --update-secrets=GOOGLE_API_KEY=<secret-name>:latest \
  --update-secrets=GOOGLE_CSE_ID=<secret-name>:latest \
  --update-secrets=SMTP_EMAIL=<secret-name>:latest \
  --update-secrets=SMTP_PASSWORD=<secret-name>:latest \
  --region=us-central1 \
  --platform=managed
```

---

## ⏰ Scheduler Job (Daily at 10 AM IST)

Cloud Scheduler uses UTC.
10 AM IST = **4:30 AM UTC** → cron: `30 4 * * *`.

```bash
gcloud scheduler jobs create http <job-name> \
  --location=us-central1 \
  --schedule="30 4 * * *" \
  --uri="https://<cloud-run-url>/news" \
  --http-method=GET \
  --oidc-service-account-email=<service-account>@<project-id>.iam.gserviceaccount.com
```

Trigger manually:

```bash
gcloud scheduler jobs run <job-name> --location=us-central1
```

---

## 🌩 Testing Protected Cloud Run Endpoint

If the service is private:

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
     https://<cloud-run-url>/news
```

---

## 🔐 Secrets Used

| Variable                     | Description                      |
| ---------------------------- | -------------------------------- |
| `GOOGLE_API_KEY`             | Google Custom Search API Key     |
| `GOOGLE_CSE_ID`              | Custom Search Engine ID          |
| `SMTP_EMAIL`                 | Sender email address             |
| `SMTP_PASSWORD`              | Email app password               |
| *(none for service account)* | Cloud Run uses Workload Identity |