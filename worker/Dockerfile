FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN chown -R appuser:appgroup /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD pgrep -f "python worker.py" || exit 1

CMD ["python", "worker.py"]