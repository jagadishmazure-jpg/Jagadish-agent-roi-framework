# Agent ROI Framework — what an agent earns versus what it costs

> Synthetic data only. Independent project, not affiliated with or endorsed
> by any vendor or employer. Every company, wage and volume below is
> fictional, and every figure is computed from that fictional data at run
> time by the code in this repo.

**Recruiter summary.** Teams can meter an agent's token bill to the cent
yet usually cannot answer the only question that matters: is it worth
more than it costs? This framework joins operational telemetry (requests,
containment, accuracy, escalations) to business baselines (handling time,
loaded wages) and computes ROI the way a finance reviewer would demand —
with human review, failure rework and amortised build cost all charged
to the agent, break-even containment solved rather than assumed, and a
sensitivity range instead of one flattering number. On the fictional demo
portfolio: **net $115,295.64/month, ROI 157.6%, payback 1.8 months** —
and one of the four use cases (Internal IT help, **−12.9%**) honestly loses
money. Human review is the largest cost line in every use case, ahead of
inference. 73 offline tests.

## The problem

An agent's *cost* side is easy to observe and easy to understate. The
demo's own numbers show why: for the returns agent, inference is
**$1,200 of a $27,522.67 monthly cost (4%)**. The rest is people —
$18,810 of human review for escalations the agent could not finish, and
$3,591 of rework for tasks it finished wrongly — plus platform and the
month's share of an $85,000 build. Any ROI claim built on the model bill
alone is fiction.

The *value* side is usually worse: a deflection count multiplied by a
salary, with no adjustment for the deflected tasks that were resolved
incorrectly. This framework's rule is blunt — a task resolved wrong is
not value, it is a rework bill. In the joined model a wrongly contained
task is charged exactly once: its avoided handling counts as value and
its redo counts as rework cost, so at zero accuracy containment nets to
zero and only the agent's own costs remain. (Standalone, `roi/value.py`
reports value already net of failures.)

## How it works

```mermaid
flowchart LR
    T[Telemetry<br/>requests, containment,<br/>accuracy, escalations] --> C[roi/costs.py<br/>5 cost components]
    B[Business baseline<br/>handling minutes,<br/>loaded hourly rate] --> V[roi/value.py<br/>avoided handling cost<br/>x accuracy]
    C --> X[roi/compute.py<br/>net, ROI, payback,<br/>break-even, sensitivity]
    V --> X
    X --> R[roi/reports.py<br/>Markdown + HTML]
    I[Candidate use cases] --> G[roi/intake.py<br/>score + rank + poor marker]
    G --> X
```

1. **Cost model** (`roi/costs.py`) — inference, infrastructure, human
   review of escalations, rework of failed tasks at baseline cost, and
   the period's amortised share of build cost. Components are reported
   separately; nothing is blended away.
2. **Value model** (`roi/value.py`) — baseline cost avoided on correctly
   contained tasks, plus measured handling-time savings on tasks a human
   still finished, both scaled by accuracy.
3. **Computation** (`roi/compute.py`) — net value, ROI %, cost per
   correctly resolved task versus the human cost per task, payback in
   months (explicitly *never* when monthly net is negative), break-even
   containment (bisected from the model, verified by plugging it back
   in), and a low/base/high sensitivity sweep. A use case whose plausible
   range straddles zero is flagged **fragile**.
4. **Intake gate** (`roi/intake.py`) — scores unbuilt candidates on
   volume, handling time, containment plausibility, data readiness and
   risk; low volume paired with high build complexity is marked **poor**
   outright.
5. **Reports** (`roi/reports.py`) — Markdown and HTML rendered from the
   computed values only; tests assert the rendered headline numbers equal
   the engine's, so the report cannot drift from the model.

One design decision matters throughout: scenarios are driven by the
underlying drivers, not by frozen cost rates. Raise containment and the
escalation load falls while the failure load rises, exactly as it would
in production. See `knowledge/03-value-and-break-even.md`.

## Demo results (fictional data, computed at run time)

One month at the invented retailer Cinder Peak Outfitters. The block
below is the real output of the demo; CI re-runs it and fails if this
README drifts (`scripts/render_docs.py --check`).

<!-- run: python scripts/count_tests.py -->
```text
73 tests collected
```
<!-- /run -->

