BACKEND + DEVOPS ENHANCEMENT ROADMAP

- [x] Refactor FastAPI into modular layers: routers, services, repositories, schemas, models, and core.
- [x] Separate API routing, business logic, database operations, AI logic, and external integrations.
- [x] Add API versioning using `/api/v1/...`.
- [x] Create dedicated APIs for suppliers, risks, threats, simulations, mitigation, intelligence, and metrics.
- [x] Add strict Pydantic request and response schemas for every API.
- [x] Add centralized exception handling with consistent error responses.
- [x] Add request validation, payload-size limits, and input sanitization.
- [x] Add pagination, filtering, sorting, and search to supplier and risk APIs.
- [x] Add authentication and role-based authorization for admin, analyst, and viewer roles.
- [x] Add API rate limiting, especially for expensive simulation and AI endpoints.
- [x] Add request/correlation IDs across API requests, logs, and traces.
- [x] Replace unstructured print statements with structured JSON logging.
- [x] Add `/health` endpoint for process health.
- [x] Add `/ready` endpoint that verifies required dependencies such as Neo4j.
- [x] Add async HTTP clients for News, Weather, and Gemini integrations.
- [x] Add connection pooling for Neo4j.
- [x] Add configurable timeouts for every external dependency.
- [x] Add exponential-backoff retries for transient external API failures.
- [x] Add circuit-breaker behavior for repeatedly failing external services.
- [x] Add Redis-based caching for frequently requested external intelligence and risk data.
- [x] Add background job processing for expensive simulations and intelligence ingestion.
- [x] Add job-status APIs for long-running simulations.
- [x] Add idempotency keys to simulation and mitigation-generation requests.
- [x] Add deterministic risk-propagation logic that can operate without Gemini.
- [x] Use Gemini for AI enrichment and reasoning rather than making it a single point of failure.
- [x] Add structured Gemini prompts with strict JSON output schemas.
- [x] Validate every Gemini response against Pydantic schemas before processing it.
- [x] Add fallback handling for unavailable, invalid, or incomplete Gemini responses.
- [x] Add Gemini token and cost tracking.
- [x] Store AI model/version metadata with generated predictions.
- [x] Add confidence scores to predicted risks.
- [x] Make risk-weighting configurable instead of hardcoded.
- [x] Add time-decay logic for stale threats.
- [x] Add supplier criticality scoring based on dependency depth, alternatives, lead time, and geographic concentration.
- [x] Add multi-level cascading-risk propagation through the Neo4j graph.
- [x] Improve Time-to-Impact calculation using lead time, inventory, transportation, and dependency depth.
- [x] Add single-source-of-failure detection.
- [x] Add critical-path supplier detection.
- [x] Add geographic concentration-risk detection.
- [x] Add alternative-supplier discovery through Neo4j graph queries.
- [x] Add alternative-route scoring using cost, distance, capacity, risk, and delay.
- [x] Add baseline-vs-disruption-vs-mitigation scenario comparison.
- [x] Store simulation history, inputs, outputs, timestamps, and model metadata.
- [x] Add historical risk tracking instead of storing only current risk state.
- [x] Deduplicate threats across News, Weather, and geopolitical sources.
- [x] Add source reliability and confidence scoring.
- [x] Store source attribution and timestamps for intelligence-derived risks.
- [x] Add expiration/TTL handling for stale external intelligence.
- [x] Add prompt-injection protection when external intelligence is sent to Gemini.
- [x] Sanitize and constrain external text before LLM processing.
- [x] Add Neo4j constraints and indexes for suppliers, locations, products, routes, and threats.
- [x] Optimize expensive Cypher queries and unnecessary graph traversals.
- [x] Add Neo4j transaction handling for multi-step graph updates.
- [x] Add Neo4j retry handling for transient database failures.
- [x] Add database query-duration metrics.
- [x] Add reproducible Neo4j initialization, constraints, indexes, and seed-data ingestion.
- [x] Add database schema/version migration handling.
- [x] Add automated backend unit tests with pytest.
- [x] Add integration tests for FastAPI and Neo4j.
- [x] Add mocked tests for News, Weather, and Gemini APIs.
- [x] Add end-to-end tests covering disruption → propagation → mitigation.
- [x] Add API contract tests against the OpenAPI specification.
- [x] Add backend performance benchmarks for graph traversal and risk simulation.
- [x] Add concurrency controls to prevent expensive simulations from overwhelming the backend.
- [x] Add production worker configuration for FastAPI/Uvicorn.
- [x] Add graceful startup and shutdown handling for database connections, HTTP clients, and background jobs.
- [x] Add Dockerfile for the FastAPI backend.
- [x] Add Dockerfile for the React frontend and serve the production build through Nginx.
- [x] Create Docker Compose configuration for reproducible local development.
- [x] Add `.env.example` and ensure real `.env` files are never committed.
- [x] Store production secrets using a cloud secret-management system.
- [x] Add GitHub Actions CI for backend tests, frontend checks, security scans, and Docker builds.
- [x] Add Trivy scanning for container and filesystem vulnerabilities.
- [x] Add Gitleaks scanning for accidentally committed secrets.
- [x] Add Bandit security scanning for Python code.
- [x] Add Dependabot for dependency updates.
- [x] Build and publish versioned Docker images to a container registry.
- [x] Tag Docker images using Git commit SHA or release versions instead of relying on `latest`.
- [x] Add separate development, staging, and production configurations.
- [x] Automate deployment from GitHub Actions.
- [x] Add deployment rollback capability.
- [x] Add Terraform for reproducible cloud infrastructure.
- [x] Add application metrics for request count, latency, errors, simulations, database queries, and external API failures.
- [x] Add Prometheus-compatible metrics collection.
- [x] Add Grafana dashboards for backend health, latency, errors, simulations, and dependencies.
- [x] Add distributed tracing with OpenTelemetry across FastAPI, Neo4j, external APIs, and Gemini.
- [x] Add centralized log collection for production debugging.
- [x] Add load testing with k6 or Locust.
- [x] Measure p50, p95, and p99 API latency, throughput, and error rate.
- [x] Add Neo4j backup and restore procedures.
- [x] Document disaster recovery for database failure, backend failure, external API failure, and deployment failure.
- [x] Add architecture, data-flow, deployment, and CI/CD diagrams to the README.
- [x] Add Kubernetes only after Docker, CI/CD, Terraform, testing, and observability are stable.
- [x] If Kubernetes is introduced, configure Deployments, Services, Secrets, ConfigMaps, probes, resource limits, rolling deployments, and autoscaling.
- [x] Document every infrastructure component by the specific reliability, scalability, security, or operational problem it solves.



