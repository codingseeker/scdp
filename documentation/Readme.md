# Supply Chain Disruption Predictor (SCDP)

Supply Chain Disruption Predictor (SCDP) is a backend-focused platform for detecting and analyzing supply chain risks before they become major problems.

It maps suppliers and their dependencies as a graph, collects information from news and weather sources, identifies potential disruptions, and calculates how those disruptions could spread through the supply chain.

The system also uses Gemini to analyze events and suggest possible mitigation strategies such as alternative suppliers and routes.

The main focus of the project is not just the AI model. It is building the system like a real backend service: reliable APIs, graph-based processing, background jobs, caching, testing, monitoring, security, and automated deployment.

## What It Does

* Tracks multi-tier supplier relationships using Neo4j.
* Detects potentially risky suppliers and dependencies.
* Collects external information from news and weather APIs.
* Analyzes events such as port closures, extreme weather, geopolitical issues, and strikes.
* Propagates a disruption through the supplier graph to estimate its wider impact.
* Calculates supplier criticality and Time-to-Impact.
* Detects single points of failure and critical suppliers.
* Finds possible alternative suppliers and transportation routes.
* Allows users to compare normal, disrupted, and mitigated scenarios.
* Uses Gemini to enrich threat analysis and generate mitigation suggestions.
* Keeps simulation history so previous scenarios can be reviewed.
* Continues basic risk calculations even when Gemini or another external service is unavailable.

## Example

A user could enter:

```text
Port closure in Miami for 5 days
```

The backend can then:

```text
Disruption
    ↓
Identify affected location
    ↓
Find connected suppliers
    ↓
Traverse supplier dependencies
    ↓
Calculate cascading risk
    ↓
Estimate Time-to-Impact
    ↓
Identify critical suppliers
    ↓
Find alternative suppliers/routes
    ↓
Generate mitigation recommendation
```

## Architecture

```text
                         User
                           |
                           v
                     +-----------+
                     |   Nginx   |
                     +-----+-----+
                           |
                +----------+----------+
                |                     |
                v                     v
          React Frontend         FastAPI Backend
                                      |
                +----------+----------+----------+
                |          |          |          |
                v          v          v          v
              Neo4j      Redis    Risk Engine  Gemini
                           |
                           |
                    Background Jobs
                           |
              +------------+------------+
              |            |            |
              v            v            v
            News        Weather    Other Sources
```

## Backend

The backend is built with FastAPI and is split into separate components so that API code, business logic, database operations, and external services do not get mixed together.

```text
backend/
├── api/
│   └── v1/
│       ├── suppliers.py
│       ├── risks.py
│       ├── threats.py
│       ├── simulations.py
│       ├── mitigation.py
│       ├── intelligence.py
│       └── metrics.py
│
├── ai/
│   ├── gemini_client.py
│   ├── prompts.py
│   ├── validators.py
│   └── fallback.py
│
├── graph/
│   ├── risk_propagation.py
│   ├── supplier_scoring.py
│   └── route_optimizer.py
│
├── services/
│   ├── risk_service.py
│   ├── simulation_service.py
│   ├── mitigation_service.py
│   └── intelligence_service.py
│
├── repositories/
│   ├── supplier_repository.py
│   ├── risk_repository.py
│   └── simulation_repository.py
│
├── integrations/
│   ├── news.py
│   ├── weather.py
│   └── geopolitics.py
│
├── database/
│   ├── neo4j.py
│   ├── indexes.py
│   └── seed.py
│
├── workers/
│   ├── simulation_tasks.py
│   └── ingestion_tasks.py
│
├── schemas/
│   ├── supplier.py
│   ├── risk.py
│   ├── threat.py
│   ├── simulation.py
│   └── mitigation.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── logging.py
│   └── exceptions.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── main.py
```

## API

The API is versioned so future changes do not break existing clients.

```text
/api/v1/health
/api/v1/ready

/api/v1/suppliers
/api/v1/suppliers/{supplier_id}

/api/v1/risks
/api/v1/risks/{supplier_id}

/api/v1/threats
/api/v1/threats/{threat_id}

/api/v1/intelligence
/api/v1/intelligence/news
/api/v1/intelligence/weather

/api/v1/simulations
/api/v1/simulations/{simulation_id}

/api/v1/mitigation
/api/v1/mitigation/routes
/api/v1/mitigation/suppliers

/api/v1/metrics
```

