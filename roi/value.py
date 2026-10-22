"""The value side of agent ROI: what the work would have cost without it.

Value here means one narrow, auditable thing -- human handling cost that
no longer has to be spent because the agent did the task, or did most of
it. It is deliberately not revenue, not satisfaction scores, and not
"strategic value": those are real, but they cannot be checked against a
timesheet, and a framework that mixes them in can be made to say
anything.

Two adjustments keep the number honest:

* Containment only counts when the resolution is *correct*. A task the
  agent closed wrongly is not avoided cost; it is a future rework bill,
  so the accuracy factor multiplies every value term. At zero accuracy
  the agent creates no value in this model, however much it "handles".
* Tasks the agent could not fully resolve still help if they shorten
  the human's handling time. That partial value is counted separately,
  at the measured time saving, so it cannot masquerade as full
  containment.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueInputs:
    """Baseline and agent-effect drivers for one use case over one period."""

    volume: int                   # tasks arriving in the period
    baseline_minutes: float       # minutes a human needs per task, unaided
    loaded_hourly_rate: float     # fully loaded cost of that human time
    containment_rate: float       # share of tasks the agent resolves alone
    accuracy: float               # share of agent work that is correct
    assisted_time_saving: float = 0.0  # handling-time cut on the rest

    def __post_init__(self):
        if self.volume < 0:
            raise ValueError("volume must be non-negative, got %r" % self.volume)
        if self.baseline_minutes < 0:
            raise ValueError(
                "baseline_minutes must be non-negative, got %r" % self.baseline_minutes)
        if self.loaded_hourly_rate < 0:
            raise ValueError(
                "loaded_hourly_rate must be non-negative, got %r" % self.loaded_hourly_rate)
        for name in ("containment_rate", "accuracy", "assisted_time_saving"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError("%s must be a fraction in [0, 1], got %r" % (name, value))


@dataclass(frozen=True)
class ValueBreakdown:
    """Where the period's gross value comes from."""

    contained_value: float   # baseline cost avoided on contained tasks
    assisted_value: float    # handling time saved on human-finished tasks

    @property
    def gross(self):
        return self.contained_value + self.assisted_value


def baseline_cost_per_task(inputs):
    """What one task costs when a person does all of it."""
    return inputs.baseline_minutes / 60.0 * inputs.loaded_hourly_rate


def total_baseline_cost(inputs):
    """What the whole period's volume would cost with no agent at all."""
    return inputs.volume * baseline_cost_per_task(inputs)


def contained_tasks(inputs):
    return inputs.volume * inputs.containment_rate


def assisted_tasks(inputs):
    return inputs.volume * (1.0 - inputs.containment_rate)


def correctly_contained(inputs):
    """Contained *and* right -- the only resolutions that avoid real cost."""
    return contained_tasks(inputs) * inputs.accuracy


def value_breakdown(inputs):
    per_task = baseline_cost_per_task(inputs)
    contained = contained_tasks(inputs) * per_task
    assisted = assisted_tasks(inputs) * per_task * inputs.assisted_time_saving
    return ValueBreakdown(
        contained_value=inputs.accuracy * contained,
        assisted_value=inputs.accuracy * assisted,
    )
