"""Return eligibility engine."""

from __future__ import annotations

from portal.rule import RuleEngine
from portal.types import ArticleEligibility, Order


def evaluate_eligibility(order: Order) -> list[ArticleEligibility]:
    """Evaluate return eligibility for every article in *order*.

    Returns:
        A list of :class:`ArticleEligibility`, one per article in the order.
    """
    results: list[ArticleEligibility] = []

    rule_engine = RuleEngine()

    for article in order.articles:
        eligibility = rule_engine.evaluate_article(article, order)
        results.append(eligibility)

    return results