The API includes validation, consistent error responses, pagination, filtering, rate limiting, authentication, and request IDs.

## Risk Engine

The risk engine is intentionally not completely dependent on the LLM.

The core risk calculation is deterministic so the application can still produce a risk result if Gemini is temporarily unavailable.

The main calculations include:

* Supplier criticality.
* Cascading risk propagation.
* Time-to-Impact.
* Geographic concentration risk.
* Single-source-of-failure detection.
* Critical-path detection.
* Threat confidence.
* Risk weighting.
* Risk decay over time.
* Alternative supplier scoring.
* Alternative route scoring.

## AI Layer

Gemini is used where an LLM provides value rather than being responsible for the entire system.

It is used for:

* Understanding unstructured threat information.
* Enriching disruption analysis.
* Generating mitigation suggestions.
* Creating executive summaries.
* Comparing possible mitigation strategies.

Gemini responses are validated before they are used by the backend.

The system also tracks:

* Model version.
* Token usage.
* Request cost.
* AI response failures.
* Invalid responses.

External news and other untrusted text is treated as data, not instructions, to reduce prompt-injection risks.

## External Intelligence

SCDP can consume information from:

* News APIs.
* Weather APIs.
* Geopolitical sources.

Incoming information is:

```text
External Data
     ↓
Validation
     ↓
Deduplication
     ↓
Source Reliability
     ↓
Threat Classification
     ↓
Risk Engine
```

Old information is automatically given less influence or removed using timestamps and TTL rules.

## Background Processing

Some operations can take too long to run directly inside an HTTP request.

Examples include:

* Large risk simulations.
* Intelligence ingestion.
* Risk recalculation.
* Mitigation generation.

These operations are handled through background workers using Celery and Redis.

The API can return a job ID:

```text
POST /api/v1/simulations

        ↓

202 Accepted

{
    "job_id": "abc123",
    "status": "queued"
}
```

The client can then check:

```text
GET /api/v1/simulations/abc123
```

## Reliability

External services can fail, so the backend does not assume everything is always available.

The system uses:

* Request timeouts.
* Retries with exponential backoff.
* Circuit breakers.
* Redis caching.
* Neo4j connection pooling.
* Background jobs.
* Concurrency limits.
* Graceful shutdown.
* Fallback risk calculations.

For example:

```text
Gemini unavailable
       ↓
Use deterministic risk engine
       ↓
Return risk result
       ↓
Mark AI enrichment as unavailable
```

This is preferable to making the entire application return an error because one external API is down.

## Observability

The backend exposes useful operational information instead of relying only on application errors.

Tracked metrics include:

* API requests.
* API latency.
* HTTP errors.
* Simulation duration.
* Simulation failures.
* Neo4j query duration.
* Neo4j failures.
* External API failures.
* Gemini requests.
* Gemini token usage.
* Background job failures.

The observability stack uses:

* Prometheus.
* Grafana.
* OpenTelemetry.
* Structured JSON logging.

Distributed traces can follow a request through:

```text
FastAPI
   ↓
Risk Engine
   ↓
Neo4j
   ↓
External API / Gemini
```

## Security

The backend includes:

* JWT/OAuth2 authentication.
* Role-based authorization.
* Input validation.
* Rate limiting.
* Request-size limits.
* CORS restrictions.
* Secure secret management.
* Prompt-injection protection.
* Dependency vulnerability scanning.
* Container scanning.
* Secret scanning.
* Python security scanning.

Production secrets are not stored in the repository or Docker images.

## Testing

The project uses multiple levels of testing.

### Unit Tests

Core logic is tested independently:

* Risk propagation.
* Supplier scoring.
* Time-to-Impact.
* Route scoring.
* Threat scoring.
* AI response validation.
* Fallback logic.

### Integration Tests

Test the interaction between:

* FastAPI and Neo4j.
* FastAPI and Redis.
* Database transactions.
* External API clients.
* Background workers.

### End-to-End Tests

Test the complete flow:

```text
Create Disruption
       ↓
Identify Threat
       ↓
Propagate Risk
       ↓
Calculate Impact
       ↓
Find Critical Suppliers
       ↓
Generate Mitigation
       ↓
Return Result
```

## DevOps

The application is containerized so the same environment can be reproduced locally and deployed remotely.

```text
Developer
    ↓
Git Push
    ↓
GitHub Actions
    ↓
Tests
    ↓
Security Scans
    ↓
Docker Build
    ↓
Container Registry
    ↓
Deployment
    ↓
Health Checks
    ↓
Production
```

