"""Agent ROI framework: what an agent earns versus what it costs."""

from .compute import (
    PortfolioResult,
    SensitivityResult,
    UseCase,
    UseCaseResult,
    breakeven_containment,
    evaluate,
    payback_months,
    rollup,
    sensitivity,
)
from .costs import CostBreakdown, CostInputs, cost_breakdown
from .intake import Candidate, ScoredCandidate, rank_candidates, score_candidate
from .value import ValueBreakdown, ValueInputs, value_breakdown

__all__ = [
    "Candidate",
    "CostBreakdown",
    "CostInputs",
    "PortfolioResult",
    "ScoredCandidate",
    "SensitivityResult",
    "UseCase",
    "UseCaseResult",
    "ValueBreakdown",
    "ValueInputs",
    "breakeven_containment",
    "cost_breakdown",
    "evaluate",
    "payback_months",
    "rank_candidates",
    "rollup",
    "score_candidate",
    "sensitivity",
    "value_breakdown",
]
