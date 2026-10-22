"""Intake scoring: rank candidate use cases before anyone builds them.

The cheapest ROI decision is the one made at intake. This gate scores a
candidate on the drivers that decide its economics -- how much work
arrives, how long that work takes a person today, how much of it an
agent could plausibly contain, whether the underlying data is ready to
be retrieved, and how much risk a wrong answer carries -- and returns a
ranked shortlist with the reasons attached.

One verdict is deliberately blunt. A candidate with low volume and high
build complexity is marked ``poor`` no matter how elegant the demo
looks: there is not enough repeated work for the savings to repay the
engineering. Marking it early is the gate doing its job.
"""
from dataclasses import dataclass, field

# Reference points the scores are normalised against. They are judgement
# calls, stated here so they can be argued with and changed in one place.
FULL_VOLUME = 20000        # monthly requests that count as "high volume"
FULL_MINUTES = 20.0        # unaided handling minutes that count as "long"
POOR_VOLUME_CEILING = 3000  # at or below this, volume alone cannot pay
HIGH_COMPLEXITY = 0.7       # build complexity at or above this is "high"

W_VOLUME = 0.30
W_MINUTES = 0.20
W_CONTAINMENT = 0.25
W_READINESS = 0.15
W_RISK = 0.10


@dataclass(frozen=True)
class Candidate:
    """A proposed agent use case, described by intake estimates."""

    name: str
    monthly_volume: int
    baseline_minutes: float        # unaided human minutes per task
    containment_plausibility: float  # share an agent could plausibly resolve
    data_readiness: float          # 0 = scattered, 1 = clean and retrievable
    risk: float                    # 0 = harmless if wrong, 1 = severe harm
    complexity: float              # 0 = trivial build, 1 = major programme

    def __post_init__(self):
        if self.monthly_volume < 0:
            raise ValueError(
                "monthly_volume must be non-negative, got %r" % self.monthly_volume)
        if self.baseline_minutes < 0:
            raise ValueError(
                "baseline_minutes must be non-negative, got %r" % self.baseline_minutes)
        for name in ("containment_plausibility", "data_readiness", "risk", "complexity"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError("%s must be a fraction in [0, 1], got %r" % (name, value))


@dataclass(frozen=True)
class ScoredCandidate:
    candidate: Candidate
    score: float        # 0-100
    verdict: str        # "strong", "viable", "weak" or "poor"
    poor: bool          # low volume + high complexity, called out explicitly
    reasons: list = field(default_factory=list)


def _volume_score(candidate):
    return min(1.0, candidate.monthly_volume / FULL_VOLUME)


def _minutes_score(candidate):
    return min(1.0, candidate.baseline_minutes / FULL_MINUTES)


def is_poor(candidate):
    """Low repeated volume plus a hard build: the economics cannot work."""
    return candidate.monthly_volume <= POOR_VOLUME_CEILING and candidate.complexity >= HIGH_COMPLEXITY


def score_candidate(candidate):
    score = 100.0 * (
        W_VOLUME * _volume_score(candidate)
        + W_MINUTES * _minutes_score(candidate)
        + W_CONTAINMENT * candidate.containment_plausibility
        + W_READINESS * candidate.data_readiness
        + W_RISK * (1.0 - candidate.risk)
    )
    poor = is_poor(candidate)
    if poor:
        verdict = "poor"
    elif score >= 65:
        verdict = "strong"
    elif score >= 40:
        verdict = "viable"
    else:
        verdict = "weak"

    reasons = []
    if candidate.monthly_volume >= FULL_VOLUME:
        reasons.append("volume is high enough for savings to compound monthly")
    elif candidate.monthly_volume <= POOR_VOLUME_CEILING:
        reasons.append("monthly volume is low, so total savings stay small")
    if candidate.baseline_minutes >= FULL_MINUTES:
        reasons.append("unaided handling is slow, so each contained task saves real time")
    elif candidate.baseline_minutes <= 5:
        reasons.append("unaided handling is already quick, limiting the saving per task")
    if candidate.containment_plausibility >= 0.6:
        reasons.append("a large share of the work looks containable by an agent")
    elif candidate.containment_plausibility <= 0.3:
        reasons.append("only a small share of the work looks containable")
    if candidate.data_readiness <= 0.3:
        reasons.append("the underlying data is not ready to retrieve reliably")
    if candidate.risk >= 0.7:
        reasons.append("a wrong answer carries serious risk, raising review costs")
    if poor:
        reasons.append(
            "marked poor: low volume paired with high build complexity rarely repays the build")
    if not reasons:
        reasons.append("no single dominant factor; a mid-range case on every driver")
    return ScoredCandidate(
        candidate=candidate, score=score, verdict=verdict, poor=poor, reasons=reasons)


def rank_candidates(candidates):
    """Score every candidate and rank best first (stable for ties)."""
    scored = [score_candidate(c) for c in candidates]
    return sorted(scored, key=lambda s: -s.score)
