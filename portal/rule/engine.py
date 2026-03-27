from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from portal.types import Article, ArticleEligibility, Order, RuleEvaluationInput

RuleDict = dict[str, Any]

ConditionFn = Callable[[RuleEvaluationInput], bool]

_RULES_PATH = Path(__file__).resolve().parent.parent/ "data" / "rules.json"


def _is_digital(rule_evaluation_input: RuleEvaluationInput) -> bool:
    return rule_evaluation_input.article.is_digital


def _is_final_sale(rule_evaluation_input: RuleEvaluationInput) -> bool:
    return rule_evaluation_input.article.is_final_sale


def _fully_returned(rule_evaluation_input: RuleEvaluationInput) -> bool:
    return (rule_evaluation_input.article.quantity_returned >=
            rule_evaluation_input.article.quantity)


def _past_return_window(rule_evaluation_input: RuleEvaluationInput) -> bool:
    category = rule_evaluation_input.article.category
    if rule_evaluation_input.threshold.get(category):
        allowed_days: int = int(rule_evaluation_input.threshold.get("days", 30))
        elapsed = (datetime.now() - rule_evaluation_input.order.delivery_date).days
        return elapsed > allowed_days
    return True


_DEFAULT_CONDITIONS: dict[str, ConditionFn] = {
    "is_digital": _is_digital,
    "is_final_sale": _is_final_sale,
    "fully_returned": _fully_returned,
    "past_return_window": _past_return_window,
}


class RuleEngine:
    """Data-driven deny-list rule engine for return eligibility.
    Parameters
    ----------
    rules_path:
        Path to the JSON rule file.  Defaults to ``rule.json`` shipped
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
        self._rules = self._load_rules(rules_path)
        self._conditions = conditions or dict(_DEFAULT_CONDITIONS)

    @staticmethod
    def _load_rules(path: Path) -> list[RuleDict]:
        """Read and return the ordered rule list from *path*."""
        with path.open(encoding="utf-8") as fh:
            rules: list[RuleDict] = json.load(fh)
        return rules

    def evaluate_article(self, article: Article, order: Order) -> ArticleEligibility:
        for rule in self._rules:
            condition_name: str = rule["condition"]
            handler = self._conditions.get(condition_name)
            if handler is None:
                continue
            threshold: dict[str, Any] = rule.get("threshold", {})
            rule_evaluation_input: RuleEvaluationInput = RuleEvaluationInput(
                article=article,
                order=order,
                threshold=threshold
            )
            if handler(rule_evaluation_input):
                return ArticleEligibility(
                    article=article,
                    returnable=False,
                    reason=rule.get("description", ""),
                    matched_rule=rule.get("id", condition_name),
                )

        return ArticleEligibility(
            article=article,
            returnable=True,
            reason="",
            matched_rule="",
        )
