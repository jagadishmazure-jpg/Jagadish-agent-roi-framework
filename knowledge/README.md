# Knowledge notes

Short, self-contained explanations of the thinking behind this repo.

1. [Why agent ROI is hard](01-why-roi-is-hard.md) — the four failure
   modes of naive ROI claims: hidden people costs, deflection counted
   as value, a moving baseline, and gameable point estimates.
2. [The cost model](02-cost-model.md) — five components (inference,
   infrastructure, human review, failure rework, amortised build), why
   they are never blended, and which lever moves each.
3. [Value and break-even](03-value-and-break-even.md) — avoided handling
   cost discounted by accuracy, break-even containment as the actionable
   number, and why scenarios must move costs and value together.
4. [Architecture](04-architecture.md) — module boundaries, and the design
   decisions (validation at construction, `None` for impossible answers,
   sum-then-ratio rollups, test-pinned reports) that keep the numbers
   defensible.
