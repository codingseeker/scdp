# Grand Strategy & Deployment Action Plan — SCDP

This document provides a single, unified, and unambiguous strategy and step-by-step action plan for deploying the Supply Chain Disruption Predictor (SCDP) across Development, Staging, and Production environments.

---

## 1. Core Deployment Principles

1. **Zero Downtime**: Utilize progressive canary traffic shifting (10% → 50% → 100%) for all production updates to prevent service interruption.
2. **Immutable Containers**: Package applications into versioned Docker containers tagged strictly with Git commit SHAs (`scdp-backend:<SHA>`). Never deploy unversioned or `latest` tags to production.
3. **Automated Quality & Security Gates**: Every release candidate must pass static analysis (SAST), secret scanning, container vulnerability scanning, unit/integration tests, and load tests before promotion.
4. **Decoupled Resilient Architecture**: Keep public web interfaces isolated from internal database networks. Ensure the system automatically falls back to deterministic graph engines if external APIs (Gemini/News) become unavailable.

---

## 2. Infrastructure Matrix

| Environment | Platform | Services Running | Network Ingress |
| :--- | :--- | :--- | :--- |
| **Development** | Workstation (Docker Compose) | Backend, Frontend, Neo4j, Redis, Prometheus, Grafana | Localhost (`:8000`, `:80`) |
| **Staging** | Cloud Run / AWS ECS | Candidate Backend & Frontend Containers | Private VCN + HTTPS Ingress |
| **Production** | Cloud Run / GKE Cluster | Canary & Stable Containers + Managed Databases | Cloud Load Balancer + TLS |

---

## 3. Phased Execution Plan

```
Phase 1: Local Baseline Setup
       ↓
Phase 2: CI/CD & Security Gates
       ↓
Phase 3: IaC Cloud Provisioning
       ↓
Phase 4: Staging Deployment & Testing
       ↓
Phase 5: Production Canary Rollout
       ↓
Phase 6: Observability & Backups
```

---

### Phase 1: Local Development Baseline Setup

* **Step 1.1 — Environment Initialization**:
  Copy environment configuration template and set application credentials.
  ```bash
  cd backend
  cp .env.example .env
  ```
  *Required settings*: Set `APP_ENV=development`, configure a secure `JWT_SECRET` (min 32 chars), `NEO4J_PASSWORD`, and `REDIS_PASSWORD`.

* **Step 1.2 — Launch Container Stack**:
  Build and start all local infrastructure components in background mode.
  ```bash
  docker-compose up --build -d
  ```

* **Step 1.3 — Baseline Health Check**:
  Confirm backend process health and database readiness.
  ```bash
  curl -s http://localhost:8000/health | jq .
  curl -s http://localhost:8000/ready | jq .
  ```

---

### Phase 2: CI/CD Pipeline & Automated Security Gates

* **Step 2.1 — Test Suite Execution**:
  Run unit, integration, and security test suites.
  ```bash
  cd backend
  source .venv/bin/activate
  python -m pytest tests/ -v --tb=short
  ```

* **Step 2.2 — Static Analysis & Secret Scanning**:
  Run Bandit to audit Python code and Gitleaks to detect hardcoded credentials.
  ```bash
  bandit -r backend/ -x backend/tests/
  gitleaks detect --source . -v
  ```

* **Step 2.3 — Container Build & Vulnerability Scan**:
  Build image tagged with Git commit SHA and run Trivy CVE scanner.
  ```bash
  export IMAGE_TAG=$(git rev-parse --short HEAD)
  docker build -t scdp-backend:${IMAGE_TAG} ./backend
  trivy image scdp-backend:${IMAGE_TAG}
  ```

---

### Phase 3: Infrastructure Provisioning (Terraform)

* **Step 3.1 — Terraform Initialization & Plan**:
  Initialize cloud state and review resource changes.
  ```bash
  cd infrastructure/terraform
  terraform init
  terraform plan -var="project_id=YOUR_PROJECT_ID" -var="environment=staging"
  ```

* **Step 3.2 — Provision Cloud Infrastructure**:
  Deploy container services, secret manager instances, and IAM roles.
  ```bash
  terraform apply -auto-approve -var="project_id=YOUR_PROJECT_ID" -var="environment=staging"
  ```

---

### Phase 4: Staging Deployment & Automated Validation

* **Step 4.1 — Publish Container Artifacts**:
  Push Git SHA-tagged images to Container Registry (GHCR/GCR).
  ```bash
  docker tag scdp-backend:${IMAGE_TAG} ghcr.io/your-org/scdp-backend:${IMAGE_TAG}
  docker push ghcr.io/your-org/scdp-backend:${IMAGE_TAG}
  ```

* **Step 4.2 — Deploy to Staging Environment**:
  Trigger deployment pipeline with release image tag.
  ```bash
  gh workflow run deploy.yml -f environment=staging -f image_tag=${IMAGE_TAG}
  ```

* **Step 4.3 — Staging Verification & Performance Test**:
  Run end-to-end integration flow and load test candidate build.
  ```bash
  # End-to-End Suite
  pytest backend/tests/e2e/ -v
  
  # Load Capacity Test
  k6 run tests/load/k6_test.js
  ```

---

### Phase 5: Production Canary Rollout

* **Step 5.1 — Database & Secret Audit**:
  Verify Neo4j indexes and production secrets in Secret Manager before routing live traffic.

* **Step 5.2 — Progressive Traffic Shifting**:
  1. Route **10% of traffic** to new container revision. Monitor error rates for 15 minutes.
  2. Increase traffic to **50%** if 5xx error rate remains below 0.01%.
  3. Route **100% of traffic** to complete production deployment.

* **Step 5.3 — Rollback Trigger & Execution**:
  * *Automated Rollback Triggers*: HTTP 5xx error rate > 1.0%, latency p95 > 1500ms, or failed readiness probes.
  * *Manual Rollback Command*:
    ```bash
    gh workflow run deploy.yml -f environment=production -f image_tag=PREVIOUS_STABLE_SHA
    ```

---

### Phase 6: Post-Deployment Observability & Maintenance

* **Step 6.1 — Prometheus & Grafana Monitoring**:
  Monitor request rate, latency, and database query durations via `/api/v1/metrics/prometheus`.

* **Step 6.2 — Security Audit Log Monitoring**:
  Inspect `/api/v1/audit` to confirm authentication and simulation events are logged.

* **Step 6.3 — Database Backup Execution**:
  Run automated Neo4j graph data backup.
  ```bash
  docker exec scdp-neo4j neo4j-admin database dump neo4j --to-path=/data/backups/
  ```

---

## 4. Emergency Action Protocol

| Event | Immediate Action | Mitigation Procedure |
| :--- | :--- | :--- |
| **API Error Spike (>1%)** | Instant Traffic Reversion | Roll back load balancer to previous Git SHA tag. |
| **External AI API Down** | Circuit Breaker Active | System automatically falls back to deterministic graph propagation. |
| **Database Disconnection** | Health Probe Alert | Backend serves sample fallback data without crashing API. |
| **Secret Leak** | Rotate Secret in Cloud Manager | Re-deploy container revision to inject rotated credentials. |

---

*Document Version*: `1.0.0`  
*Location*: `documentation/grand_strategy_deployment.md`
