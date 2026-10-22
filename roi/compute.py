"""Joining cost and value: net value, ROI, payback, break-even, sensitivity.

A ``UseCase`` is described by its underlying drivers (volume, handling
time, containment, accuracy, rates) rather than by pre-aggregated cost
rates. That is what makes scenario analysis honest: when containment
moves, the escalation load and the failure load move with it, because

* escalations are drawn from the tasks the agent did *not* contain
  (``escalation_share`` of the uncontained remainder gets human review);
* failures are the contained tasks that turned out wrong
  (containment x (1 - accuracy) of all requests), redone at baseline cost.

``costs.py`` works from measured rates directly; this module derives
those rates from the drivers so a what-if question never mixes a new
containment assumption with last month's escalation bill.
"""
from dataclasses import dataclass, replace

from .costs import CostInputs, cost_breakdown
from .value import ValueInputs, baseline_cost_per_task, correctly_contained, value_breakdown


@dataclass(frozen=True)
class UseCase:
    """One agent use case, described by drivers over a period."""

    name: str
    volume: int                   # tasks arriving in the period
    baseline_minutes: float       # unaided human minutes per task
    loaded_hourly_rate: float     # fully loaded cost of human time
    containment_rate: float       # share of tasks the agent resolves alone
    accuracy: float               # share of agent work that is correct
    assisted_time_saving: float   # handling-time cut on uncontained tasks
    avg_cost_per_request: float   # model/inference dollars per request
    infra_monthly: float          # allocated platform cost per month
    review_minutes: float         # human minutes per reviewed escalation
    escalation_share: float       # share of uncontained tasks a human reviews
    build_cost: float             # one-time build cost
    months: int = 1               # period length, months
    amortize_months: int = 24     # months the build cost is spread across

    def __post_init__(self):
        # Build the two sub-models once; their validation covers the drivers.
        self.value_inputs()
        self.cost_inputs()

    def value_inputs(self):
        return ValueInputs(
            volume=self.volume,
            baseline_minutes=self.baseline_minutes,
            loaded_hourly_rate=self.loaded_hourly_rate,
            containment_rate=self.containment_rate,
            accuracy=self.accuracy,
            assisted_time_saving=self.assisted_time_saving,
        )

    def cost_inputs(self):
        return CostInputs(
            requests=self.volume,
            avg_cost_per_request=self.avg_cost_per_request,
            infra_monthly=self.infra_monthly,
            months=self.months,
            escalation_rate=(1.0 - self.containment_rate) * self.escalation_share,
            review_minutes=self.review_minutes,
            loaded_hourly_rate=self.loaded_hourly_rate,
            failure_rate=self.containment_rate * (1.0 - self.accuracy),
            baseline_cost_per_task=baseline_cost_per_task(self.value_inputs()),
            build_cost=self.build_cost,
            amortize_months=self.amortize_months,
        )

    def with_changes(self, **changes):
        return replace(self, **changes)


@dataclass(frozen=True)
class UseCaseResult:
    name: str
    gross_value: float
    total_cost: float
    net_value: float
    roi_pct: float                  # None when the period cost is zero
    cost_per_correct_resolution: float  # None when nothing was correctly contained
    human_cost_per_task: float
    payback_months: float           # None when the agent never pays back
    breakeven_containment: float    # None when even 100% containment loses money


def _net(use_case):
    costs = cost_breakdown(use_case.cost_inputs())
    value = value_breakdown(use_case.value_inputs())
    return value.gross - costs.total


def payback_months(use_case, net_value):
    """Months of net value needed to recover the build cost.

    Zero build cost pays back immediately. A use case whose monthly net
    is zero or negative never pays back, and this returns ``None`` for
    that case rather than a comforting large number.
    """
    if use_case.build_cost <= 0:
        return 0.0
    monthly_net = net_value / use_case.months
    if monthly_net <= 0:
        return None
    return use_case.build_cost / monthly_net