The CI/CD pipeline handles:

* Backend tests.
* Frontend checks.
* Security scanning.
* Docker image builds.
* Image publishing.
* Deployment.
* Rollback.

Docker images are tagged using Git commit SHAs or release versions instead of relying only on `latest`.

## Infrastructure

Infrastructure is managed using Terraform.

The deployment is separated into:

```text
Development
     ↓
Staging
     ↓
Production
```

Production secrets are stored using the cloud provider's secret-management system.

Kubernetes can be added later for workloads that actually require orchestration, scaling, or rolling deployments.

## Tech Stack

### Backend

* Python 3.12+
* FastAPI
* Uvicorn
* Pydantic
* httpx
* Neo4j Python Driver
* Cypher

### AI / Risk

* Google Gemini API
* Custom risk-propagation engine
* Graph algorithms
* Supplier criticality scoring
* Time-to-Impact calculation

### Data

* Neo4j
* Redis

### Background Jobs

* Celery
* Redis

### Frontend

* React
* Vite
* React Flow
* Tailwind CSS
* Recharts

### Testing

* pytest
* pytest-asyncio
* httpx
* Testcontainers

### Observability

* Prometheus
* Grafana
* OpenTelemetry
* Structured JSON logging

### Security

* JWT/OAuth2
* Trivy
* Gitleaks
* Bandit
* Dependabot

### DevOps

* Docker
* Docker Compose
* Nginx
* GitHub Actions
* Terraform
* Container Registry
* k6

### Optional

* Kubernetes

## Project Structure

```text
supply-chain-disruption-predictor/
│
├── backend/
├── frontend/
├── data/
├── infrastructure/
│   ├── terraform/
│   └── kubernetes/
├── monitoring/
│   ├── prometheus/
│   └── grafana/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── docker.yml
│       └── deploy.yml
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Running Locally

### Requirements

* Python 3.12+
* Node.js 20+
* Docker
* Docker Compose
* Neo4j
* Redis

### Start Neo4j and Redis

```bash
docker compose up -d neo4j redis
```

### Start Backend

```bash
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python -m uvicorn main:app --reload
```

### Start Frontend

```bash
cd frontend

npm install
npm run dev
```

### Run Tests

```bash
cd backend
pytest
```

### Run the Complete Stack

```bash
docker compose up --build
```

## Environment Variables

Create `.env` from `.env.example`.

```env
APP_ENV=development
LOG_LEVEL=INFO

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password

REDIS_URL=redis://localhost:6379/0

GEMINI_API_KEY=your_gemini_api_key
NEWS_API_KEY=your_news_api_key
WEATHER_API_KEY=your_weather_api_key

JWT_SECRET=your_jwt_secret
CORS_ORIGINS=http://localhost:5173
```

Never commit real API keys or production secrets.

## Performance Testing

The backend is tested under load using k6.

The main metrics are:

```text
Requests/sec
p50 latency
p95 latency
p99 latency
Error rate
Neo4j query latency
Simulation duration
Background job duration
External API latency
```

Performance numbers will be documented after actual load tests rather than being claimed beforehand.

## Disaster Recovery

The project includes recovery procedures for:

* Neo4j failure.
* Redis failure.
* Backend failure.
* External API outages.
* Failed deployments.
* Corrupted data.
* Lost application instances.

Neo4j backups should be regularly restored in a test environment to verify that they actually work.

## Roadmap

```text
Phase 1
Backend architecture
Risk engine
Neo4j
API
Testing

        ↓

Phase 2
Docker
Redis
Background jobs
Caching
Reliability

        ↓

Phase 3
CI/CD
Security scanning
Container registry
Cloud deployment

        ↓

Phase 4
Terraform
Monitoring
Logging
Tracing
Load testing

        ↓

Phase 5
Kubernetes
Autoscaling
Advanced streaming
```

## Goal

The goal of SCDP is to build more than a demo that calls an AI API.

It combines:

* Graph databases.
* Backend engineering.
* AI-assisted analysis.
* External data integration.
* Distributed background processing.
* Fault tolerance.
* Caching.
* Security.
* Automated testing.
* CI/CD.
* Infrastructure as code.
* Monitoring and tracing.
* Performance testing.

The result should be a system that can detect a disruption, understand how it affects the supply chain, explain the impact, and provide practical mitigation options while remaining reliable when individual services fail.
