# SECURITY.md — Supply Chain Disruption Predictor Security Documentation

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue for security vulnerabilities.
2. Email security concerns to the project maintainers directly.
3. Include a description of the vulnerability, steps to reproduce, and potential impact.
4. We will acknowledge receipt within 48 hours and provide a timeline for resolution.

## Supported Security Controls

### Authentication & Authorization

- **JWT/OAuth2 Authentication**: Short-lived access tokens (30 minutes) with refresh token rotation.
- **Role-Based Access Control**: Three roles with least-privilege access:
  - `admin`: Full access including system configuration
  - `analyst`: Read/write access to simulations, threats, and mitigation
  - `viewer`: Read-only access to dashboards and reports
- **Password Hashing**: Bcrypt with automatic salting (Argon2id recommended for production).
- **Authorization enforcement at backend service layer**, not only in the frontend.
- **Deny by default**: Endpoints are protected unless explicitly made public.

### API Security

- **Input Validation**: Strict Pydantic schemas with type checking, length limits, and pattern matching.
- **Rate Limiting**: Per-endpoint rate limits (authentication: 20/min, simulation: 10/min, general: 100/min).
- **Request Size Limits**: 1MB maximum request body.
- **Pagination Limits**: Maximum 100 items per page to prevent oversized queries.
- **Request Timeouts**: All external and database operations have configurable timeouts.
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy, HSTS (production), CSP (production).
- **CORS**: Explicit origin allowlist in production (no wildcards).

### Database Security

- **Parameterized Queries**: All Cypher queries use parameters — never string concatenation.
- **Neo4j Isolation**: Neo4j only accessible from backend via internal Docker network.
- **Connection Pooling**: Configurable pool size with timeout enforcement.
- **Query Timeouts**: Expensive graph operations are timeout-limited.
- **Dedicated Application User**: Application uses a separate Neo4j user with restricted permissions.

### Redis Security

- **Private Network**: Redis accessible only from backend.
- **Authentication**: Password required for production Redis.
- **TLS Support**: Configurable for production environments.
- **TTL Enforcement**: All cached data has expiration times.
- **No Sensitive Data**: Long-term secrets are not stored in Redis.

### AI/LLM Security

- **Prompt Injection Defenses**:
  - System instructions separated from external data.
  - External content marked as "UNTRUSTED EXTERNAL DATA".
  - Dangerous instruction patterns filtered from input.
  - Input length limits enforced.
- **Output Validation**: All Gemini responses validated against Pydantic schemas before use.
- **Dangerous Content Detection**: Responses containing code execution patterns, Cypher fragments, or XSS payloads are rejected.
- **Rate Limiting**: Gemini API calls rate-limited to prevent cost spikes.
- **Token Tracking**: Usage and cost tracked per request.
- **Fallback Behavior**: System continues with deterministic risk calculations when AI is unavailable.
- **AI outputs are clearly marked as recommendations**, not verified facts.

### External API Security

- **Backend-Only API Keys**: All external API keys stored only on the backend.
- **Circuit Breakers**: Repeated failures trigger circuit breaker to prevent retry storms.
- **Response Size Limits**: External responses exceeding 5MB are rejected.
- **Timeout Enforcement**: Strict connection and response timeouts.
- **Input Sanitization**: External text truncated and filtered before LLM processing.

### Secret Management

- `.env` files are in `.gitignore` and never committed.
- `.env.example` contains only placeholder values.
- Production secrets stored in cloud Secret Manager (GCP Secret Manager).
- Secrets never appear in logs, error messages, or stack traces.
- Separate credentials for development, staging, and production.
- Gitleaks scanning in CI prevents accidental secret commits.

### Container Security

- **Multi-Stage Builds**: Development dependencies stripped from production images.
- **Non-Root Users**: Backend runs as `scdp` user, frontend as `nginx` user.
- **No Secrets in Images**: Secrets injected at runtime via environment variables.
- **Read-Only Filesystem**: Production containers use read-only root filesystem.
- **Resource Limits**: CPU and memory limits enforced via Docker Compose.
- **Trivy Scanning**: Container images scanned in CI for vulnerabilities.
- **Minimal Base Images**: `python:3.12-slim` and `nginx:alpine`.

### CI/CD Security

- **Tests Before Deploy**: All tests must pass before deployment.
- **Security Scanning**: Bandit (Python), Gitleaks (secrets), Trivy (containers) in CI.
- **Least-Privilege Permissions**: GitHub Actions use minimal `contents: read` permissions.
- **Environment Approval**: Production deployments require manual approval.
- **Immutable Tags**: Docker images tagged with Git commit SHA.
- **Dependabot**: Automated dependency update monitoring.

### Logging & Monitoring

- **Structured JSON Logging**: All logs in parseable JSON format.
- **Sensitive Data Redaction**: Passwords, tokens, API keys automatically redacted from logs.
- **Security Event Logging**: Authentication failures, authorization denials, rate limit violations, suspicious patterns all logged.
- **Request IDs**: Every request tagged with a unique ID for correlation.
- **Prometheus Metrics**: Network health, API latency, Gemini usage exposed for monitoring.

## Trust Boundaries

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│   Browser    │────▶│   Nginx      │────▶│   FastAPI     │
│  (Untrusted) │     │  (Frontend)  │     │  (Backend)    │
└─────────────┘     └──────────────┘     └───┬───────────┘
                                              │
                    ┌─────────────────────────┤
                    │                         │
               ┌────▼────┐             ┌─────▼─────┐
               │  Neo4j  │             │   Redis   │
               │(Private)│             │ (Private) │
               └─────────┘             └───────────┘
                    │
              ┌─────▼──────┐     ┌──────────┐
              │  Gemini AI │     │  News/    │
              │ (External) │     │  Weather  │
              └────────────┘     │ (External)│
                                 └──────────┘
```

- **Browser → Nginx**: All input is untrusted. CORS, CSP, security headers enforced.
- **Nginx → FastAPI**: Authentication, authorization, validation at every endpoint.
- **FastAPI → Neo4j/Redis**: Private network. Parameterized queries only.
- **FastAPI → Gemini**: External content sanitized. Responses validated. Rate limited.
- **FastAPI → News/Weather**: External data treated as untrusted. Size limits. Circuit breakers.

## Incident Response

1. **Detection**: Security events logged and monitored via Prometheus/Grafana alerts.
2. **Containment**: Rate limiting and circuit breakers automatically limit blast radius.
3. **Investigation**: Request IDs enable full request tracing across services.
4. **Recovery**: Deployment rollback available. Neo4j backups can be restored.
5. **Post-Incident**: Audit logs provide complete activity trail.

## Backup & Recovery

- **Neo4j**: Regular backup procedures documented. Restoration tested in non-production environments.
- **Redis**: Data is ephemeral cache — no backup required. Application works without Redis.
- **Configuration**: Infrastructure defined in Terraform. Reproducible from code.
- **Deployment**: Rollback to previous Git SHA via CI/CD pipeline.
