course: deepseek-think
title: DeepSeek Reasoning & Analysis
description: 10 scenarios testing reasoning, analysis, and multi-step thinking — logical
  deduction, constraint satisfaction, multi-step planning, trade-off analysis, cause-effect
  reasoning, counterfactual thinking, prioritization, risk assessment, requirement
  ambiguity resolution, analytical decomposition
difficulty: standard
model: deepseek-v4-flash
scenarios:
- id: think-01
  name: Logical deduction puzzle
  description: Solve a logic puzzle using step-by-step deduction
  tags:
  - reasoning
  - logic
  prompt: 'Four services — Auth, Orders, Payments, Notifications — are deployed across
    four

    servers (S1–S4). Each server runs exactly one service. Use the clues below to

    determine which service runs on each server.


    Clues:

    1. Auth runs on an even-numbered server.

    2. Orders does not run on S1.

    3. Payments runs on a server whose number is greater than Auth''s but less than
    Notifications''.

    4. Notifications runs two servers away from Auth (exactly one server between them).

    5. The sum of the server numbers for Orders and Payments is 5.


    Answer directly with the final mapping.

    '
  expected_behaviors:
  - S1
  - S2
  - Auth
  judge_criteria:
  - All five clues are used in the reasoning
  - Final mapping is correct and consistent
- id: think-02
  name: Constraint satisfaction — resource scheduling
  description: Schedule 5 batch jobs on 3 GPUs minimizing total runtime given constraints
  tags:
  - reasoning
  - scheduling
  - constraint-satisfaction
  prompt: 'Five ML training jobs (A–E) must run on 3 identical GPUs (G1, G2, G3).
    Each job has a

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

    Just give the answer.

    '
  expected_behaviors:
  - GPU
  - makespan
  - memory
  judge_criteria:
  - All constraints are satisfied
  - Schedule minimizes makespan (8h or 9h is optimal)
  - Reasoning explains why alternative schedules are worse
- id: think-03
  name: Multi-step planning — data pipeline
  description: Plan an ETL pipeline execution order given data dependencies and failures
  tags:
  - reasoning
  - planning
  - data-engineering
  - python
  - sql
  prompt: "You manage 6 ETL steps (T1–T6) with these properties:\n\nT1: extracts from\
    \ source A → outputs table X (10 min, 90% success rate)\nT2: extracts from source\
    \ B → outputs table Y (8 min, 85% success rate)\nT3: joins X and Y → outputs table\
    \ Z (15 min, fails if X or Y missing)\nT4: aggregates Z → outputs table W (5 min,\
    \ 95% success rate)\nT5: loads W to warehouse → outputs table R (3 min, 99% success\
    \ rate)\nT6: sends notification email (2 min, 100% success rate, runs after T5)\n\
    \nEach step costs $1 per minute of runtime when it runs, whether it succeeds or\
    \ fails.\nA failed step can be retried immediately (same cost again).\nThe pipeline\
    \ has a budget of $60.\n\nThe pipeline is currently orchestrated as:\n\n```python\n\
    from datetime import datetime\nimport random\n\ndef run_pipeline(seed=None):\n\
    \    random.seed(seed)\n    cost = 0\n    outcome = {}\n\n    # T1 and T2 run\
    \ in parallel\n    t1_ok = random.random() < 0.90\n    t2_ok = random.random()\
    \ < 0.85\n    cost += 10 + 8\n    # ... rest of sequential logic\n\n    return\
    \ cost, outcome\n```\n\nAnd the target warehouse schema:\n\n```sql\nCREATE TABLE\
    \ warehouse.analytics (\n    id SERIAL PRIMARY KEY,\n    metric_type VARCHAR(50),\n\
    \    value DECIMAL(12,4),\n    computed_at TIMESTAMP DEFAULT now()\n);\n```\n\n\
    Design a run plan that maximizes the probability of completing the full pipeline\n\
    within budget. Consider retry strategies: retry all failures immediately, or\n\
    conditionally retry only some steps. Show the expected cost and success probability.\n"
  expected_behaviors:
  - retry
  - probability
  - pipeline
  judge_criteria:
  - Dependency graph is correctly identified
  - Cost model is applied consistently
  - Recommended strategy is justified with probability calculations
