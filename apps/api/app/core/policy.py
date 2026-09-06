from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PolicyDecision:
    decision: str
    reason: str | None = None


def evaluate_policy(*, purpose: str, attributes: list[str], consent_approved: bool) -> PolicyDecision:
    if not consent_approved:
        return PolicyDecision(decision='DENY', reason='CONSENT_REQUIRED')
    allowed = set(attributes)
    requested = {'income.status', 'scholarship_eligibility'}
    if allowed.issubset(requested):
        return PolicyDecision(decision='ALLOW', reason='policy-allow')
    return PolicyDecision(decision='DENY', reason='POLICY_DENIED')