def breakeven_containment(use_case):
    """The containment rate at which net value crosses zero, if it does.

    Holds every other driver fixed and scans containment from 0 to 1,
    then bisects the first upward crossing. Returns 0.0 when the use
    case is already at or above break-even with no containment at all,
    and ``None`` when even perfect containment cannot cover the costs.
    """
    def net_at(rate):
        return _net(use_case.with_changes(containment_rate=rate))

    if net_at(0.0) >= 0:
        return 0.0
    if net_at(1.0) < 0:
        return None
    lo, hi = 0.0, 1.0
    step = 0.001
    prev = 0.0
    bracket = None
    rate = step
    while rate <= 1.0:
        if net_at(rate) >= 0:
            bracket = (prev, rate)
            break
        prev = rate
        rate += step
    if bracket is None:
        return None
    lo, hi = bracket
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if net_at(mid) >= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


def evaluate(use_case):
    """Full ROI picture for one use case over its period."""
    costs = cost_breakdown(use_case.cost_inputs())
    value = value_breakdown(use_case.value_inputs())
    net = value.gross - costs.total
    correct = correctly_contained(use_case.value_inputs())
    return UseCaseResult(
        name=use_case.name,
        gross_value=value.gross,
        total_cost=costs.total,
        net_value=net,
        roi_pct=(net / costs.total * 100.0) if costs.total > 0 else None,
        cost_per_correct_resolution=(costs.total / correct) if correct > 0 else None,
        human_cost_per_task=baseline_cost_per_task(use_case.value_inputs()),
        payback_months=payback_months(use_case, net),
        breakeven_containment=breakeven_containment(use_case),
    )


@dataclass(frozen=True)
class SensitivityResult:
    """Net value under pessimistic, expected and optimistic assumptions."""

    low_net: float
    base_net: float
    high_net: float
    fragile: bool   # True when the plausible range straddles zero


def _clamp01(value):
    return max(0.0, min(1.0, value))


def sensitivity(use_case):
    """Vary the three drivers teams estimate worst: containment, accuracy, pay.

    Low case: containment and accuracy each drop, and the loaded rate
    falls 20% (cheaper human time makes the agent worth less). High case
    mirrors it. A use case is *fragile* when those plausible swings do
    not all land on the same side of zero -- its business case depends on
    the optimistic reading being the true one.
    """
    low = use_case.with_changes(
        containment_rate=_clamp01(use_case.containment_rate - 0.10),
        accuracy=_clamp01(use_case.accuracy - 0.05),
        loaded_hourly_rate=use_case.loaded_hourly_rate * 0.8,
    )
    high = use_case.with_changes(
        containment_rate=_clamp01(use_case.containment_rate + 0.10),
        accuracy=_clamp01(use_case.accuracy + 0.05),
        loaded_hourly_rate=use_case.loaded_hourly_rate * 1.2,
    )
    nets = (_net(low), _net(use_case), _net(high))
    signs = {1 if n > 0 else -1 for n in nets if n != 0}
    fragile = len(signs) > 1 or nets[1] == 0
    return SensitivityResult(
        low_net=nets[0], base_net=nets[1], high_net=nets[2], fragile=fragile)


@dataclass(frozen=True)
class PortfolioResult:
    gross_value: float
    total_cost: float
    net_value: float
    roi_pct: float        # None when the portfolio cost is zero
    total_build_cost: float
    payback_months: float  # None when the portfolio never pays back


def rollup(use_cases):
    """Portfolio totals: sums first, ratios from the sums (never averaged)."""
    results = [evaluate(uc) for uc in use_cases]
    gross = sum(r.gross_value for r in results)
    cost = sum(r.total_cost for r in results)
    net = sum(r.net_value for r in results)
    build = sum(uc.build_cost for uc in use_cases)
    months = use_cases[0].months if use_cases else 1
    monthly_net = net / months if months else 0.0
    if build <= 0:
        payback = 0.0
    elif monthly_net <= 0:
        payback = None
    else:
        payback = build / monthly_net
    return PortfolioResult(
        gross_value=gross,
        total_cost=cost,
        net_value=net,
        roi_pct=(net / cost * 100.0) if cost > 0 else None,
        total_build_cost=build,
        payback_months=payback,
    )
