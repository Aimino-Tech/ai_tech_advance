-- Enable WAL mode for concurrent reads during eval writes
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    skills TEXT,
    course TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    total_scenarios INTEGER NOT NULL,
    passed_scenarios INTEGER NOT NULL,
    total_score REAL NOT NULL,
    duration_seconds REAL,
    git_sha TEXT,
    judge_model TEXT
);

CREATE TABLE IF NOT EXISTS scenarios (
    id TEXT PRIMARY KEY,
    course TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    difficulty TEXT DEFAULT 'smoke',
    tags TEXT,
    max_score REAL NOT NULL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS scenario_results (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(id),
    scenario_id TEXT NOT NULL REFERENCES scenarios(id),
    passed INTEGER NOT NULL DEFAULT 0,
    score REAL NOT NULL DEFAULT 0.0,
    output TEXT,
    judge_feedback TEXT,
    duration_seconds REAL,
    error TEXT,
    attempt INTEGER NOT NULL DEFAULT 1,
    UNIQUE(run_id, scenario_id, attempt)
);

CREATE INDEX IF NOT EXISTS idx_results_run ON scenario_results(run_id);
CREATE INDEX IF NOT EXISTS idx_results_scenario ON scenario_results(scenario_id);
