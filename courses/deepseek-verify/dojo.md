---
course: deepseek-verify
title: DeepSeek Verification & Testing
description: 10 scenarios testing verification and testing — edge case test design, input/output contracts, property-based tests, boundary analysis, regression test selection, test coverage gap analysis, assertion writing, test fixture setup, mocking external dependencies, test report analysis
difficulty: standard
model: deepseek-v4-flash
scenarios:
  - id: verify-01
    name: "Test edge cases for a date parser"
    description: "Write comprehensive test cases for a date parsing function including edge cases"
    tags: [testing, edge-cases, go]
    prompt: |
      Write a comprehensive set of test cases for this Go function that parses
      date strings in multiple formats:

      ```go
      package dateutil

      import "time"

      // ParseDate parses a date string in multiple formats.
      // Supported formats:
      //   - "2006-01-02" (ISO 8601)
      //   - "02-Jan-2006" (DD-Mon-YYYY)
      //   - "Jan 2, 2006" (Mon DD, YYYY)
      //   - "2006/01/02" (YYYY/MM/DD)
      //   - Unix timestamp (seconds since epoch, e.g. "1700000000")
      //
      // Returns the parsed time in UTC. If the string is empty or unparsable,
      // returns (time.Time{}, error).
      func ParseDate(s string) (time.Time, error) {
          // ... implementation ...
      }
      ```

      Write tests (using Go's testing package, not a table-driven style for
      individual cases, but you may use table-driven for the happy path) covering:

      - All 5 supported formats with valid inputs
      - Unix timestamp edge cases: 0, negative (before epoch), very large (year 2038+)
      - Empty string
      - Whitespace-only string
      - Invalid format (e.g., "not a date")
      - February 29 on leap years and non-leap years
      - Month boundary: Jan 32, Apr 31 (invalid days for month)
      - Two-digit year ambiguity (e.g., "05-06-07")
      - Timezone handling: ensure output is always UTC regardless of input
      - Nil/empty behavior (the function receives a string, so nil isn't possible)

      Each test function must have a descriptive name following Go convention:
      `func TestParseDate_<scenario>(t *testing.T)`

      Also include a helper function `mustParse` that panics on error for use
      in non-test setup code.
    expected_behaviors:
      - TestParseDate_
      - table-driven
      - mustParse
    judge_criteria:
      - "Covers all 5 formats, empty string, invalid, leap year, month overflow"
      - "Unix timestamp tests include negative and year-2038 values"
      - "Tests verify UTC timezone"
      - "mustParse helper panics on error (for test setup only)"

  - id: verify-02
    name: "Validate input/output contracts"
    description: "Add runtime contract validation using Pydantic models"
    tags: [testing, contracts, python]
    prompt: |
      This Python function processes order data but has no type validation.
      Add Pydantic models to validate both input and output contracts.

      ```python
      from dataclasses import dataclass
      from decimal import Decimal
      from datetime import datetime
      from typing import Optional

      # Current code — no validation
      @dataclass
      class OrderInput:
          order_id: str
          user_id: str
          items: list  # list of dicts with product_id, quantity, unit_price
          shipping_address: Optional[dict] = None  # dict with street, city, zip, country
          coupon_code: Optional[str] = None
          notes: Optional[str] = None

      @dataclass
      class OrderOutput:
          order_id: str
          total: Decimal
          discount_applied: Decimal
          final_total: Decimal
          estimated_delivery: datetime
          items: list

      def process_order(order: OrderInput) -> OrderOutput:
          # ... complex business logic ...
          pass
      ```

      Requirements:
      - Replace both dataclasses with Pydantic v2 BaseModel
      - Add proper field validations:
        - order_id: must be non-empty, match pattern "ORD-\d{8}"
        - user_id: must be non-empty
        - items: must have at least 1 item, max 50 items
        - Each item must have: product_id (str, non-empty), quantity (int, 1-999),
          unit_price (Decimal, positive, max 999999.99)
        - shipping_address is required (not Optional) — street, city, zip, country
          all non-empty strings
        - coupon_code: if provided, must be 6-20 alphanumeric characters
      - Add a field validator that checks: if any item has quantity > 10,
        the order must have notes (notes is required in that case)
      - On the output side, ensure total and final_total are always positive
        and have at most 2 decimal places

      Also write a test that demonstrates validation passing and one that
      demonstrates validation failing.
    expected_behaviors:
      - BaseModel
      - field_validator
      - model_validator
    judge_criteria:
      - "Uses Pydantic v2 syntax (field_validator, model_validator, Field)"
      - "Cross-field validator catches quantity>10 without notes"
      - "Decimal fields use condecimal or Field(max_digits=10, decimal_places=2)"

  - id: verify-03
    name: "Property-based tests for a sort function"
    description: "Write property-based tests for a sorting function using Hypothesis"
    tags: [testing, property-based, python]
    prompt: |
      Write property-based tests using the Hypothesis library for a generic
      sort function. The function signature is:

      ```python
      def stable_sort(items: list[T], key: Callable[[T], Any] = None, reverse: bool = False) -> list[T]:
          """Return a new list sorted stably by key. Preserves original list.
          Stable sort: equal elements retain their original relative order.
          """
          # ... implementation ...
      ```

      Properties that must always hold for any valid input:

      1. **Sortedness**: The result is sorted (non-decreasing by default,
         non-increasing if reverse=True)
      2. **Permutation**: The result contains the same elements as the input
         (same multiset)
      3. **Idempotence**: Sorting an already-sorted list returns the same list
      4. **Stability**: If two elements compare equal by key, their relative
         order in the output matches their relative order in the input
      5. **Key function**: The sort uses the key function correctly
      6. **Original preserved**: The input list is not mutated
      7. **Empty/singleton**: Empty list and single-element lists return
         themselves

      Write the test file using Hypothesis `@given` strategies. For each property,
      write a separate test function with a descriptive name and use appropriate
      Hypothesis strategies (lists, integers, tuples, etc.).

      For stability testing, use a custom class or a tuple with a secondary
      index to verify original ordering is preserved for equal-keyed items.
    expected_behaviors:
      - from hypothesis
      - @given
      - st.lists
    judge_criteria:
      - "Each test uses Hypothesis strategy, not hardcoded examples"
      - "Stability test uses an enumerated list and sorts by one field"
      - "Original preservation test asserts input is unchanged after sort"

  - id: verify-04
    name: "Boundary analysis — rate limiter"
    description: "Identify boundary values for a rate limiter and write tests for them"
    tags: [testing, boundaries, typescript]
    prompt: |
      A token bucket rate limiter has this interface:

      ```typescript
      interface RateLimitConfig {
        maxTokens: number;       // Max burst capacity (1-1000)
        refillRate: number;      // Tokens added per second (0.1-100)
        refillInterval: number;  // How often tokens refill in ms (100-60000)
      }

      class TokenBucketRateLimiter {
        constructor(config: RateLimitConfig) {}

        // Consume tokens. Returns true if allowed, false if rate limited.
        // cost: number of tokens to consume (default: 1, max: maxTokens)
        consume(cost?: number): boolean { ... }

        // Get current token count (for testing/inspection)
        getTokens(): number { ... }

        // Reset to full tokens
        reset(): void { ... }
      }
      ```

      Perform a boundary analysis. For each parameter, identify:
      1. Valid equivalence partitions and their boundaries
      2. Invalid partitions and their boundaries
      3. Combination hazards (when two parameters at their extremes interact)

      Then write TypeScript tests (using Vitest or Jest) targeting these boundaries:
      - maxTokens at 1, 500, 1000 and 0 (invalid), 1001 (invalid)
      - refillRate at 0.1, 1, 100 and 0 (invalid), 101 (invalid)
      - refillInterval at 100, 30000, 60000 and 99 (invalid), 60001 (invalid)
      - Consume cost = 0, 1, maxTokens, maxTokens+1
      - Consume exactly refillRate tokens after refillInterval
      - Consume more tokens than available (should fail)
      - Consume tokens, wait partial interval, try again (should fail)
      - Consume, wait full interval, try again (should succeed)

      Use `vi.useFakeTimers()` for time-based testing.
    expected_behaviors:
      - maxTokens
      - refillRate
      - useFakeTimers
    judge_criteria:
      - "Boundary values correctly identified (maxTokens=0 invalid, maxTokens=1001 invalid)"
      - "Tests use vi.advanceTimersByTime for precise time control"
      - "Partial interval test verifies rate limiting works correctly"
      - "Combination test: low refillRate + high maxTokens still limits correctly"

  - id: verify-05
    name: "Regression test selection"
    description: "Given a change set, determine which tests must be re-run"
    tags: [testing, regression, typescript]
    prompt: |
      A monorepo has this structure:

      ```
      packages/
        shared/       # Shared types and utilities
          src/validation.ts
          src/formatting.ts
          src/types.ts    # exported by dozens of packages
        auth/         # Authentication service
          src/login.ts
          src/session.ts
          src/middleware.ts
        orders/       # Order processing
          src/handler.ts
          src/pricing.ts     # imports from shared/validation, shared/formatting
          src/inventory.ts   # imports from shared/types
        payments/     # Payment processing
          src/charge.ts
          src/refund.ts      # imports from shared/validation
        notifications/
          src/email.ts
      ```

      Given each of the following change sets, determine which packages need
      to be re-tested and why. Use the dependency graph — a change to a package
      can break anything that depends on it (directly or transitively).

      Change A: `packages/shared/src/types.ts` — the `User` interface gains a
      new optional field `phone: string`

      Change B: `packages/shared/src/validation.ts` — the `validateEmail`
      function now rejects plus addressing (name+tag@example.com)

      Change C: `packages/orders/src/pricing.ts` — the `calculateDiscount`
      function now requires a minimum order value of $10 (was $5)

      Change D: `packages/auth/src/login.ts` — the session token TTL changes
      from 24h to 1h

      For each change:
      1. List all packages that must be re-tested (including the changed one)
      2. Explain the dependency path (X → Y → Z)
      3. Identify which specific test suites are most likely to break
      4. Note any tests that are likely unnecessary
    expected_behaviors:
      - dependency graph
      - transitive
      - re-tested
    judge_criteria:
      - "Change A: shared/types → all packages must retest (types are foundational)"
      - "Change B: shared/validation → orders/pricing and payments/refund"
      - "Change C: orders/pricing → only orders package (no one depends on orders)"
      - "Change D: auth/login → auth package only (unless others import login function)"

  - id: verify-06
    name: "Test coverage gap analysis"
    description: "Analyze a codebase for test coverage gaps using line coverage data"
    tags: [testing, coverage, python]
    prompt: |
      Given this coverage report (simplified), identify all test coverage gaps.
      For each gap, propose what test(s) should be added.

      ```python
      # coverage_report.txt
      # Lines executed: 72.3%
      # Branches executed: 58.1%

      src/payment/gateway.py:
        process_payment():      85% — missing lines 45-50, 120-125
        refund():               92% — missing lines 200-205
        validate_card():        40% — only tested with Visa, missing lines 310-350
        retry_failed():         0%  — completely untested

      src/orders/discount.py:
        apply_discount():       90%  — missing lines 80-85 (edge case: zero quantity)
        calculate_tier():       100% — fully covered

      src/notifications/email.py:
        send_email():           60%  — missing lines 30-50 (SMTP connection errors)
        render_template():      75%  — missing non-existent template error path
        batch_send():           0%   — completely untested

      src/auth/session.py:
        create_session():       100% — fully covered
        validate_session():     70%  — missing expired session, revoked session paths
        revoke_session():       100% — fully covered
      ```

      For each gap:
      1. Which function/method has the gap
      2. What specific scenario is untested
      3. What test case would cover it (describe the arrange/act/assert)
      4. Priority (high/medium/low) — based on risk:
         - Untested payment logic = high
         - Untested error path for notifications = medium
         - Missing edge case in discount = low

      Then calculate the overall risk score and produce a ranked action plan
      with estimated effort (in test cases) per item.
    expected_behaviors:
      - coverage gaps
      - untested
      - risk
    judge_criteria:
      - "Identifies validate_card() is only tested with Visa (missing MC, Amex, Discover)"
      - "Prioritizes retry_failed() and batch_send() as high (completely untested)"
      - "Expired and revoked session paths identified as medium"
      - "Zero quantity discount edge case identified as low"

  - id: verify-07
    name: "Assertion writing — database state verification"
    description: "Write assertions that verify complex database state after operations"
    tags: [testing, assertions, sql]
    prompt: |
      An order processing system has this schema:

      ```sql
      CREATE TABLE orders (
          id          SERIAL PRIMARY KEY,
          user_id     INTEGER NOT NULL REFERENCES users(id),
          status      TEXT NOT NULL DEFAULT 'pending',
          total       DECIMAL(10,2) NOT NULL,
          created_at  TIMESTAMP DEFAULT now()
      );

      CREATE TABLE order_items (
          id          SERIAL PRIMARY KEY,
          order_id    INTEGER NOT NULL REFERENCES orders(id),
          product_id  INTEGER NOT NULL,
          quantity    INTEGER NOT NULL CHECK (quantity > 0),
          unit_price  DECIMAL(10,2) NOT NULL,
          line_total  DECIMAL(10,2) NOT NULL
      );

      CREATE TABLE payments (
          id          SERIAL PRIMARY KEY,
          order_id    INTEGER NOT NULL REFERENCES orders(id),
          amount      DECIMAL(10,2) NOT NULL,
          status      TEXT NOT NULL DEFAULT 'pending',
          paid_at     TIMESTAMP,
          error_msg   TEXT
      );

      CREATE TABLE inventory_reservations (
          id          SERIAL PRIMARY KEY,
          order_id    INTEGER NOT NULL REFERENCES orders(id),
          product_id  INTEGER NOT NULL,
          quantity    INTEGER NOT NULL,
          status      TEXT NOT NULL DEFAULT 'reserved'
      );
      ```

      Write test assertions (in Python with psycopg2 and pytest) that verify
      the database state after a `place_order` operation. The operation is:

      ```python
      def place_order(conn, user_id: int, items: list[dict]) -> int:
          """Creates order, inserts items, charges payment, reserves inventory.
          Returns order_id on success. Raises on failure (rolls back).
          """
          ...
      ```

      Write assertions for a successful order:
      1. Exactly one order row is created with the correct user_id, total, status='confirmed'
      2. Exactly N order_item rows match the input items (quantity, unit_price, line_total)
      3. Total of order_items.line_total equals order.total
      4. A payment row exists with amount = order.total and status = 'completed'
      5. inventory_reservations rows exist for each product with status = 'reserved'
      6. Timestamps are within 5 seconds of the test execution time

      Also write assertions for a failed order (e.g., insufficient funds):
      1. No order row is created (transaction rolled back)
      2. No payment rows are created
      3. No inventory_reservations rows are created

      Use pytest fixtures for the database connection. The assertions should
      be clear enough that a failing assertion tells you exactly what went wrong.
    expected_behaviors:
      - place_order
      - assert
      - SELECT
    judge_criteria:
      - "Assertions query the database (not mock objects)"
      - "line_total and order.total cross-table check"
      - "Timestamp check allows reasonable clock skew (5s)"
      - "Failed order assertions verify complete rollback (all tables unchanged)"

  - id: verify-08
    name: "Test fixture setup — realistic data factory"
    description: "Design a test fixture factory for a complex domain model"
    tags: [testing, fixtures, typescript]
    prompt: |
      Design a test fixture factory (using a builder pattern) for this domain:

      ```typescript
      interface Organization {
        id: string;
        name: string;
        plan: "free" | "pro" | "enterprise";
        billingEmail: string;
        created_at: Date;
        settings: {
          maxUsers: number;
          maxProjects: number;
          allowedAuthProviders: string[];
          featureFlags: Record<string, boolean>;
        };
      }

      interface User {
        id: string;
        email: string;
        name: string;
        role: "admin" | "member" | "viewer";
        organizationId: string;
        isActive: boolean;
        lastLogin: Date | null;
        preferences: {
          theme: "light" | "dark";
          notifications: boolean;
          timezone: string;
        };
      }

      interface Project {
        id: string;
        name: string;
        organizationId: string;
        ownerUserId: string;
        status: "active" | "archived" | "deleted";
        created_at: Date;
        memberIds: string[];
      }

      interface Task {
        id: string;
        projectId: string;
        title: string;
        assigneeId: string | null;
        status: "todo" | "in_progress" | "review" | "done";
        priority: 0 | 1 | 2 | 3;
        dueDate: Date | null;
        tags: string[];
        estimatedHours: number | null;
      }
      ```

      Write a fixture builder that:
      - Has a default factory function per entity (with sensible defaults)
      - Uses a builder pattern for customization
      - Handles cross-entity references automatically
        (e.g., creating a User also references an Organization)
      - Supports creating "linked" entities (e.g., create Org → User → Project → Task)
      - Generates unique IDs automatically (uuid)
      - Allows overriding any field

      Example API:
      ```typescript
      const org = await fixture.create.org({ plan: "pro" });
      const user = await fixture.create.user({ orgId: org.id, role: "admin" });
      const project = await fixture.create.project({ orgId: org.id, ownerUserId: user.id });
      const tasks = await fixture.create.many.task(3, { projectId: project.id });
      ```

      Write the implementation in TypeScript. Use a class `TestFixture` with
      methods for each entity. Each method returns the created entity and
      optionally auto-creates dependent entities.
    expected_behaviors:
      - TestFixture
      - fixture.create
      - sensible defaults
    judge_criteria:
      - "Fixture.create.org() works without arguments (sensible defaults)"
      - "Fixture.create.user() auto-creates an org if orgId not provided"
      - "Fixture.create.many.task(3, ...) creates 3 tasks"
      - "Overrides merge with defaults (shallow merge at minimum)"

  - id: verify-09
    name: "Mocking external dependencies"
    description: "Write tests for a service that depends on external APIs using mocks"
    tags: [testing, mocking, go]
    prompt: |
      This Go service fetches weather data from an external API and caches it.
      Write tests using interfaces and mocks to test the service without
      hitting the real API.

      ```go
      package weather

      import (
          "context"
          "encoding/json"
          "fmt"
          "net/http"
          "time"
      )

      type WeatherData struct {
          City        string    `json:"city"`
          Temperature float64   `json:"temperature"`
          Humidity    int       `json:"humidity"`
          Description string    `json:"description"`
          RetrievedAt time.Time `json:"retrieved_at"`
      }

      type WeatherAPIClient interface {
          FetchWeather(ctx context.Context, city string) (*WeatherData, error)
      }

      type Cache interface {
          Get(key string) (interface{}, bool)
          Set(key string, value interface{}, ttl time.Duration)
      }

      type WeatherService struct {
          apiClient WeatherAPIClient
          cache     Cache
          cacheTTL  time.Duration
      }

      func NewWeatherService(apiClient WeatherAPIClient, cache Cache, cacheTTL time.Duration) *WeatherService {
          return &WeatherService{
              apiClient: apiClient,
              cache:     cache,
              cacheTTL:  cacheTTL,
          }
      }

      func (s *WeatherService) GetWeather(ctx context.Context, city string) (*WeatherData, error) {
          // 1. Check cache
          if cached, ok := s.cache.Get(city); ok {
              return cached.(*WeatherData), nil
          }

          // 2. Fetch from API
          data, err := s.apiClient.FetchWeather(ctx, city)
          if err != nil {
              return nil, fmt.Errorf("api fetch failed: %w", err)
          }

          // 3. Cache the result
          s.cache.Set(city, data, s.cacheTTL)

          return data, nil
      }
      ```

      Write Go tests (testing package) with:
      1. A mock implementation of WeatherAPIClient using a struct (not a mocking library)
      2. A mock implementation of Cache
      3. Tests for:
         - Cache hit returns cached data without calling API
         - Cache miss calls API and caches result
         - API error is propagated correctly
         - Context cancellation is respected
         - Type assertion failure in cache is handled gracefully

      Also write a test that verifies the integration test approach: instead of
      mocking, create a test HTTP server that returns fake weather data and test
      against that (for the real HTTP client implementation).
    expected_behaviors:
      - WeatherAPIClient
      - httptest
      - mock
    judge_criteria:
      - "Mock WeatherAPIClient records whether FetchWeather was called"
      - "Cache hit test asserts FetchWeather was NOT called"
      - "HTTPTest server integration test does NOT mock the client interface"
      - "Context cancellation test uses a canceled context and expects an error"

  - id: verify-10
    name: "Test report analysis"
    description: "Analyze a flaky test report and determine the root cause"
    tags: [testing, flaky-tests, analysis]
    prompt: |
      A CI pipeline has a test that passes 70% of the time and fails 30% of
      the time, always on the same assertion. Here's the failing test output:

      ```
      FAILED test_ordering.py::test_concurrent_checkout

      test_ordering.py:215: in test_concurrent_checkout
          assert final_stock[product_a] == initial_stock - 2
      E       assert 48 == (50 - 2)
      E         +48
      E         -48
      E       Expected: 48
      E       Actual  : 49
      ```

      The test:

      ```python
      def test_concurrent_checkout():
          """Two users should be able to check out simultaneously
          without overselling inventory."""
          product_a = create_product(stock=50)

          # Simulate two concurrent checkouts
          results = []
          with ThreadPoolExecutor(max_workers=2) as executor:
              f1 = executor.submit(checkout, user1, [product_a])
              f2 = executor.submit(checkout, user2, [product_a])
              results = [f1.result(), f2.result()]

          # Both should succeed (stock = 50, each buys 1)
          assert all(results), "Both checkouts should succeed"

          # Verify final stock
          conn = get_db_connection()
          final_stock = get_stock(conn, product_a)
          conn.close()
          assert final_stock == initial_stock - 2
      ```

      The stock decrement logic:

      ```python
      def decrement_stock(conn, product_id: int, quantity: int) -> bool:
          """Decrement stock if sufficient quantity available.
          Returns True if successful, False if insufficient stock."""
          cur = conn.cursor()
          cur.execute(
              "UPDATE products SET stock = stock - %s "
              "WHERE id = %s AND stock >= %s",
              (quantity, product_id, quantity)
          )
          return cur.rowcount > 0
      ```

      Analyze the test failure. Determine:
      1. Why does the test fail 30% of the time?
      2. Is the bug in the test or in the production code?
      3. Is the stock decrement logic correct for concurrent access?
      4. What type of isolation level is needed to prevent this?
      5. Write a fixed version of the test AND the production logic

      Hint: The decrement_stock function looks correct (atomic UPDATE with
      stock >= quantity check). The issue is that the test reads `final_stock`
      in a separate connection with default READ COMMITTED isolation, while
      the concurrent transactions may not have committed yet. But that would
      give 50, not 49.

      Actually, think again: if both transactions succeed, the stock goes
      50 → 49 → 48. The assertion expects 48 but gets 49. This means only
      one decrement was applied. But both checkouts returned True (the assert
      `all(results)` passed). How is that possible?

      The answer: default PostgreSQL READ COMMITTED isolation. Two concurrent
      transactions both read stock=50, both see stock >= 1, and both update.
      The first UPDATE locks the row, the second waits. After the first commits,
      the second UPDATE executes but re-evaluates the WHERE clause with the new
      stock value (49). Since 49 >= 1, the second UPDATE also succeeds.
      Stock is now 49. Both checkouts returned True. But stock decremented by
      1 instead of 2. This is the classic "lost update" in READ COMMITTED.

      The fix: use `SELECT ... FOR UPDATE` or SERIALIZABLE isolation level.
      Write both the test fix and the production code fix.
    expected_behaviors:
      - lost update
      - READ COMMITTED
      - SELECT FOR UPDATE
    judge_criteria:
      - "Root cause: READ COMMITTED allows both txns to see stock=50"
      - "Fix uses SELECT stock FROM products WHERE id=X FOR UPDATE before decrement"
      - "Or: uses SERIALIZABLE isolation with retry on serialization failure"
      - "Test fix uses a single connection or explicit transaction control"
---