- id: think-04
  name: Trade-off analysis — caching strategy
  description: Compare caching strategies for a social media feed API
  tags:
  - reasoning
  - tradeoffs
  - system-design
  - typescript
  prompt: "A social media app serves user feeds via a TypeScript API that aggregates\
    \ posts\nfrom followed accounts:\n\n```typescript\nasync function getFeed(userId:\
    \ string): Promise<Post[]> {\n  const follows = await db.query(\n    \"SELECT\
    \ followee_id FROM follows WHERE follower_id = $1\", [userId]\n  );\n  // follows\
    \ = 200 followees\n\n  const allPosts: Post[] = [];\n  for (const f of follows)\
    \ {\n    const posts = await db.query(\n      \"SELECT * FROM posts WHERE author_id\
    \ = $1 ORDER BY created_at DESC LIMIT 50\",\n      [f.followee_id]\n    );\n \
    \   allPosts.push(...posts);\n  }\n  // allPosts = 10,000 posts for 200 followees\
    \ × 50 each\n\n  return allPosts.sort((a, b) => b.created_at - a.created_at).slice(0,\
    \ 100);\n}\n```\n\nEach request requires:\n1. Fetch 200 follow relationships (2ms\
    \ each)\n2. Fetch latest 50 posts per followed user (1ms each) → 10,000 fetches\n\
    3. Merge and rank 10,000 posts by recency (5ms)\n\nOptions:\nA. Cache entire feed\
    \ per user for 30s (stale read tolerance = 10s, cache miss = full computation)\n\
    B. Cache individual posts for 60s, merge on read (cache miss per post)\nC. Cache\
    \ follow graph for 300s + cache posts for 60s, merge on read\nD. No caching —\
    \ compute on every request\n\nTraffic: 1,000 feed requests/second. Data: 1M users,\
    \ 50M posts.\nCache hit ratio: option A = 90%, B = 95% per post (but 10k posts/request),\n\
    C = follow 99% + post 95%.\n\nEstimate the latency P50 and P99 for each option.\
    \ Recommend one and explain why.\nState any assumptions you make about cache server\
    \ overhead.\n"
  expected_behaviors:
  - latency
  - cache
  - Option
  judge_criteria:
  - Latency estimates are consistent with the given costs
  - Recommendation addresses both average and tail latency
  - Assumptions about overhead are stated and reasonable
- id: think-05
  name: Cause-effect reasoning — production outage
  description: Root cause analysis of a production incident from observability data
  tags:
  - reasoning
  - root-cause
  - observability
  - go
  prompt: "At 14:32 UTC, users of a payment API started receiving HTTP 503 errors.\n\
    By 14:35, pager duty alerted the on-call engineer. The team collected this timeline:\n\
    \n14:28 — Deploy v2.14.3 rolled out to 20% of instances (canary). Changes: upgraded\n\
    \        payment-gateway client library from v3.1.0 → v4.0.0, added new fraud-check\n\
    \        middleware.\n14:30 — Payment success rate dropped from 99.2% to 87%.\n\
    14:31 — Payment-gateway client error rate spiked from 0.5% to 12%.\n14:32 — Database\
    \ connection pool (max 100) hit 100% utilization.\n14:33 — Canary rolled back\
    \ to v2.14.2.\n14:34 — DB pool dropped to 60% utilization, error rate returned\
    \ to 0.5%.\n14:35 — Pager alerted.\n\nThe new fraud-check middleware code:\n\n\
    ```go\nfunc FraudCheckMiddleware(next http.Handler) http.Handler {\n    return\
    \ http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {\n        db\
    \ := getDB(r) // gets a connection from pool\n        // Holds db connection during\
    \ 3 external API calls\n        score := callFraudService(r.Context(), r.Header.Get(\"\
    x-session\"))\n        history := callHistoryService(r.Context(), r.Header.Get(\"\
    x-user-id\"))\n        geo := callGeoService(r.Context(), r.RemoteAddr)\n    \
    \    // ... evaluate score\n        next.ServeHTTP(w, r)\n        db.Close() //\
    \ connection returned here\n    })\n}\n```\n\nAdditional data:\n- The new fraud-check\
    \ middleware makes 3 external API calls per request.\n- Each external call holds\
    \ a DB connection for the call duration (avg 200ms).\n- The payment-gateway v4.0.0\
    \ changelog mentions: \"Deprecated: v3 client's\n  synchronous retry. Use async\
    \ retry or configure retry interceptor.\"\n\nTrace through the causal chain. What\
    \ was the root cause? What three things should\nthe team do to prevent a recurrence?\n"
  expected_behaviors:
  - root cause
  - retry
  - DB connection
  judge_criteria:
  - Correctly identifies the payment-gateway retry change as root cause
  - Explains the DB connection exhaustion mechanism
  - Recommendations are concrete (not 'improve monitoring')
