# Supply Chain Disruption Predictor (SCDP)

Supply chain risk intelligence platform. Maps suppliers as a graph, propagates disruption scenarios through the network, and produces executive summaries, impact scores, and mitigation actions.

Full product documentation lives in [documentation/Readme.md](documentation/Readme.md).

## Stack

| Service   | Image                     | Host port |
|-----------|---------------------------|-----------|
| frontend  | React + Nginx             | 80        |
| backend   | FastAPI (Python 3.12)     | 8000      |
| neo4j     | neo4j:5.26-community      | 7474, 7687|
| redis     | redis:7.4-alpine          | internal  |
| prometheus| prom/prometheus:v2.54.1   | 9090      |
| grafana   | grafana/grafana:11.4.0    | 3000      |

## What is implemented vs. mocked

The backend runs fully **without** Neo4j, Redis, or any external API by falling back to a bundled demo dataset. Enable the real integrations by setting credentials — the app hands off to real services automatically.

| Capability | When mocked | When real |
|------------|-------------|-----------|
| Supplier graph + risk scores | Bundled demo dataset (`database/mock_data.py`) | Neo4j graph queries |
| Disruption propagation | Deterministic graph BFS (`graph/risk_propagation.py`) — always computed | Same algorithm (no mock shortcut) |
| Threat / news intelligence | Derived from bundled demo news items | `integrations/news.py` + `integrations/weather.py` |
| AI mitigation summaries | Skipped (returns `ai_enriched: false`) | Gemini (`ai/gemini_client.py`) |
| Demo users (admin/analyst/viewer) | In-memory, seeded from env vars | In-memory, seeded from env vars (no external auth store). Set `{ROLE}_USERNAME`/`{ROLE}_PASSWORD` to enable a role. |

The deterministic simulation engine and risk-propagation algorithm are **always real** — only the *data sources* (graph, news, weather, Gemini) have a demo fallback. Tests run against the mocked backends for isolation.

## Quick start (Docker Compose)

Requirements: Docker + Docker Compose.

```bash
# 1. Backend config (credentials for Neo4j, Redis, users, APIs, JWT)
cp backend/.env.example backend/.env
#    Edit: NEO4J_PASSWORD, REDIS_PASSWORD, JWT_SECRET, user passwords, API keys

# 2. Root env for infra service passwords that compose interpolates (REQUIRED)
cp .env.example .env
#    Edit: NEO4J_PASSWORD, REDIS_PASSWORD, GRAFANA_PASSWORD (must match backend/.env)

# 3. Build and start the whole stack
docker compose up --build -d
```

Compose **fails fast** if any required password is missing (no insecure defaults). `NEO4J_PASSWORD` must match the value in `backend/.env` so the backend can authenticate to Neo4j.

```bash
# Verify
curl http://localhost/health        # liveness — process is up
curl http://localhost/ready         # readiness — 503 if configured Neo4j is down
docker compose ps                   # all services healthy
```

Stop everything with `docker compose down`. On first boot in non-production environments the backend auto-seeds the demo dataset into a fresh Neo4j.

## URLs / demo credentials

| App       | URL                      | Notes                                   |
|-----------|--------------------------|-----------------------------------------|
| Frontend  | http://localhost         | SPA; no login required for demo mode    |
| API docs  | http://localhost:8000/api/docs | Swagger UI                          |
| Neo4j     | http://localhost:7474    | auth per `NEO4J_PASSWORD`               |
| Grafana   | http://localhost:3000    | auth per `GRAFANA_PASSWORD`             |
| Prometheus| http://localhost:9090    | metrics                                 |

Authenticated endpoints (`/api/v1/simulations`, `/api/v1/audit`, etc.) accept the demo users defined in `backend/.env` (`ADMIN_USERNAME`/`ADMIN_PASSWORD`, `ANALYST_*`, `VIEWER_*`). No role is enabled until its credentials are set. The public `/api/v1/simulation` route powers the SPA demo without authentication.

## Local dev (no Docker for the app)

Run Node/Postgres-less: the backend needs only Python. Neo4j/Redis are optional (empty credentials → demo mode).

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # optional; app also has sensible defaults
python -m uvicorn main:app --reload
```

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

## Tests

```bash
cd backend
pytest                          # unit + integration tests (CI runs these two suites)
```

The test suite seeds its own demo users/environment via `tests/conftest.py` and does not depend on a local `.env` or live services.

## Known fixes applied to this repo

- `neo4j:5.27-community` tag does not exist on Docker Hub → pinned to `5.26-community`.
- Redis runs on the private network only (no host port): avoids clashes with other apps on 6379.
- `passlib` 1.7.4 crashes with `bcrypt>=4.1` → `bcrypt<4.1` pinned in `backend/requirements.txt`.
- `database/redis.py`: enabled Redis for non-localhost URLs and dropped the `ssl=` kwarg (redis-py 8.x).
- Frontend healthcheck uses `127.0.0.1` (busybox `wget` resolves `localhost` to IPv6 behind nginx).