<!-- run: python demos/run_demo.py -->
```text
# Agent ROI report -- Cinder Peak Outfitters (fictional)

## Per-use-case results (one month)

| Use case | Gross value | Total cost | Net value | ROI | Agent $/correct task | Human $/task | Payback | Break-even containment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Support triage | $76,302.59 | $21,848.84 | $54,453.75 | 249.2% | $2.11 | $5.70 | 0.9 mo | 5.4% |
| Order status | $58,382.57 | $7,493.60 | $50,888.97 | 679.1% | $0.35 | $2.53 | 0.6 mo | 9.8% |
| Returns handling | $39,580.80 | $27,522.67 | $12,058.13 | 43.8% | $9.27 | $8.87 | 5.4 mo | 29.0% |
| Internal IT help | $14,187.89 | $16,293.11 | $-2,105.22 | -12.9% | $30.48 | $15.60 | never | 35.5% |

## Portfolio rollup

- Gross value: $188,453.85
- Total cost: $73,158.21
- Net value: $115,295.64
- Portfolio ROI: 157.6%
- Total build cost: $218,000.00
- Portfolio payback: 1.8 mo

## Cost detail (where the money actually goes)

| Use case | Inference | Infrastructure | Human review | Failure rework | Build (amortised) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Support triage | $1,980.00 | $420.00 | $12,996.00 | $4,452.84 | $2,000.00 |
| Order status | $1,300.00 | $300.00 | $2,964.00 | $1,679.60 | $1,250.00 |
| Returns handling | $1,200.00 | $380.00 | $18,810.00 | $3,591.00 | $3,541.67 |
| Internal IT help | $484.00 | $350.00 | $11,211.20 | $1,956.24 | $2,291.67 |

## Sensitivity (net value if the estimates are wrong)

| Use case | Pessimistic | Expected | Optimistic | Verdict |
| --- | ---: | ---: | ---: | --- |
| Support triage | $32,161.72 | $54,453.75 | $82,806.72 | stable |
| Order status | $32,586.27 | $50,888.97 | $72,040.40 | stable |
| Returns handling | $1,159.35 | $12,058.13 | $27,246.92 | stable |
| Internal IT help | $-5,863.95 | $-2,105.22 | $3,760.30 | FRAGILE -- sign flips inside the plausible range |

## Intake ranking (candidates not yet built)

| Rank | Candidate | Score | Verdict | Why |
| ---: | --- | ---: | --- | --- |
| 1 | Product questions on the catalogue | 71.7 | strong | volume is high enough for savings to compound monthly; unaided handling is already quick, limiting the saving per task; a large share of the work looks containable by an agent |
| 2 | Warranty claim intake | 51.0 | viable | no single dominant factor; a mid-range case on every driver |
| 3 | Shift-swap helper for store staff | 34.4 | poor | monthly volume is low, so total savings stay small; marked poor: low volume paired with high build complexity rarely repays the build |

All figures are computed from the input data at run time. Telemetry and rates in the demo are fictional.

wrote demos/output/report.md
wrote demos/output/report.html
```
<!-- /run -->

Intake ranking for three unbuilt candidates: product questions on the
catalogue **71.7 (strong)**, warranty claim intake **51.0 (viable)**,
a shift-swap helper for store staff **34.4 (poor — 900 requests/month
against high build complexity)**.

Two readings worth noticing. Returns handling nets positive even though
its all-in cost per correct resolution ($9.27) exceeds the human cost per
task ($8.87): the unit metric loads every cost — including reviews of
tasks the agent never claimed — onto correctly contained tasks only,
while the value side also earns assisted-time savings across 4,125
human-finished tasks. And Internal IT help is not a mystery failure: at
30% containment against a 35.5% break-even, the framework states exactly
how far it has to climb, or that it should be descoped.

## Run it

```bash
python3 demos/run_demo.py     # prints the report, writes demos/output/
python3 -m pytest tests/      # 73 tests, offline, stdlib only
python3 scripts/count_tests.py
```

No dependencies, no network, no API keys. To model your own agent,
build a `UseCase` with your drivers (see `demos/meridian.py`) and call
`roi.evaluate`, or feed measured rates straight into `roi.costs` /
`roi.value` — the implementation guide walks through both.