- id: think-06
  name: Counterfactual thinking — test strategy
  description: Given a bug report and the fix, determine what test would have caught
    it
  tags:
  - reasoning
  - testing
  - counterfactual
  - python
  prompt: 'Bug fix commit message:


    ```

    fix: handle empty Content-Type header in request parser


    The request parser assumed Content-Type was always present when

    parsing POST bodies. If a client sent POST /api/data without a

    Content-Type header, bodyParser crashed with a KeyError on

    headers[''Content-Type''].


    Fix: Use .get() with default ''application/octet-stream'' on the

    headers dict.


    -  content_type = headers[''Content-Type'']

    +  content_type = headers.get(''Content-Type'', ''application/octet-stream'')

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

    '
  expected_behaviors:
  - Content-Type
  - fuzz
  - KeyError
  judge_criteria:
  - Explanation identifies the test's error checking (no exception check)
  - Test explicitly sends a POST without Content-Type
  - Test asserts that no exception is raised (or returns correct default)
- id: think-07
  name: Prioritization — security vulnerabilities
  description: 'Prioritize 6 open vulnerabilities by risk: likelihood × impact'
  tags:
  - reasoning
  - prioritization
  - security
  prompt: "You manage a SaaS product with 10,000 active users. Six vulnerabilities\
    \ are\nreported. Prioritize them (1 = fix first) using risk = likelihood × impact.\n\
    \nA. SQL injection in admin reports endpoint — requires authenticated admin\n\
    \   session with a specific role. Attacker must be inside the VPN.\n   Likelihood:\
    \ low. Impact: can read all user data.\n\nB. XSS in user profile bio field — stored,\
    \ no sanitization. Renders in\n   public profile pages. Any visitor can trigger\
    \ it.\n   Likelihood: high. Impact: session theft for profile viewers.\n\nC. Rate\
    \ limiting missing on password reset — no cap on reset attempts.\n   Likelihood:\
    \ medium. Impact: account takeover if weak password is guessed.\n\nD. Dependency\
    \ with known CVE-2024-XXXX (CVSS 9.8) in image-processing\n   library used in\
    \ user avatar upload. Requires multipart POST with crafted\n   image. Not directly\
    \ accessible to unauthenticated users.\n   Likelihood: low. Impact: remote code\
    \ execution on the upload server.\n\nE. Information disclosure in error pages\
    \ — stack traces shown to users\n   on 500 errors. Affects all endpoints.\n  \
    \ Likelihood: medium. Impact: internal path/query structure leaked.\n\nF. Weak\
    \ session cookie — no Secure flag, no HttpOnly flag, SameSite=None.\n   Likelihood:\
    \ high (if any XSS exists). Impact: session hijacking.\n\nShow your risk scoring\
    \ for each, then the ranked priority list. Explain any\ndependencies among fixes\
    \ (e.g., F depends on B being fixed first).\n"
  expected_behaviors:
  - likelihood
  - impact
  - priority
  judge_criteria:
  - Scoring is consistent with the descriptions
  - Dependency between B and F is identified
  - Ranking accounts for exploitability, not just CVSS
- id: think-08
  name: Risk assessment — migration plan
  description: Evaluate risks in a database migration plan and suggest mitigations
  tags:
  - reasoning
  - risk-assessment
  - databases
  - sql
  - shell
  prompt: "A team plans to migrate a production PostgreSQL database from a single\
    \ EC2 instance\n(500GB, serving 5,000 req/s, 99.95% uptime target) to Amazon RDS\
    \ Aurora. The current\nschema includes this migration script:\n\n```sql\n-- Migration\
    \ V23: add partition key to orders table\nALTER TABLE orders ADD COLUMN org_id\
    \ INTEGER NOT NULL DEFAULT 1;\nCREATE INDEX idx_orders_org_created ON orders(org_id,\
    \ created_at);\n```\n\nAnd the deploy script used to apply schema changes:\n\n\
    ```bash\n#!/bin/bash\n# apply_migration.sh\nset -euo pipefail\nfor f in migrations/*.sql;\
    \ do\n  echo \"Applying $f...\"\n  psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f\
    \ \"$f\"\ndone\necho \"Migration complete\"\n```\n\nThe migration plan:\n\nPhase\
    \ 1 (Week 1): Set up Aurora cluster, configure replication from current DB.\n\
    Phase 2 (Week 2): Run application in read-only mode against Aurora for 48h to\n\
    \                  validate. Both DBs running simultaneously.\nPhase 3 (Week 3):\
    \ Cutover — stop writes to old DB, verify Aurora is caught up,\n             \
    \     switch DNS to Aurora writer endpoint.\nPhase 4 (Week 4): Decommission old\
    \ EC2 instance.\n\nIdentify at least 5 specific risks (not generic \"something\
    \ could go wrong\") in\nthis plan. For each risk, assess severity (low/med/high)\
    \ and propose a concrete\nmitigation. Finally, evaluate whether a blue-green or\
    \ rolling cutover is safer\nand why.\n"
  expected_behaviors:
  - risk
  - severity
  - mitigation
  judge_criteria:
  - Risks are specific (e.g., 'replication lag during Phase 2 validation')
  - Mitigations are actionable, not platitudes
  - Cutover recommendation addresses trade-offs between speed and safety