CYBERSECURITY HARDENING — SCDP

- [x] Add a dedicated security layer instead of modifying the existing risk engine logic.
- [x] Keep risk calculation and security controls separate so security changes cannot alter business-risk calculations.

API SECURITY

- [x] Add authentication to protected `/api/v1/*` endpoints.
- [x] Implement JWT/OAuth2 authentication using short-lived access tokens.
- [x] Add role-based access control with `admin`, `analyst`, and `viewer` roles.
- [x] Enforce authorization at the endpoint/service layer, not only in the frontend.
- [x] Deny access by default and explicitly allow required roles.
- [x] Add rate limiting to authentication, simulation, AI, and intelligence endpoints.
- [x] Add stricter rate limits to expensive Gemini and simulation operations.
- [x] Add request body size limits.
- [x] Add maximum pagination limits to prevent oversized database queries.
- [x] Validate every path parameter, query parameter, and request body with Pydantic.
- [x] Reject unexpected fields where strict schemas are appropriate.
- [x] Sanitize user-controlled strings before using them in logs, Cypher queries, prompts, or generated reports.
- [x] Never construct Cypher queries by concatenating user input.
- [x] Use parameterized Cypher queries everywhere.
- [x] Add protection against excessive graph traversal requests.
- [x] Add request timeouts to every API endpoint that performs external or database operations.
- [x] Add consistent security error responses without exposing internal implementation details.

AUTHENTICATION SECURITY

