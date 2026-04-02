"""Decorator-based condition registry for the rule engine.

New conditions can live in any module — just decorate with
``@condition("name")`` and ensure the module is imported before the
engine is instantiated.
"""

from __future__ import annotations

from collections.abc import Callable

from portal.types import RuleEvaluationInput

ConditionFn = Callable[[RuleEvaluationInput], bool]

_REGISTRY: dict[str, ConditionFn] = {}


def condition(name: str) -> Callable[[ConditionFn], ConditionFn]:
    """Register a condition handler under *name*."""

    def decorator(fn: ConditionFn) -> ConditionFn:
        if name in _REGISTRY:
            raise ValueError(f"Duplicate condition name: {name!r}")
        _REGISTRY[name] = fn
        return fn

    return decorator


def get_registry() -> dict[str, ConditionFn]:
    """Return a copy of the current condition registry."""
    return dict(_REGISTRY)
