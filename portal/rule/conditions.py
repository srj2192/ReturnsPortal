"""Built-in conditions for the rule engine.

New conditions can be added here or in separate modules — just decorate
with ``@condition("name")`` and ensure the module is imported before the
engine is instantiated.
"""

from __future__ import annotations

from datetime import datetime

from portal.rule.registry import condition
from portal.types import RuleEvaluationInput


@condition("is_digital")
def is_digital(inp: RuleEvaluationInput) -> bool:
    return inp.article.is_digital


@condition("is_final_sale")
def is_final_sale(inp: RuleEvaluationInput) -> bool:
    return inp.article.is_final_sale


@condition("fully_returned")
def fully_returned(inp: RuleEvaluationInput) -> bool:
    return inp.article.quantity_returned >= inp.article.quantity

@condition("past_return_window")
def past_return_window(inp: RuleEvaluationInput) -> bool:
    category = inp.article.category
    category_config = inp.threshold.get(category, inp.threshold.get("default"))

    if category_config:
        allowed_days = int(category_config.get("days"))
        now = inp.now or datetime.now()
        elapsed = (now - inp.order.delivery_date).days
        return elapsed > allowed_days
    return True
