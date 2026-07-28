"""Pydantic v2 models for benchmark scenarios and results."""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class Scenario(BaseModel):
    """A single evaluation scenario with prompt, expected behaviors, and judge criteria."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    description: str
    difficulty: str = "smoke"
    tags: list[str] = []
    max_score: float = 1.0
    prompt: str
    expected_behaviors: list[str] = []
    judge_criteria: list[str] = []


class ScenarioResult(BaseModel):
    """Result of evaluating a single scenario."""

    model_config = ConfigDict(frozen=True)

    scenario_id: str
    passed: bool
    score: float
    output: str
    judge_feedback: str
    error: Optional[str] = None
    attempt: int = 1


class RunResult(BaseModel):
    """Complete result of a model evaluation run."""

    model_config = ConfigDict(frozen=True)

    id: str
    model: str
    skills: list[str]
    course: str
    created_at: str
    total_scenarios: int
    passed_scenarios: int
    total_score: float
    results: list[ScenarioResult]
