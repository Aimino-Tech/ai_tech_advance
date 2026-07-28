---
course: deepseek-architect
title: DeepSeek Architecture & Design
description: 10 scenarios testing architecture and design — system decomposition, interface design, dependency management, data flow design, state management, error boundary design, API design, database schema design, authentication flow design, deployment architecture
difficulty: standard
model: deepseek-v4-flash
scenarios:
  - id: arch-01
    name: "System decomposition — break monolith into modules"
    description: "Propose a modular decomposition of a monolithic e-commerce backend"
    tags: [architecture, decomposition, modularity]
    prompt: |
      A startup's e-commerce backend is a single Python Django monolith with:

      ```
      monolith/
        models.py       # 2000 lines — User, Product, Order, Cart, Payment, Review, Inventory, Category
        views.py        # 1500 lines — all HTTP handlers
        serializers.py  # 800 lines — DRF serializers for every model
        tasks.py        # 600 lines — Celery tasks (email, report generation, cache warming)
        utils.py        # 400 lines — shared helpers (formatting, validation, pricing)
        admin.py        # 300 lines — Django admin config
      ```

      The team plans to split this into a service-oriented architecture with
      independent deployability, separate databases per service, and each service
      owning its data.

      Design a decomposition into services. For each service, specify:
      1. Service name and responsibility
      2. The models/tables it owns (exclusively)
      3. The API endpoints or message contracts it exposes
      4. Inter-service communication pattern (sync HTTP, async event, or both)
      5. Data consistency model (strong vs eventual)

      Additionally:
      - Identify which service should own user authentication
      - Describe how an order creation flow crosses service boundaries
      - Specify at least 2 async events that services publish/subscribe to
    expected_behaviors:
      - services
      - data ownership
      - service boundary
    judge_criteria:
      - "Services are cohesive (not splitting one model per service)"
      - "No circular dependencies between services"
      - "Order creation flow correctly involves Cart, Order, Payment, Inventory, Notification"

  - id: arch-02
    name: "Interface design — plugin system for data exporters"
    description: "Design a Go interface for a pluggable data export system"
    tags: [architecture, interfaces, go]
    prompt: |
      A reporting system needs a plugin-based data export system. Plugins export
      data in different formats (CSV, Excel, PDF, JSON). The system should:
      - Allow new export formats without changing the core
      - Support configuration per export (filename, compression, headers)
      - Handle large datasets via streaming (not loading all in memory)
      - Report progress and support cancellation
      - Surface errors specific to the export (per-row vs fatal)

      Design the Go interfaces and types. Write the actual code for:
      - The `Exporter` interface (and any related interfaces)
      - The `ExportConfig` type
      - The `ExportResult` type
      - A `Registry` that manages registered exporters
      - One concrete implementation: CSVExporter

      Key design decisions to address:
      - How does progress reporting work without coupling to a UI framework?
      - How does cancellation propagate through streaming?
      - How does per-row vs fatal error distinction work?
      - How are plugins registered (compile-time vs runtime)?

      Write the actual Go code, not pseudocode. Use idiomatic Go patterns.
    expected_behaviors:
      - Exporter interface
      - context.Context
      - CSVExporter
    judge_criteria:
      - "Exporter interface has Export(ctx, data, config) and returns (<-chan Progress, Result)"
      - "ExportConfig is a struct, not a map[string]interface{}"
      - "Registry uses init() registration or explicit Register() pattern"
      - "CSVExporter handles streaming (io.Writer, not string buffer)"

  - id: arch-03
    name: "Dependency management — dependency inversion in Python"
    description: "Apply dependency inversion to decouple a notification system from its transports"
    tags: [architecture, dependency-inversion, python]
    prompt: |
      This notification system is tightly coupled to specific transport implementations.
      Refactor it using dependency inversion so that:
      - The core notification logic doesn't import any transport directly
      - New transports (SMS, push, Slack, Teams) can be added without modifying core
      - Transport selection is done via configuration, not if/else chains

      ```python
      # notification.py — current code
      import smtplib
      from email.message import EmailMessage
      import requests

      class EmailSender:
          def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
              self.smtp_host = smtp_host
              self.smtp_port = smtp_port
              self.username = username
              self.password = password

          def send(self, to: str, subject: str, body: str) -> bool:
              msg = EmailMessage()
              msg.set_content(body)
              msg["Subject"] = subject
              msg["To"] = to
              msg["From"] = self.username

              with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                  server.login(self.username, self.password)
                  server.send_message(msg)
              return True

      class SlackSender:
          def __init__(self, webhook_url: str):
              self.webhook_url = webhook_url

          def send(self, channel: str, message: str) -> bool:
              resp = requests.post(self.webhook_url, json={"channel": channel, "text": message})
              return resp.status_code == 200

      class NotificationService:
          def __init__(self):
              self.email = EmailSender("smtp.example.com", 587, "user", "pass")
              self.slack = SlackSender("https://hooks.slack.com/xxx")

          def notify(self, user_email: str, slack_channel: str, message: str):
              self.email.send(user_email, "Notification", message)
              self.slack.send(slack_channel, message)
      ```

      Design the refactored architecture. Write:
      1. The abstract `Transport` protocol class (using `abc` or `Protocol`)
      2. The refactored `NotificationService` (depends on abstractions)
      3. A `TransportFactory` that creates transports from config
      4. Example config (YAML or dict) and wiring

      Also describe: how would you handle transports with different parameters
      (Slack needs a channel, Email needs a subject)?
    expected_behaviors:
      - Transport
      - NotificationService
      - dependency inversion
    judge_criteria:
      - "Transport ABC has a generic send(to, message) or similar signature"
      - "NotificationService does NOT import smtplib or requests"
      - "Configuration-driven factory allows adding transports without code changes"

  - id: arch-04
    name: "Data flow design — event-driven analytics pipeline"
    description: "Design a data flow for real-time user analytics"
    tags: [architecture, data-flow, events]
    prompt: |
      A SaaS product needs a real-time analytics pipeline. Every user action
      (page view, click, API call, error) should be available in dashboards
      within 30 seconds. The architecture must handle 100K events/second at peak.

      Current stack: PostgreSQL, Redis, Python, Kafka.

      Constraints:
      - Raw events must be retained for 90 days for replay/re-audit
      - Aggregated metrics (DAU, page views, error rates) must be queryable
        with sub-second latency
      - The dashboard queries should not impact event ingestion
      - Cost efficiency matters — hot storage is expensive

      Design the data flow from event ingestion to dashboard query. For each stage:
      1. Component name and role
      2. Data format at that stage
      3. Storage medium and retention policy
      4. Scaling approach (partitioning, sharding)
      5. Failure mode (what happens when this component is down)

      Also design:
      - The schema (or structure) for raw events vs aggregated metrics
      - How 30-second freshness is achieved
      - How backpressure works if downstream falls behind
      - At-least-once vs exactly-once semantics per stage

      Write your answer as a clear architecture description with a data flow diagram
      (text-based is fine) and rationale for each design decision.
    expected_behaviors:
      - pipeline
      - Kafka
      - ingestion
    judge_criteria:
      - "Pipeline has distinct stages for ingestion, enrichment, aggregation, serving"
      - "Uses Kafka for buffering/decoupling, not as primary store"
      - "Aggregates are pre-computed and stored in Redis/ClickHouse/Druid"
      - "Backpressure mechanism is described (Kafka consumer lag, dead-letter queue)"

  - id: arch-05
    name: "State management — distributed counter service"
    description: "Design a globally distributed counter service with strong consistency"
    tags: [architecture, state-management, distributed-systems]
    prompt: |
      Design a distributed counter service API with these requirements:

      - `Increment(counter_name: str, delta: int) -> int` — returns new value
      - `Get(counter_name: str) -> int` — returns current value
      - Counters have TTL and auto-expire after inactivity
      - Must handle 1M increments/second globally
      - Counters must be strongly consistent (read-your-writes)
      - The system spans 3 regions (US, EU, APAC)
      - Latency target: <10ms P99 for both operations

      You cannot use a single centralized database (too slow cross-region).
      You cannot use CRDTs (too complex for this use case — but explain why
      someone might suggest this).

      Design a solution. Address:
      - How strong consistency is achieved across regions
      - How the 10ms latency target is met
      - How TTL expiration works (lazy vs active)
      - What happens during a region failure
      - The trade-offs you're accepting

      Provide an architecture diagram (text-based), key data structures,
      and the API contract (protobuf or OpenAPI).
    expected_behaviors:
      - consistent hashing
      - primary region
      - failover
    judge_criteria:
      - "Design assigns each counter to a primary region via consistent hashing"
      - "Cross-region reads go to primary region (or use async replication + read-repair)"
      - "TTL uses lazy expiration (check on read) + periodic cleanup"
      - "Trade-offs explicitly stated (e.g., write latency higher for remote primaries)"

  - id: arch-06
    name: "Error boundary design — resilient microservices"
    description: "Design error boundaries and resilience patterns for a multi-service checkout flow"
    tags: [architecture, error-boundaries, resilience]
    prompt: |
      An e-commerce checkout flow involves these services:

      ```
      Client → API Gateway → Cart Service → Order Service → Payment Service
                                                              ↓
                                                    Inventory Service
                                                              ↓
                                                    Shipping Service
                                                              ↓
                                                    Notification Service
      ```

      The flow steps:
      1. Cart → validate cart contents
      2. Order → create order record (idempotency key required)
      3. Payment → charge payment method
      4. Inventory → reserve items
      5. Shipping → create shipping label
      6. Notification → send confirmation

      Problems to solve:
      - Payment succeeds but Inventory reservation fails → order is paid but no stock
      - Shipping service is down → entire checkout fails even though order is valid
      - Network timeout to Payment → was the charge made or not?
      - Cart → Order has a race: user submits twice → two orders created

      Design error boundaries and recovery mechanisms for each service boundary.
      For each inter-service call, specify:
      1. Timeout and retry policy (how many retries? exponential backoff? jitter?)
      2. Circuit breaker threshold
      3. Fallback behavior (fail fast? queue for retry? return cached/default?)
      4. Saga/compensation action on failure
      5. Idempotency strategy

      Also design the orchestration pattern:
      - Choreography (each service talks to next) vs Orchestration (central coordinator)
      - Which pattern is better here and why?
      - What does the saga compensation flow look like?

      Write specific configuration values (numbers), not generic advice.
    expected_behaviors:
      - saga
      - compensation
      - circuit breaker
    judge_criteria:
      - "Retry policies differ per service (Payment = 1 retry with 100ms, Shipping = 3 retries)"
      - "Saga compensation: if Inventory fails → cancel Payment (call Payment.reverse)"
      - "Idempotency uses request ID header on Order and Payment"
      - "Circuit breaker thresholds are specified (e.g., 5 failures in 30s → open 60s)"

  - id: arch-07
    name: "API design — RESTful resource hierarchy"
    description: "Design REST API endpoints for a multi-tenant project management system"
    tags: [architecture, api-design, rest]
    prompt: |
      Design a RESTful API for a multi-tenant project management system.

      Requirements:
      - Organizations have users, projects, and teams
      - Projects have tasks with assignees, status, priority, due dates
      - Tasks have comments, attachments, and time entries
      - Users can belong to multiple organizations
      - All resources are scoped to an organization
      - Need bulk operations: assign multiple tasks, move tasks between projects
      - Need partial update (PATCH) for task status changes only
      - 50M+ tasks per organization (pagination is critical)

      Design the URL hierarchy, HTTP methods, query parameters, and response formats.

      For each endpoint specify:
      - URL pattern
      - HTTP methods (what each does)
      - Required authentication scopes (if any)
      - Pagination approach (cursor vs offset)
      - Key query parameters for filtering/sorting
      - Example curl command

      Additional design decisions:
      - How to handle bulk operations (custom endpoint? batch?)
      - How to nest resources vs flatten (tasks under projects vs /api/tasks?)
      - Response envelope format (wrapping in {data, meta} or just the resource?)
      - How to represent tenant ID (path param / header / domain?)
      - How to version the API

      Provide one endpoint group fully specified (e.g., tasks) with all methods,
      and a summary of the remaining resources.
    expected_behaviors:
      - /api/v1/
      - cursor-based
      - multi-tenancy
    judge_criteria:
      - "URLs follow pattern /api/v1/orgs/:org_id/projects/:project_id/tasks"
      - "Task list supports filter[status]=, filter[assignee_id]=, sort=-created_at"
      - "Bulk operations use POST /tasks/batch with {actions: [...]}"
      - "PATCH /tasks/:id for partial updates with only changed fields"

  - id: arch-08
    name: "Database schema design — time-series billing data"
    description: "Design a schema for high-volume billing and usage metering"
    tags: [architecture, schema-design, sql]
    prompt: |
      A SaaS platform needs to meter customer usage for billing. Requirements:

      - Track usage events: API calls, storage (GB-hours), compute (CPU-seconds)
      - 10K customers, each 100K events/day → 1B events/day at peak
      - Queries: "total usage for customer X in date range Y" (sub-second)
      - Queries: "current month-to-date usage for customer X for real-time dashboard"
      - Bills are generated monthly but need daily usage snapshots for audit
      - Usage events arrive in real-time (Kafka) and batch (daily CSVs)
      - Retention: raw events 90 days, aggregated data 7 years
      - PostgreSQL is the primary database (you can add extensions)

      Design the schema (tables, indexes, partitions, materialized views).
      Address:
      - Partitioning strategy (by time? by customer? by metric type?)
      - Pre-aggregation strategy (hourly/daily/monthly rollups)
      - How raw events vs aggregated data are stored
      - How concurrent writes (100s/sec) don't block billing reads
      - How backfilling works (correcting past usage data)
      - Which PostgreSQL features/extensions help (pg_partman, TimescaleDB?)

      Write the actual CREATE TABLE statements with proper partitioning, indexes,
      and constraints. Also write the query for "month-to-date usage for customer X"
      that runs in <100ms.
    expected_behaviors:
      - PARTITION BY
      - hourly rollup
      - CREATE TABLE
    judge_criteria:
      - "Raw events table is partitioned by month (or week)"
      - "Hourly rollup table: customer_id, metric_type, hour, sum(value), count"
      - "Month-to-date query uses pre-aggregated hourly data"
      - "Backfilling strategy handles late-arriving data (upsert on hourly aggregates)"

  - id: arch-09
    name: "Authentication flow design — OAuth2 + JWT"
    description: "Design the auth flow for a multi-service architecture"
    tags: [architecture, authentication, security]
    prompt: |
      Design a complete authentication flow for a microservices architecture with:

      - A React SPA frontend
      - 5 backend services (API Gateway, Users, Orders, Payments, Notifications)
      - Third-party OAuth2 providers (Google, GitHub)
      - The system issues JWTs for service-to-service auth

      Requirements:
      - Users log in via OAuth2 (Google/GitHub) OR email+password
      - Session persists for 24h (access) + 7d (refresh)
      - Services authenticate each other with mTLS OR JWTs
      - A user's session must be revocable (logout everywhere)
      - Rate limiting per authenticated user, not per IP
      - Must handle token refresh without user re-authentication

      Design:
      1. The complete login flow (OAuth2 and email/password)
      2. Token format (JWT claims) for access tokens
      3. Refresh token strategy (rotation? opaque vs JWT?)
      4. Service-to-service auth mechanism
      5. Session revocation mechanism (blacklist? short TTL?)
      6. How the frontend stores and sends tokens
      7. How rate limiting works per authenticated user

      Write the JWT payload structure (with specific claim names and example values),
      the middleware pseudocode for token validation in the API Gateway,
      and the refresh token rotation protocol.
    expected_behaviors:
      - JWT
      - refresh token
      - OAuth2
    judge_criteria:
      - "Access JWT contains: sub, org_id, roles, iat, exp, jti"
      - "Refresh token is opaque (not JWT) stored in DB with family chain"
      - "Gateway validates JWT, extracts user_id for rate limiter key"
      - "Revocation: blacklist jti in Redis with TTL matching token expiry"

  - id: arch-10
    name: "Deployment architecture — zero-downtime migration"
    description: "Design deployment strategy for a stateful service with zero downtime"
    tags: [architecture, deployment, docker]
    prompt: |
      A service manages long-running WebSocket connections (10K concurrent).
      It needs to be deployed 3x/week with zero downtime. Each deployment
      involves a new binary and a database schema migration.

      Current setup:
      - Single Go binary, connected to PostgreSQL
      - WebSocket connections hold state (1-2MB each)
      - The service is behind a load balancer (HTTP + WebSocket)
      - Deployed via Docker on Kubernetes

      Problems:
      - Graceful shutdown: old pods get SIGTERM, but WebSocket clients reconnect
        and lose 1-2s of in-flight messages
      - DB migration: ALTER TABLE ADD COLUMN locks the table for minutes on large tables
      - Connection draining: k8s removes pods from service before preStop hook finishes
      - State migration: some deploys change the WebSocket message protocol (v1→v2)

      Design the deployment architecture addressing each problem:

      1. **Graceful shutdown**: design the signal handling and connection drain flow
      2. **Zero-downtime migrations**: expand-contract pattern (add column → dual-write → backfill → drop old)
      3. **Connection draining**: configure preStop, readiness probe, and timing
      4. **Protocol versioning**: how to handle mixed old/new clients during rolling update
      5. **Rollback**: how to detect a bad deploy and roll back without data loss

      Write the actual:
      - Kubernetes preStop hook script (shell)
      - Signal handler pseudocode in Go
      - Migration sequence for "add a required field to the message schema"
      - Rollback decision criteria and procedure
    expected_behaviors:
      - expand-contract
      - preStop
      - zero-downtime
    judge_criteria:
      - "PreStop: drains existing connections up to max 60s, then SIGTERM"
      - "DB migration uses expand-contract (add column nullable → dual-write → backfill → make NOT NULL → drop dual-write)"
      - "Protocol versioning uses version field in messages, client advertises supported range"
      - "Rollback criteria: error rate > 5% for 60s triggers automated rollback"
---
