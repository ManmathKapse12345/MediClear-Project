# ---------- Stage 1: build the React frontend ----------
FROM node:24-slim AS frontend
WORKDIR /app/frontend

# Install libraries first (cached until package files change)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Then copy the code and build -> /app/frontend/dist
COPY frontend/ ./
RUN npm run build


# ---------- Stage 2: Python backend that also serves the frontend ----------
FROM python:3.14-slim

# Don't write .pyc files; print logs immediately (so Render shows them live)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

# Install Python libraries first (cached until requirements.txt changes)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Same folder layout as the repo, so config.py's REPO_ROOT still works:
#   /app/backend/app   /app/data   /app/frontend/dist
COPY backend/app ./app
COPY data /app/data
COPY --from=frontend /app/frontend/dist /app/frontend/dist

# Run as a normal user, not root (safer if anything is ever exploited)
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Render tells the app which port to use in $PORT; locally it falls back to 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]