## Guardrails and integrity controls

- Inputs are validated at construction: rates must be fractions in
  [0, 1], money and volumes non-negative, period lengths at least one
  month. Nonsense raises immediately instead of producing a glossy
  wrong answer.
- Negative results are first-class: negative ROI prints as negative,
  payback returns `None` (rendered "never"), break-even returns `None`
  ("unreachable") when even perfect containment cannot cover costs.
- The report layer performs no arithmetic of its own; every rendered
  number is formatted from an engine output, and tests pin the two
  together.
- No personal data exists anywhere in the repo; all telemetry is
  fictional and aggregate (counts and rates, never transcripts).

## Limitations

- **Attribution is modelled, not proven.** The framework assumes the
  baseline handling time would have been spent without the agent. It
  cannot detect demand the agent created or suppressed.
- **Loaded rates are assumptions the user must supply.** A wrong wage
  assumption moves every result; that is why sensitivity varies it ±20%
  rather than hiding it.
- **Accuracy is a single input.** Real quality varies by task type; a
  production user should feed per-segment accuracy and run the model
  per segment.
- **Demo telemetry is fictional** and deliberately tidy. Its purpose is
  to exercise the model across winners, a fragile case and a loser —
  not to benchmark any real system.
- Value here is avoided handling cost only. Revenue effects, customer
  satisfaction and risk reduction are real but excluded by design,
  because they cannot be audited against a timesheet.

## Built / Written-not-run / Planned

| Item | Status |
| --- | --- |
| Cost model with 5 separated components | Built, tested |
| Value model with accuracy adjustment | Built, tested |
| Net / ROI / unit-cost / payback computation | Built, tested |
| Break-even containment solver (plug-back verified) | Built, tested |
| Sensitivity sweep with fragile flag | Built, tested |
| Intake scoring, ranking, poor-candidate marker | Built, tested |
| Markdown + HTML reports pinned to engine output | Built, tested |
| Fictional 4-use-case demo portfolio | Built, run |
| CI: ruff, pytest, README-vs-fresh-run check, hashed brand check, gitleaks; CodeQL; Dependabot | Built, running on GitHub Actions |
| Per-segment accuracy inputs | Planned |
| Importing live trace exports as telemetry | Planned |

## Review fixes (portfolio-standard review, 2026-10-22)

Two real math bugs were found and fixed, each pinned by a test in
`tests/test_compute.py`:

1. **Failures were billed twice.** A wrongly contained task was removed
   from value (accuracy factor) *and* charged as rework at full baseline
   cost. Without an agent that task costs one baseline; with a failed
   agent attempt it costs one baseline of rework plus inference. Fixed in
   the joined model (`value_breakdown(..., net_of_failures=False)`).
2. **Payback double-counted the build.** Payback divided the build cost by
   a monthly net that had already been charged the amortised build share.
   It now divides by operating net, and a use case whose net is negative
   (payback longer than its amortisation life) reports *never*.

Effect on the demo (before → after): portfolio ROI 141.6% → 157.6%,
payback 2.1 → 1.8 months, Internal IT help −24.9% → −12.9% (still a
loser), and Returns handling is no longer FRAGILE — its pessimistic case
was negative only because of the double count. Internal IT help is now
the fragile case.

## Threat model and decisions

- `docs/threat-model.md` — misuse of the model (gamed inputs, cherry-picked
  scenarios) and the controls against it.
- `docs/adr/` — key design decisions.

## Related repos

- **Jagadish-azure-finops** — optimises cloud spend itself. This repo is
  different: it asks whether the spend earns anything, for any agent on
  any platform.
- **Jagadish-agent-trace-observability** — produces per-request cost and
  cost-per-successful-request from execution traces. This framework
  consumes that style of telemetry and adds the missing half: the value
  those successful requests created, and the humans still in the loop.
- **Jagadish-llm-evals-observability** — measures whether answers are
  right; its accuracy figures are exactly the input this model needs.

## Docs

- `knowledge/` — why agent ROI is hard, the cost model, value and
  break-even thinking, and the architecture.
- `docs/implementation-guide.md` — adopting the framework on a real
  programme, including where each input should come from.
- `docs/interview-points.md` — the short version for interviews.