- [x] Hash passwords using Argon2id if local accounts are implemented.
- [x] Never store plaintext passwords.
- [x] Never store JWT signing secrets in source code.
- [x] Rotate JWT signing secrets through the deployment secret manager.
- [x] Use short-lived access tokens.
- [x] Add refresh-token rotation if refresh tokens are implemented.
- [x] Invalidate sessions/tokens after critical account changes.
- [x] Add account lockout or progressive delays for repeated authentication failures.
- [x] Log authentication failures without logging passwords, tokens, or sensitive request data.

AUTHORIZATION

- [x] Verify that every resource belongs to the authenticated user or permitted organization before returning it.
- [x] Prevent IDOR/BOLA vulnerabilities such as accessing another user's `/suppliers/{id}` or `/simulations/{id}`.
- [x] Apply authorization checks to simulation history, mitigation results, supplier data, and administrative operations.
- [x] Keep authorization logic in backend services rather than relying on React route protection.

SECRETS

- [x] Add `.env` to `.gitignore`.
- [x] Keep `.env.example` limited to placeholder values.
- [x] Scan the repository with Gitleaks before every release.
- [x] Rotate any API key that has ever been committed to Git history.
- [x] Never expose Gemini, News, Weather, Neo4j, Redis, or JWT secrets to the frontend.
- [x] Pass secrets to production through a cloud secret manager.
- [x] Prevent secrets from appearing in application logs.
- [x] Prevent secrets from appearing in exception messages and stack traces returned to clients.
- [x] Use separate credentials for development, staging, and production.
- [x] Give each service only the credentials it actually needs.

NEO4J SECURITY

- [x] Never expose Neo4j Bolt ports directly to the public internet.
- [x] Allow Neo4j network access only from the backend.
- [x] Use a dedicated Neo4j database user for the application.
- [x] Restrict application database permissions to the operations the backend actually requires.
- [x] Keep administrative Neo4j credentials separate from application credentials.
- [x] Use encrypted Neo4j connections in production.
- [x] Parameterize all Cypher queries.
- [x] Add query timeouts for expensive graph operations.
- [x] Limit graph traversal depth for user-triggered queries.
- [x] Add pagination to graph-derived API responses.
- [x] Log suspiciously expensive or unusually deep graph queries.
- [x] Add database backups and regularly test restoration.
- [x] Do not expose Neo4j Browser or administrative interfaces publicly in production.

REDIS SECURITY

- [x] Keep Redis on a private network.
- [x] Require authentication for production Redis.
- [x] Use TLS for Redis connections where supported by the deployment environment.
- [x] Do not store long-term sensitive information in Redis unless necessary.
- [x] Configure TTLs for cached intelligence and temporary job data.
- [x] Prevent untrusted users from directly accessing Redis.

GEMINI / LLM SECURITY

- [x] Treat News, Weather, and other external text as untrusted input.
- [x] Add prompt-injection defenses before sending external content to Gemini.
- [x] Separate system instructions from external data.
- [x] Clearly mark external content as untrusted data inside prompts.
- [x] Never allow external content to override application instructions.
- [x] Restrict Gemini output to predefined structured schemas.
- [x] Validate Gemini output before passing it to business logic.
- [x] Never execute shell commands, Cypher, SQL, URLs, or code directly from Gemini output.
- [x] Never allow Gemini to directly modify the database.
- [x] Keep database writes behind deterministic backend functions.
- [x] Add maximum input length for LLM prompts.
- [x] Add maximum output/token limits.
- [x] Add Gemini request rate limits.
- [x] Track Gemini usage and unusual spikes in consumption.
- [x] Add fallback behavior when Gemini returns malformed or unsafe output.
- [x] Store the source of information used for AI-generated recommendations.
- [x] Mark AI-generated recommendations as recommendations rather than verified facts.

EXTERNAL API SECURITY

