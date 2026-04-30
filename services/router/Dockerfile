FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN pip install -U pip && pip install fastapi uvicorn[standard] pydantic transformers torch --extra-index-url https://download.pytorch.org/whl/cpu
COPY services/router ./services/router
COPY services/__init__.py ./services/__init__.py
EXPOSE 8100
CMD ["uvicorn", "services.router.server:app", "--host", "0.0.0.0", "--port", "8100"]
