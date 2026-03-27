from __future__ import annotations

import json
import logging
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import portal.rule.conditions as _conditions  # noqa: F401 — register built-ins

from portal.rule.registry import ConditionFn, get_registry
from portal.types import Article, ArticleEligibility, Order, RuleEvaluationInput

logger = logging.getLogger(__name__)

RuleDict = dict[str, Any]

_RULES_PATH = Path(__file__).resolve().parent.parent / "data" / "rules.json"
_REQUIRED_RULE_FIELDS = {"id", "description"}


@lru_cache(maxsize=4)
def _load_rules(path: str) -> tuple[RuleDict, ...]:
    """Read, validate, and return the ordered rule list from *path*.

    Results are cached per path so the file is only read once.
    Call ``_load_rules.cache_clear()`` to force a reload.
    """
    with open(path, encoding="utf-8") as fh:
        rules: list[RuleDict] = json.load(fh)
    for i, rule in enumerate(rules):
        missing = _REQUIRED_RULE_FIELDS - rule.keys()
        if missing:
            raise ValueError(
                f"Rule at index {i} missing required fields: {missing}"
            )
        if "condition" not in rule and "conditions" not in rule:
            raise ValueError(
                f"Rule at index {i} must have 'condition' or 'conditions'"
            )
    return tuple(rules)


class RuleEngine:
    """Data-driven deny-list rule engine for return eligibility.

    Parameters
    ----------
    rules_path:
        Path to the JSON rule file.  Defaults to ``rules.json`` shipped
        alongside this module.
    conditions:
        Optional dict mapping condition names to handler functions.
        Defaults to the built-in condition registry.
    """

    def __init__(
        self,
        rules_path: Path = _RULES_PATH,
        conditions: dict[str, ConditionFn] | None = None,
    ) -> None:
        self._rules = _load_rules(str(rules_path))
        self._conditions = conditions or get_registry()

    # -- public API --------------------------------------------------------

    def evaluate_article(
        self,
        article: Article,
        order: Order,
        *,
        now: datetime | None = None,
    ) -> ArticleEligibility:
        """Evaluate *article* against every rule; return on first deny match."""
        for rule in self._rules:
            if self._rule_matches(rule, article, order, now):
                return ArticleEligibility(
                    article=article,
                    returnable=False,
                    reason=rule.get("description", ""),
                    matched_rule=rule.get("id", ""),
                )
        return ArticleEligibility(
            article=article,
            returnable=True,
            reason="",
            matched_rule="",
        )

    def evaluate_all(
        self,
        article: Article,
        order: Order,
        *,
        now: datetime | None = None,
    ) -> list[ArticleEligibility]:
        """Return *all* matching deny rules, not just the first."""
        matches: list[ArticleEligibility] = []
        for rule in self._rules:
            if self._rule_matches(rule, article, order, now):
                matches.append(
                    ArticleEligibility(
                        article=article,
                        returnable=False,
                        reason=rule.get("description", ""),
                        matched_rule=rule.get("id", ""),
                    )
                )
        if not matches:
            return [
                ArticleEligibility(
                    article=article,
                    returnable=True,
                    reason="",
                    matched_rule="",
                )
            ]
        return matches

    # -- internals ---------------------------------------------------------

    def _rule_matches(
        self,
        rule: RuleDict,
        article: Article,
        order: Order,
        now: datetime | None,
    ) -> bool:
        """Evaluate the condition(s) for a single rule.

        Supports both single ``"condition"`` and composed ``"conditions"``
        with an ``"operator"`` (``"all"`` or ``"any"``).  Prefix a condition
        name with ``!`` to negate it.
        """
        condition_names: list[str] = rule.get("conditions") or [rule["condition"]]
        operator: str = rule.get("operator", "all")
        threshold: dict[str, Any] = rule.get("threshold", {})

        results: list[bool] = []
        for name in condition_names:
            negate = name.startswith("!")
            actual_name = name.lstrip("!")

            handler = self._conditions.get(actual_name)
            if handler is None:
                logger.warning(
                    "Unknown condition %r in rule %r — skipped",
                    actual_name,
                    rule.get("id"),
                )
                continue

            inp = RuleEvaluationInput(
                article=article,
                order=order,
                threshold=threshold,
                now=now,
            )
            result = handler(inp)
            results.append(not result if negate else result)

        if not results:
            return False

        return any(results) if operator == "any" else all(results)
