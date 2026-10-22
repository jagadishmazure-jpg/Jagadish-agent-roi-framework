"""The cost side of agent ROI: every dollar an agent actually consumes.

Agent demos usually quote one number -- the model bill. A deployed agent
costs more than that. People still review its escalations, people still
redo its failures by hand, the platform it runs on is not free, and the
money spent building it has to be recovered before anyone can claim a
return. This module keeps those five components separate on purpose:
a single blended figure hides exactly the line item that tends to grow.

All inputs are period totals or per-request telemetry of the kind an
observability pipeline already emits (requests served, average model
spend per request, escalation rate, failure rate). Rates are fractions
of total requests, measured, not modelled -- the scenario layer in
``compute.py`` derives them from containment and accuracy instead.
"""
from dataclasses import dataclass


def _require_non_negative(name, value):
    if value < 0:
        raise ValueError("%s must be non-negative, got %r" % (name, value))


def _require_rate(name, value):
    if not 0.0 <= value <= 1.0:
        raise ValueError("%s must be a fraction in [0, 1], got %r" % (name, value))


@dataclass(frozen=True)
class CostInputs:
    """Measured cost drivers for one agent over one period."""

    requests: int                 # requests the agent handled in the period
    avg_cost_per_request: float   # model/inference dollars per request
    infra_monthly: float          # allocated platform cost per month
    months: int = 1               # length of the period, in months
    escalation_rate: float = 0.0  # share of requests a human had to review
    review_minutes: float = 0.0   # human minutes spent per reviewed request
    loaded_hourly_rate: float = 0.0   # fully loaded cost of reviewer time
    failure_rate: float = 0.0     # share of requests whose work failed
    baseline_cost_per_task: float = 0.0  # what a failed task costs to redo by hand
    build_cost: float = 0.0       # one-time cost of building the agent
    amortize_months: int = 24     # months the build cost is spread across

    def __post_init__(self):
        _require_non_negative("requests", self.requests)
        _require_non_negative("avg_cost_per_request", self.avg_cost_per_request)
        _require_non_negative("infra_monthly", self.infra_monthly)
        _require_non_negative("review_minutes", self.review_minutes)
        _require_non_negative("loaded_hourly_rate", self.loaded_hourly_rate)
        _require_non_negative("baseline_cost_per_task", self.baseline_cost_per_task)
        _require_non_negative("build_cost", self.build_cost)
        _require_rate("escalation_rate", self.escalation_rate)
        _require_rate("failure_rate", self.failure_rate)
        if self.months < 1:
            raise ValueError("months must be at least 1, got %r" % self.months)
        if self.amortize_months < 1:
            raise ValueError(
                "amortize_months must be at least 1, got %r" % self.amortize_months)


@dataclass(frozen=True)
class CostBreakdown:
    """One period of agent cost, component by component."""

    inference: float
    infrastructure: float
    human_review: float
    failure_rework: float
    build_amortized: float
    escalated_requests: float
    failed_tasks: float

    @property
    def total(self):
        return (self.inference + self.infrastructure + self.human_review
                + self.failure_rework + self.build_amortized)


def inference_cost(inputs):
    """Model spend: requests served times the average cost of each."""
    return inputs.requests * inputs.avg_cost_per_request


def infrastructure_cost(inputs):
    """The agent's share of platform, hosting and tooling for the period."""
    return inputs.infra_monthly * inputs.months


def escalated_requests(inputs):
    return inputs.requests * inputs.escalation_rate


def human_review_cost(inputs):
    """Reviewer time is agent cost: the human is finishing the agent's work."""
    reviews = escalated_requests(inputs)
    return reviews * (inputs.review_minutes / 60.0) * inputs.loaded_hourly_rate


def failed_tasks(inputs):
    return inputs.requests * inputs.failure_rate


def failure_rework_cost(inputs):
    """A failed task is done twice: once badly by the agent, once by a person."""
    return failed_tasks(inputs) * inputs.baseline_cost_per_task


def build_amortized_cost(inputs):
    """The period's share of the one-time build cost."""
    return inputs.build_cost / inputs.amortize_months * inputs.months


def cost_breakdown(inputs):
    return CostBreakdown(
        inference=inference_cost(inputs),
        infrastructure=infrastructure_cost(inputs),
        human_review=human_review_cost(inputs),
        failure_rework=failure_rework_cost(inputs),
        build_amortized=build_amortized_cost(inputs),
        escalated_requests=escalated_requests(inputs),
        failed_tasks=failed_tasks(inputs),
    )
