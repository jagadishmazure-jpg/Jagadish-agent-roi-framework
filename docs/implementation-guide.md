# Implementation guide: running this framework on a real programme

## 1. Assemble the inputs, per use case

Each driver has a natural source. If a number cannot be sourced, that
is a finding in itself — the programme is flying blind there.

| Driver | Where it should come from |
| --- | --- |
| Volume | Ticket / conversation counts for the period |
| Baseline minutes | Time study or handle-time reports from before the agent, per task type |
| Loaded hourly rate | Finance's fully loaded figure (salary + overheads), not the wage alone |
| Containment rate | Agent telemetry: tasks closed with no human touch |
| Accuracy | Your evaluation set or sampled human review of closed tasks — never the agent's own confidence |
| Assisted time saving | Handle time on agent-touched tasks versus the baseline |
| Cost per request | Trace / observability export (requests and model spend) |
| Infrastructure | The platform bill, allocated by a stated rule |
| Review minutes | Time reviewers actually spend per escalation, sampled |
| Escalation share | Of the tasks the agent did not contain, the share a human reviews |
| Build cost | Project actuals, including evaluation and integration work |

Two sourcing rules matter most. Accuracy must come from independent
evaluation, or the model will certify whatever the agent claims. And
baseline minutes must predate the agent, or the "saving" is measured
against a baseline the agent itself already changed.

## 2. Run the evaluation

Feed measured rates directly:

```python
from roi.costs import CostInputs, cost_breakdown
from roi.value import ValueInputs, value_breakdown

costs = cost_breakdown(CostInputs(
    requests=18000, avg_cost_per_request=0.11, infra_monthly=420.0,
    escalation_rate=0.19, review_minutes=6.0, loaded_hourly_rate=38.0,
    failure_rate=0.043, baseline_cost_per_task=5.70,
    build_cost=48000.0, amortize_months=24))
value = value_breakdown(ValueInputs(
    volume=18000, baseline_minutes=9.0, loaded_hourly_rate=38.0,
    containment_rate=0.62, accuracy=0.93, assisted_time_saving=0.35))
net = value.gross - costs.total
```

Or describe the use case by drivers and let the framework derive the
rates — required for sensitivity and break-even, where the rates must
move with the assumptions:

```python
from roi.compute import UseCase, evaluate, sensitivity

triage = UseCase(
    name="Support triage", volume=18000, baseline_minutes=9.0,
    loaded_hourly_rate=38.0, containment_rate=0.62, accuracy=0.93,
    assisted_time_saving=0.35, avg_cost_per_request=0.11,
    infra_monthly=420.0, review_minutes=6.0, escalation_share=0.50,
    build_cost=48000.0)
result = evaluate(triage)
print(result.net_value, result.roi_pct, result.breakeven_containment)
print(sensitivity(triage).fragile)
```

## 3. Read the output like a reviewer

- Start with the **cost detail table**, not the headline. If human
  review dominates (it usually does), the roadmap item is escalation
  design, not a cheaper model.
- Treat a **fragile** flag as the action item: the decision depends on
  disputed estimates, so narrow the estimates (better evals, a time
  study) before scaling the use case.
- Use **break-even containment** in planning. "Raise containment from
  30% to 43%" is a goal a team can organise around; "improve ROI" is
  not.
- A use case that never pays back is not automatically a kill — it may
  be a deliberate quality or risk investment — but the framework makes
  someone say so explicitly, with the monthly figure attached.

## 4. Gate new work with intake scoring

Score candidates before discovery work begins. The `poor` verdict
(low volume, high complexity) exists to stop the most common portfolio
mistake: an impressive demo attached to a task that does not recur
often enough to repay building it. Require the intake estimates to be
written down; when the built system's actuals arrive, comparing them
against the intake estimates is how the gate gets calibrated.

## 5. Decisions recorded (ADR summary)

- **Value = avoided handling cost only.** Revenue and satisfaction
  effects are excluded so every figure can be audited against time and
  wage data. Programmes that need them should model them separately,
  not blend them in.
- **Accuracy multiplies all value.** Simpler than per-term factors and
  deliberately conservative; it prevents a high-containment,
  low-accuracy agent from ever looking good.
- **Rates derive from drivers in scenario mode.** Freezing cost rates
  while varying containment double-counts improvements; deriving them
  keeps scenarios internally consistent.
- **Impossible answers are `None`.** Payback and break-even never
  fabricate a number for a use case that cannot reach one.

## 6. Misuse risks to guard against

- **Cherry-picked accuracy:** evaluating on easy tasks inflates every
  value term. Sample accuracy from production traffic, stratified by
  task type.
- **Baseline shopping:** choosing the slowest historical handling time
  as the baseline. Fix the baseline source at programme start.
- **Vanishing reviewers:** excluding review time because reviewers sit
  in another team's budget. If a human finishes the agent's work, the
  agent owns that cost here.
- **Survivor portfolios:** quietly dropping losing use cases from the
  rollup. The rollup is only meaningful over the whole portfolio,
  losers included.