- [x] Store external API keys only on the backend.
- [x] Never send external API keys to React.
- [x] Set strict connection and response timeouts.
- [x] Validate external API responses before processing them.
- [x] Reject unexpectedly large external responses.
- [x] Handle API rate limits without retry storms.
- [x] Use exponential backoff for transient failures.
- [x] Add circuit breakers for repeatedly failing services.
- [x] Cache external intelligence where appropriate.
- [x] Prevent external API failures from exposing stack traces to users.

SSRF PROTECTION

- [x] Do not allow users to submit arbitrary URLs for the backend to fetch.
- [x] If URL fetching is introduced, implement an explicit domain allowlist.
- [x] Block localhost, private IP ranges, loopback, link-local, and cloud metadata addresses.
- [x] Validate redirects during server-side HTTP requests.
- [x] Do not allow Gemini-generated URLs to be fetched automatically.

FRONTEND / API BOUNDARY

- [x] Treat all frontend input as untrusted.
- [x] Do not rely on hidden React fields for authorization.
- [x] Do not place secrets in Vite environment variables unless they are intentionally public.
- [x] Configure CORS with an explicit production origin allowlist.
- [x] Disable wildcard CORS in production.
- [x] Add secure HTTP response headers.
- [x] Configure Content Security Policy where compatible with the application.
- [x] Configure HSTS when the application is served exclusively over HTTPS.
- [x] Prevent clickjacking using appropriate security headers.
- [x] Configure secure cookie attributes if cookies are used.
- [x] Avoid storing sensitive authentication tokens in localStorage when a safer architecture is possible.

LOGGING / MONITORING

- [x] Implement structured security logs.
- [x] Log authentication failures.
- [x] Log authorization failures.
- [x] Log suspicious request patterns.
- [x] Log rate-limit violations.
- [x] Log abnormal simulation activity.
- [x] Log unusually expensive graph queries.
- [x] Log repeated external API failures.
- [x] Never log passwords, API keys, JWTs, cookies, or authorization headers.
- [x] Add a request ID to security-relevant events.
- [x] Protect production logs from unauthorized modification.
- [x] Define log retention periods.
- [x] Add alerts for repeated authentication failures.
- [x] Add alerts for abnormal API usage.
- [x] Add alerts for unexpected Gemini usage spikes.
- [x] Add alerts for repeated authorization failures.

DEPENDENCY SECURITY

- [x] Pin production dependencies to controlled versions.
- [x] Generate and maintain a dependency lock file.
- [x] Run dependency vulnerability scanning in CI.
- [x] Enable Dependabot or equivalent automated dependency monitoring.
- [x] Remove unused Python and Node.js dependencies.
- [x] Review new dependencies before adding them.
- [x] Avoid abandoned or unmaintained packages.
- [x] Run Bandit against Python code.
- [x] Run npm audit or an equivalent frontend dependency scanner.
- [x] Run Trivy against Docker images.

CONTAINER SECURITY

- [x] Use minimal production base images.
- [x] Run the FastAPI container as a non-root user.
- [x] Run Nginx as a non-root user where practical.
- [x] Do not store secrets inside Docker images.
- [x] Use multi-stage Docker builds.
- [x] Remove development dependencies from production images.
- [x] Pin important base-image versions.
- [x] Scan images with Trivy during CI.
- [x] Do not expose unnecessary container ports.
- [x] Use Docker networks to isolate frontend, backend, Neo4j, and Redis traffic.
- [x] Apply container resource limits.
- [x] Add container health checks.
- [x] Drop unnecessary Linux capabilities.
- [x] Use read-only filesystems where compatible with the application.

CI/CD SECURITY

- [x] Run tests before deployment.
- [x] Run Bandit, Gitleaks, Trivy, and dependency scans in CI.
- [x] Fail the pipeline on critical security findings.
- [x] Never place cloud credentials directly in GitHub Actions YAML.
- [x] Use GitHub Actions secrets or OIDC-based cloud authentication.
- [x] Restrict GitHub Actions permissions using least privilege.
- [x] Pin critical GitHub Actions to trusted versions or commit SHAs.
- [x] Require review before production deployment.
- [x] Separate staging and production deployment credentials.
- [x] Generate immutable Docker image tags from Git commits.
- [x] Do not deploy unverified `latest` images.
- [x] Keep deployment rollback available.
- [x] Scan the final production image before deployment.

