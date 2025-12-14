# ---- 1. Base Image ----
FROM python:3.11-slim

# ---- 2. Set working directory ----
WORKDIR /app

# ---- 3. Install dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- 4. Copy app code ----
COPY . .

# ---- 5. Run FastAPI with Uvicorn ----
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]