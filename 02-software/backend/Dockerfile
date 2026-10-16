# Build context: backend/ (docker build -t refinery-api ./backend).
# Official Python and HiGHS wheels support both EC2 ARM64 and x86_64.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SOLVER_ENGINE=reference \
    SOLVER_THREADS=1 \
    SOLVE_TIME_LIMIT=20 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    PORT=8000
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt \
    && useradd --create-home --uid 1000 app

COPY --chown=app:app *.py ./
COPY --chown=app:app examples/ ./examples/
COPY --chown=app:app licences/ ./licences/
COPY --chown=app:app THIRD_PARTY_NOTICES.md ./
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/health', timeout=3)"
# One API worker: admission control is process-local. exec forwards stop signals.
# Compose exposes this port only to Caddy, which sets the forwarded headers.
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --limit-concurrency 32 --timeout-keep-alive 5 --timeout-graceful-shutdown 40 --proxy-headers --forwarded-allow-ips='*'"]
