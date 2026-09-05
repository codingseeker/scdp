# Backend Dockerfile — Multi-stage, non-root, minimal production image
# No secrets stored in image. Dev dependencies stripped.

FROM python:3.14-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---

FROM python:3.14-slim AS production

RUN groupadd -r scdp && useradd -r -g scdp -s /sbin/nologin scdp

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

# Remove test and dev files from production image
RUN rm -rf tests/ pyproject.toml .env .env.example

RUN chown -R scdp:scdp /app

USER scdp

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--no-access-log"]
