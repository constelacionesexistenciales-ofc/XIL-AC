FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN addgroup -S xilac && adduser -S -G xilac xilac

COPY pyproject.toml README.md ./
COPY core ./core
COPY frontend ./frontend
COPY migrations ./migrations
COPY scripts ./scripts

RUN pip install --no-cache-dir .

USER xilac
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2)"
CMD ["uvicorn", "core.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
