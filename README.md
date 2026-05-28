# Parodywall Backend

A high-performance FastAPI backend service for the Parodywall application, providing robust API endpoints, authentication, and database management.

## 🚀 Overview

This backend is built with **FastAPI** and uses **SQLAlchemy** for ORM and **Alembic** for database migrations. It leverages **uv** for lightning-fast dependency management and is designed to be easily deployable to Google Cloud Run.

### Key Features
- **FastAPI**: Modern, fast (high-performance) web framework for building APIs.
- **uv**: Extremely fast Python package installer and resolver.
- **SQLAlchemy 2.0**: The Database Toolkit for Python.
- **Alembic**: Lightweight database migration tool.
- **JWT Auth**: Secure user authentication and profile management.
- **Cloud Ready**: Optimized for containerized deployment on Google Cloud Run.

---

## 💻 Local Setup

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) installed on your system.

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/sujeetgund/parodywall-server.git
   cd backend
   ```

2. **Initialize the environment**:
   ```bash
   uv sync
   ```
   This will create a `.venv` directory and install all dependencies from `uv.lock`.

3. **Environment Variables**:
   Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   ```

4. **Run Database Migrations**:
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the Development Server**:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

---

## ☁️ Deployment

### Containerization
The project includes a multi-stage `Dockerfile` optimized for production. It uses `uv` to manage dependencies within the container.

#### Build locally:
```bash
docker build -t parodywall-server .
```

#### Run locally with Docker:
```bash
docker run -p 8080:8080 -e PORT=8080 --env-file .env parodywall-server
```

### Google Cloud Run Deployment

To deploy the backend to Google Cloud Run, follow these steps:

1. **Configure Google Cloud Project**:
   ```bash
   gcloud config set project [YOUR_PROJECT_ID]
   ```

2. **Build and Submit to Artifact Registry**:
   ```bash
   gcloud builds submit --tag gcr.io/[YOUR_PROJECT_ID]/parodywall-server
   ```

3. **Deploy to Cloud Run**:
   ```powershell
   gcloud run deploy parodywall-server `
     --image gcr.io/[YOUR_PROJECT_ID]/parodywall-server `
     --platform managed `
     --region [YOUR_REGION] `
     --allow-unauthenticated `
     --set-env-vars="DATABASE_URL=[YOUR_DB_URL],SECRET_KEY=[YOUR_SECRET]"
   ```

> [!TIP]
> Ensure you have the `Artifact Registry` and `Cloud Run` APIs enabled in your Google Cloud Console.

---

## 🛠️ Project Structure
```text
backend/
├── app/                # Application source code
│   ├── routes/         # API route definitions
│   ├── core/           # Core configuration and security
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic models for validation
│   └── services/       # Business logic
├── migrations/         # Alembic migration files (eg. 001_xyz.py, 002_abc.py)
├── main.py             # Entry point (script)
├── pyproject.toml      # Project dependencies and metadata
└── uv.lock             # Locked dependency versions
```