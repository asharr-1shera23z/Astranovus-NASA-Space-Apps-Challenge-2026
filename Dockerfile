# ASTRANOVUS API (FastAPI). Build from the repo root:  docker build -t astranovus-api .
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend backend
COPY model model
COPY data/dimensions.json data/targets.json data/purposes.json data/experiments.json data/target_evidence_summary.json data/validation_summary.json data/
COPY data/processed/earth_grid.csv data/processed/earth_grid_metadata.json data/processed/stage2.json data/processed/
# No synthetic fallback in production: the API refuses to start without data/processed/earth_grid.csv.
ENV ASTRANOVUS_CORS_ORIGINS="*"
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