SUPPLY-CHAIN SECURITY

- [x] Add supplier-data validation before importing records into Neo4j.
- [x] Validate imported CSV fields and reject malformed records.
- [x] Prevent imported data from becoming executable commands or Cypher fragments.
- [x] Track the source and timestamp of imported intelligence.
- [x] Assign reliability scores to external sources.
- [x] Detect duplicate or conflicting intelligence records.
- [x] Keep an audit trail for major risk-score changes.
- [x] Record which data sources influenced a simulation.
- [x] Record which model/version generated an AI recommendation.
- [x] Separate raw external intelligence from trusted internal risk data.
- [x] Restrict who can modify supplier relationships and risk configuration.

AUDITABILITY

- [x] Create an audit-log model for security-sensitive actions.
- [x] Record login and authentication events.
- [x] Record authorization failures.
- [x] Record supplier-data modifications.
- [x] Record risk-model configuration changes.
- [x] Record simulation creation and deletion.
- [x] Record mitigation changes.
- [x] Record administrative actions.
- [x] Include timestamp, actor, action, resource, request ID, and result.
- [x] Prevent normal users from modifying audit records.

SECURITY TESTING

- [x] Add authentication tests.
- [x] Add authorization tests.
- [x] Add IDOR/BOLA tests.
- [x] Add rate-limit tests.
- [x] Add input-validation tests.
- [x] Add Cypher-injection tests.
- [x] Add prompt-injection tests.
- [x] Add malicious external-data tests.
- [x] Add oversized-payload tests.
- [x] Add malformed-Gemini-response tests.
- [x] Add SSRF tests if URL fetching is introduced.
- [x] Add dependency and container scans to CI.
- [x] Run OWASP ZAP against the deployed API in staging.
- [x] Perform manual API security testing with Burp Suite against staging.
- [x] Never run destructive security tests against production.

SECURITY DOCUMENTATION

- [x] Add a `SECURITY.md` file.
- [x] Document supported security controls.
- [x] Document how to report vulnerabilities.
- [x] Document authentication and authorization architecture.
- [x] Document secret-management practices.
- [x] Document external API trust boundaries.
- [x] Document Gemini prompt-injection defenses.
- [x] Document database access controls.
- [x] Document incident-response procedures.
- [x] Document backup and recovery procedures.
- [x] Add a threat model covering users, frontend, backend, Neo4j, Redis, Gemini, News, Weather, CI/CD, and cloud infrastructure.

SAFE IMPLEMENTATION ORDER

- [x] Phase 1: Secrets, input validation, parameterized Cypher, authentication, authorization.
- [x] Phase 2: Rate limiting, security headers, CORS restrictions, API hardening.
- [x] Phase 3: Gemini prompt-injection defenses and structured-output validation.
- [x] Phase 4: Neo4j/Redis network isolation and least-privilege credentials.
- [x] Phase 5: Structured security logging, audit logging, and security alerts.
- [x] Phase 6: Docker hardening and container scanning.
- [x] Phase 7: CI/CD security scanning and least-privilege deployment credentials.
- [x] Phase 8: Automated security tests, OWASP ZAP, and staging penetration testing.
- [x] Phase 9: Threat model, incident response, backups, and recovery validation.

NON-BREAKING RULES

- [x] Keep existing risk-calculation algorithms unchanged while adding security controls around them.
- [x] Add authentication as middleware/dependencies rather than rewriting business logic.
- [x] Add validation at API boundaries rather than modifying internal calculation functions.
- [x] Introduce Redis as an optional cache before making it a hard dependency.
- [x] Add background workers only for operations that are already safe to execute asynchronously.
- [x] Keep deterministic risk calculation available if Gemini fails.
- [x] Introduce security controls behind configuration flags when a change could affect existing local development.
- [x] Implement and test each security layer independently before moving to the next one.
- [x] Run the complete existing test suite after every security-related change.
- [x] Make security improvements incrementally so the existing application remains functional throughout the migration.