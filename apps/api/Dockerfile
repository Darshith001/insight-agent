FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
RUN pip install -U pip && pip install -e .
COPY services ./services
COPY apps/api ./apps/api
EXPOSE 8000
CMD ["uvicorn", "apps.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
