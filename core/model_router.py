"""Deterministic model selection policy for XIL-AC.

This module selects a configured model identifier; it does not call a provider,
load model weights, or execute tools. Actual inference belongs in a separately
reviewed adapter layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

TaskType = Literal["general", "reasoning", "coding", "research", "privacy_sensitive"]


class ModelRouteUnavailable(RuntimeError):
    """Raised when no safe model route is configured."""


@dataclass(frozen=True, slots=True)
class ModelRoute:
    task: TaskType
    model_id: str
    local_only: bool
    rationale: str


class ModelRouter:
    """Selects an allowlisted model route without making network requests."""

    _ENV_KEYS: dict[TaskType, str] = {
        "general": "general",
        "reasoning": "reasoning",
        "coding": "coding",
        "research": "research",
        "privacy_sensitive": "local",
    }

    _RATIONALES: dict[TaskType, str] = {
        "general": "balanced general-purpose response",
        "reasoning": "multi-step analysis and structured reasoning",
        "coding": "code generation, review, and test support",
        "research": "source-grounded research synthesis",
        "privacy_sensitive": "local-only processing for sensitive material",
    }

    def __init__(self, configured_models: Mapping[str, str] | None = None) -> None:
        self._models = {
            key: value.strip()
            for key, value in (configured_models or {}).items()
            if isinstance(value, str) and value.strip()
        }

    def route(self, task: TaskType) -> ModelRoute:
        if task not in self._ENV_KEYS:
            raise ModelRouteUnavailable("unsupported_task")

        key = self._ENV_KEYS[task]
        model_id = self._models.get(key)
        if not model_id:
            raise ModelRouteUnavailable(f"model_route_not_configured:{key}")

        local_only = task == "privacy_sensitive"
        if local_only and not model_id.startswith("local/"):
            raise ModelRouteUnavailable("privacy_route_must_be_local")

        return ModelRoute(
            task=task,
            model_id=model_id,
            local_only=local_only,
            rationale=self._RATIONALES[task],
        )