- id: think-09
  name: Requirement ambiguity resolution
  description: Identify ambiguities in a product spec and resolve them with questions
  tags:
  - reasoning
  - requirements
  - analysis
  prompt: 'Product manager sends this spec for a new feature:


    ```

    Feature: Smart Retry for failed API calls


    When a payment API call fails, the system should automatically retry

    with exponential backoff. Retry up to 3 times. Log all retries and

    notify the support team if all retries fail. The retry should be

    "smart" — don''t retry if the error is permanent.

    ```


    Identify at least 6 ambiguities or missing details in this spec.

    For each ambiguity:

    1. State the ambiguity clearly.

    2. Propose two possible interpretations.

    3. Ask the specific clarifying question you would send to the PM.


    Then write the clarified, unambiguous version of the spec (as a single

    paragraph a developer could implement from).

    '
  expected_behaviors:
  - ambiguity
  - retry
  - exponential backoff
  judge_criteria:
  - 'Ambiguities cover: retry scope, error classification, backoff params, notification
    method, idempotency, timeout interaction'
  - Clarified spec leaves no identified ambiguity unresolved
  - Questions are precise and answerable by a non-technical PM
- id: think-10
  name: Analytical decomposition — API latency problem
  description: Break down a performance problem into measurable sub-problems
  tags:
  - reasoning
  - analysis
  - performance
  - python
  - sql
  prompt: "An API endpoint `GET /api/dashboard` that returns a user's aggregated analytics\n\
    data takes 12 seconds to respond. The stack is:\n\n- Python FastAPI backend\n\
    - PostgreSQL database (10M rows in analytics_events table)\n- Redis cache for\
    \ pre-computed aggregates\n- 10 downstream microservices called in sequence\n\n\
    The endpoint's current code structure:\n\n```python\n@app.get(\"/api/dashboard\"\
    )\nasync def get_dashboard(user_id: str):\n    # Step A: auth check — 50ms\n \
    \   user = await verify_token(request.headers[\"Authorization\"])\n\n    # Step\
    \ B: fetch 10 downstream services in sequence — 8s total\n    data = []\n    for\
    \ svc in DOWNSTREAM_SERVICES:\n        data.append(await fetch_from_service(svc,\
    \ user_id))\n\n    # Step C: compute aggregates from DB — 3s\n    aggregates =\
    \ await db.fetch(\"\"\"\n        SELECT event_type, COUNT(*), AVG(value)\n   \
    \     FROM analytics_events\n        WHERE user_id = $1 AND created_at > now()\
    \ - interval '30 days'\n        GROUP BY event_type\n    \"\"\", user_id)\n\n\
    \    # Step D: merge results — 0.5s\n    result = merge(data, aggregates)\n\n\
    \    # Step E: cache result for 5 minutes — 0.5s\n    await redis.set(f\"dash:{user_id}\"\
    , serialize(result), ex=300)\n\n    return result\n```\n\nDecompose the problem\
    \ into sub-problems. For each sub-problem:\n1. List possible causes (at least\
    \ 3 per sub-problem)\n2. Describe a measurement or experiment that would confirm\
    \ or rule out each cause\n3. Estimate the potential improvement if that cause\
    \ is addressed\n\nAfter decomposition, produce a ranked action plan with estimated\
    \ total impact.\n"
  expected_behaviors:
  - sub-problem
  - latency
  - diagnostic
  judge_criteria:
  - 'Sub-problems include: sequential service calls, DB query performance, cache miss
    penalty, N+1 patterns, serialization overhead'
  - Diagnostic experiments are specific (e.g., 'add trace spans around each downstream
    call to measure per-service latency')
  - Action plan estimates are internally consistent
---
