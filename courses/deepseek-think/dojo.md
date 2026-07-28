---
course: deepseek-think
title: DeepSeek Reasoning & Analysis
description: 10 scenarios testing reasoning, analysis, and multi-step thinking — logical deduction, constraint satisfaction, multi-step planning, trade-off analysis, cause-effect reasoning, counterfactual thinking, prioritization, risk assessment, requirement ambiguity resolution, analytical decomposition
difficulty: standard
model: deepseek-v4-flash
scenarios:
  - id: think-01
    name: "Logical deduction puzzle"
    description: "Solve a logic puzzle using step-by-step deduction"
    tags: [reasoning, logic]
    prompt: |
      Four services — Auth, Orders, Payments, Notifications — are deployed across four
      servers (S1–S4). Each server runs exactly one service. Use the clues below to
      determine which service runs on each server.

      Clues:
      1. Auth runs on an even-numbered server.
      2. Orders does not run on S1.
      3. Payments runs on a server whose number is greater than Auth's but less than Notifications'.
      4. Notifications runs two servers away from Auth (exactly one server between them).
      5. The sum of the server numbers for Orders and Payments is 5.

      Show your reasoning step by step, then state the final mapping.
    expected_behaviors:
      - S1
      - S2
      - Auth
    judge_criteria:
      - "All five clues are used in the reasoning"
      - "Final mapping is correct and consistent"

  - id: think-02
    name: "Constraint satisfaction — resource scheduling"
    description: "Schedule 5 batch jobs on 3 GPUs minimizing total runtime given constraints"
    tags: [reasoning, scheduling, constraint-satisfaction]
    prompt: |
      Five ML training jobs (A–E) must run on 3 identical GPUs (G1, G2, G3). Each job has a
      duration in hours and a GPU memory requirement in GB:

      - Job A: 3h, 8GB
      - Job B: 4h, 16GB
      - Job C: 2h, 8GB
      - Job D: 5h, 32GB
      - Job E: 1h, 8GB

      Constraints:
      - Each GPU has 32GB memory.
      - A GPU can run multiple jobs at once as long as total memory ≤ 32GB.
      - A job cannot be split across GPUs.
      - All jobs start at the same time t=0.
      - Dependencies: D must finish before A starts. E must finish before B starts.

      Find an assignment that minimizes the makespan (time when all jobs finish).
      Show your reasoning.
    expected_behaviors:
      - GPU
      - makespan
      - memory
    judge_criteria:
      - "All constraints are satisfied"
      - "Schedule minimizes makespan (8h or 9h is optimal)"
      - "Reasoning explains why alternative schedules are worse"

  - id: think-03
    name: "Multi-step planning — data pipeline"
    description: "Plan an ETL pipeline execution order given data dependencies and failures"
    tags: [reasoning, planning, data-engineering, python, sql]
    prompt: |
      You manage 6 ETL steps (T1–T6) with these properties:

      T1: extracts from source A → outputs table X (10 min, 90% success rate)
      T2: extracts from source B → outputs table Y (8 min, 85% success rate)
      T3: joins X and Y → outputs table Z (15 min, fails if X or Y missing)
      T4: aggregates Z → outputs table W (5 min, 95% success rate)
      T5: loads W to warehouse → outputs table R (3 min, 99% success rate)
      T6: sends notification email (2 min, 100% success rate, runs after T5)

      Each step costs $1 per minute of runtime when it runs, whether it succeeds or fails.
      A failed step can be retried immediately (same cost again).
      The pipeline has a budget of $60.

      The pipeline is currently orchestrated as:

      ```python
      from datetime import datetime
      import random

      def run_pipeline(seed=None):
          random.seed(seed)
          cost = 0
          outcome = {}

          # T1 and T2 run in parallel
          t1_ok = random.random() < 0.90
          t2_ok = random.random() < 0.85
          cost += 10 + 8
          # ... rest of sequential logic

          return cost, outcome
      ```

      And the target warehouse schema:

      ```sql
      CREATE TABLE warehouse.analytics (
          id SERIAL PRIMARY KEY,
          metric_type VARCHAR(50),
          value DECIMAL(12,4),
          computed_at TIMESTAMP DEFAULT now()
      );
      ```

      Design a run plan that maximizes the probability of completing the full pipeline
      within budget. Consider retry strategies: retry all failures immediately, or
      conditionally retry only some steps. Show the expected cost and success probability.
    expected_behaviors:
      - retry
      - probability
      - pipeline
    judge_criteria:
      - "Dependency graph is correctly identified"
      - "Cost model is applied consistently"
      - "Recommended strategy is justified with probability calculations"

  - id: think-04
    name: "Trade-off analysis — caching strategy"
    description: "Compare caching strategies for a social media feed API"
    tags: [reasoning, tradeoffs, system-design, typescript]
    prompt: |
      A social media app serves user feeds via a TypeScript API that aggregates posts
      from followed accounts:

      ```typescript
      async function getFeed(userId: string): Promise<Post[]> {
        const follows = await db.query(
          "SELECT followee_id FROM follows WHERE follower_id = $1", [userId]
        );
        // follows = 200 followees

        const allPosts: Post[] = [];
        for (const f of follows) {
          const posts = await db.query(
            "SELECT * FROM posts WHERE author_id = $1 ORDER BY created_at DESC LIMIT 50",
            [f.followee_id]
          );
          allPosts.push(...posts);
        }
        // allPosts = 10,000 posts for 200 followees × 50 each

        return allPosts.sort((a, b) => b.created_at - a.created_at).slice(0, 100);
      }
      ```

      Each request requires:
      1. Fetch 200 follow relationships (2ms each)
      2. Fetch latest 50 posts per followed user (1ms each) → 10,000 fetches
      3. Merge and rank 10,000 posts by recency (5ms)

      Options:
      A. Cache entire feed per user for 30s (stale read tolerance = 10s, cache miss = full computation)
      B. Cache individual posts for 60s, merge on read (cache miss per post)
      C. Cache follow graph for 300s + cache posts for 60s, merge on read
      D. No caching — compute on every request

      Traffic: 1,000 feed requests/second. Data: 1M users, 50M posts.
      Cache hit ratio: option A = 90%, B = 95% per post (but 10k posts/request),
      C = follow 99% + post 95%.

      Estimate the latency P50 and P99 for each option. Recommend one and explain why.
      State any assumptions you make about cache server overhead.
    expected_behaviors:
      - latency
      - cache
      - Option
    judge_criteria:
      - "Latency estimates are consistent with the given costs"
      - "Recommendation addresses both average and tail latency"
      - "Assumptions about overhead are stated and reasonable"

  - id: think-05
    name: "Cause-effect reasoning — production outage"
    description: "Root cause analysis of a production incident from observability data"
    tags: [reasoning, root-cause, observability, go]
    prompt: |
      At 14:32 UTC, users of a payment API started receiving HTTP 503 errors.
      By 14:35, pager duty alerted the on-call engineer. The team collected this timeline:

      14:28 — Deploy v2.14.3 rolled out to 20% of instances (canary). Changes: upgraded
              payment-gateway client library from v3.1.0 → v4.0.0, added new fraud-check
              middleware.
      14:30 — Payment success rate dropped from 99.2% to 87%.
      14:31 — Payment-gateway client error rate spiked from 0.5% to 12%.
      14:32 — Database connection pool (max 100) hit 100% utilization.
      14:33 — Canary rolled back to v2.14.2.
      14:34 — DB pool dropped to 60% utilization, error rate returned to 0.5%.
      14:35 — Pager alerted.

      The new fraud-check middleware code:

      ```go
      func FraudCheckMiddleware(next http.Handler) http.Handler {
          return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
              db := getDB(r) // gets a connection from pool
              // Holds db connection during 3 external API calls
              score := callFraudService(r.Context(), r.Header.Get("x-session"))
              history := callHistoryService(r.Context(), r.Header.Get("x-user-id"))
              geo := callGeoService(r.Context(), r.RemoteAddr)
              // ... evaluate score
              next.ServeHTTP(w, r)
              db.Close() // connection returned here
          })
      }
      ```

      Additional data:
      - The new fraud-check middleware makes 3 external API calls per request.
      - Each external call holds a DB connection for the call duration (avg 200ms).
      - The payment-gateway v4.0.0 changelog mentions: "Deprecated: v3 client's
        synchronous retry. Use async retry or configure retry interceptor."

      Trace through the causal chain. What was the root cause? What three things should
      the team do to prevent a recurrence?
    expected_behaviors:
      - root cause
      - retry
      - DB connection
    judge_criteria:
      - "Correctly identifies the payment-gateway retry change as root cause"
      - "Explains the DB connection exhaustion mechanism"
      - "Recommendations are concrete (not 'improve monitoring')"

  - id: think-06
    name: "Counterfactual thinking — test strategy"
    description: "Given a bug report and the fix, determine what test would have caught it"
    tags: [reasoning, testing, counterfactual, python]
    prompt: |
      Bug fix commit message:

      ```
      fix: handle empty Content-Type header in request parser

      The request parser assumed Content-Type was always present when
      parsing POST bodies. If a client sent POST /api/data without a
      Content-Type header, bodyParser crashed with a KeyError on
      headers['Content-Type'].

      Fix: Use .get() with default 'application/octet-stream' on the
      headers dict.

      -  content_type = headers['Content-Type']
      +  content_type = headers.get('Content-Type', 'application/octet-stream')
      ```

      Parse this output from a fuzz test run against the code BEFORE the fix:

      ```
      ============================== test session ==============================
      collected 0 items / 1 deselected / 1 selected
      test_fuzz.py::test_parse_requests PASSED
      ```

      The fuzz test generated 1,000 random HTTP requests including 10 without
      Content-Type. Yet it passed. Explain how this counterfactual is possible.
      Then design a test (in any language) that would have caught the bug.
    expected_behaviors:
      - Content-Type
      - fuzz
      - KeyError
    judge_criteria:
      - "Explanation identifies the test's error checking (no exception check)"
      - "Test explicitly sends a POST without Content-Type"
      - "Test asserts that no exception is raised (or returns correct default)"

  - id: think-07
    name: "Prioritization — security vulnerabilities"
    description: "Prioritize 6 open vulnerabilities by risk: likelihood × impact"
    tags: [reasoning, prioritization, security]
    prompt: |
      You manage a SaaS product with 10,000 active users. Six vulnerabilities are
      reported. Prioritize them (1 = fix first) using risk = likelihood × impact.

      A. SQL injection in admin reports endpoint — requires authenticated admin
         session with a specific role. Attacker must be inside the VPN.
         Likelihood: low. Impact: can read all user data.

      B. XSS in user profile bio field — stored, no sanitization. Renders in
         public profile pages. Any visitor can trigger it.
         Likelihood: high. Impact: session theft for profile viewers.

      C. Rate limiting missing on password reset — no cap on reset attempts.
         Likelihood: medium. Impact: account takeover if weak password is guessed.

      D. Dependency with known CVE-2024-XXXX (CVSS 9.8) in image-processing
         library used in user avatar upload. Requires multipart POST with crafted
         image. Not directly accessible to unauthenticated users.
         Likelihood: low. Impact: remote code execution on the upload server.

      E. Information disclosure in error pages — stack traces shown to users
         on 500 errors. Affects all endpoints.
         Likelihood: medium. Impact: internal path/query structure leaked.

      F. Weak session cookie — no Secure flag, no HttpOnly flag, SameSite=None.
         Likelihood: high (if any XSS exists). Impact: session hijacking.

      Show your risk scoring for each, then the ranked priority list. Explain any
      dependencies among fixes (e.g., F depends on B being fixed first).
    expected_behaviors:
      - likelihood
      - impact
      - priority
    judge_criteria:
      - "Scoring is consistent with the descriptions"
      - "Dependency between B and F is identified"
      - "Ranking accounts for exploitability, not just CVSS"

  - id: think-08
    name: "Risk assessment — migration plan"
    description: "Evaluate risks in a database migration plan and suggest mitigations"
    tags: [reasoning, risk-assessment, databases, sql, shell]
    prompt: |
      A team plans to migrate a production PostgreSQL database from a single EC2 instance
      (500GB, serving 5,000 req/s, 99.95% uptime target) to Amazon RDS Aurora. The current
      schema includes this migration script:

      ```sql
      -- Migration V23: add partition key to orders table
      ALTER TABLE orders ADD COLUMN org_id INTEGER NOT NULL DEFAULT 1;
      CREATE INDEX idx_orders_org_created ON orders(org_id, created_at);
      ```

      And the deploy script used to apply schema changes:

      ```bash
      #!/bin/bash
      # apply_migration.sh
      set -euo pipefail
      for f in migrations/*.sql; do
        echo "Applying $f..."
        psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f "$f"
      done
      echo "Migration complete"
      ```

      The migration plan:

      Phase 1 (Week 1): Set up Aurora cluster, configure replication from current DB.
      Phase 2 (Week 2): Run application in read-only mode against Aurora for 48h to
                        validate. Both DBs running simultaneously.
      Phase 3 (Week 3): Cutover — stop writes to old DB, verify Aurora is caught up,
                        switch DNS to Aurora writer endpoint.
      Phase 4 (Week 4): Decommission old EC2 instance.

      Identify at least 5 specific risks (not generic "something could go wrong") in
      this plan. For each risk, assess severity (low/med/high) and propose a concrete
      mitigation. Finally, evaluate whether a blue-green or rolling cutover is safer
      and why.
    expected_behaviors:
      - risk
      - severity
      - mitigation
    judge_criteria:
      - "Risks are specific (e.g., 'replication lag during Phase 2 validation')"
      - "Mitigations are actionable, not platitudes"
      - "Cutover recommendation addresses trade-offs between speed and safety"

  - id: think-09
    name: "Requirement ambiguity resolution"
    description: "Identify ambiguities in a product spec and resolve them with questions"
    tags: [reasoning, requirements, analysis]
    prompt: |
      Product manager sends this spec for a new feature:

      ```
      Feature: Smart Retry for failed API calls

      When a payment API call fails, the system should automatically retry
      with exponential backoff. Retry up to 3 times. Log all retries and
      notify the support team if all retries fail. The retry should be
      "smart" — don't retry if the error is permanent.
      ```

      Identify at least 6 ambiguities or missing details in this spec.
      For each ambiguity:
      1. State the ambiguity clearly.
      2. Propose two possible interpretations.
      3. Ask the specific clarifying question you would send to the PM.

      Then write the clarified, unambiguous version of the spec (as a single
      paragraph a developer could implement from).
    expected_behaviors:
      - ambiguity
      - retry
      - exponential backoff
    judge_criteria:
      - "Ambiguities cover: retry scope, error classification, backoff params,
         notification method, idempotency, timeout interaction"
      - "Clarified spec leaves no identified ambiguity unresolved"
      - "Questions are precise and answerable by a non-technical PM"

  - id: think-10
    name: "Analytical decomposition — API latency problem"
    description: "Break down a performance problem into measurable sub-problems"
    tags: [reasoning, analysis, performance, python, sql]
    prompt: |
      An API endpoint `GET /api/dashboard` that returns a user's aggregated analytics
      data takes 12 seconds to respond. The stack is:

      - Python FastAPI backend
      - PostgreSQL database (10M rows in analytics_events table)
      - Redis cache for pre-computed aggregates
      - 10 downstream microservices called in sequence

      The endpoint's current code structure:

      ```python
      @app.get("/api/dashboard")
      async def get_dashboard(user_id: str):
          # Step A: auth check — 50ms
          user = await verify_token(request.headers["Authorization"])

          # Step B: fetch 10 downstream services in sequence — 8s total
          data = []
          for svc in DOWNSTREAM_SERVICES:
              data.append(await fetch_from_service(svc, user_id))

          # Step C: compute aggregates from DB — 3s
          aggregates = await db.fetch("""
              SELECT event_type, COUNT(*), AVG(value)
              FROM analytics_events
              WHERE user_id = $1 AND created_at > now() - interval '30 days'
              GROUP BY event_type
          """, user_id)

          # Step D: merge results — 0.5s
          result = merge(data, aggregates)

          # Step E: cache result for 5 minutes — 0.5s
          await redis.set(f"dash:{user_id}", serialize(result), ex=300)

          return result
      ```

      Decompose the problem into sub-problems. For each sub-problem:
      1. List possible causes (at least 3 per sub-problem)
      2. Describe a measurement or experiment that would confirm or rule out each cause
      3. Estimate the potential improvement if that cause is addressed

      After decomposition, produce a ranked action plan with estimated total impact.
    expected_behaviors:
      - sub-problem
      - latency
      - diagnostic
    judge_criteria:
      - "Sub-problems include: sequential service calls, DB query performance,
         cache miss penalty, N+1 patterns, serialization overhead"
      - "Diagnostic experiments are specific (e.g., 'add trace spans around each
         downstream call to measure per-service latency')"
      - "Action plan estimates are internally consistent"
---
