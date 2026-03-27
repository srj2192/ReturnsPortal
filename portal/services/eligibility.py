"""Return eligibility engine."""

from __future__ import annotations

from portal.rule import RuleEngine
from portal.types import ArticleEligibility, Order

_engine = RuleEngine()


def evaluate_eligibility(order: Order) -> list[ArticleEligibility]:
    """Evaluate return eligibility for every article in *order*.

    Returns:
        A list of :class:`ArticleEligibility`, one per article in the order.
    """
    return [_engine.evaluate_article(article, order) for article in order.articles]
