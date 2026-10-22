# ADR 002 — Bill a failed containment exactly once

**Status:** accepted (2026-10-22)

**Context.** The first version excluded failed tasks from value *and*
charged them as rework, so each failure cost two baselines.

**Decision.** In the joined model, all contained tasks count as avoided
first-pass handling and failed ones are charged back as rework. Standalone,
`roi/value.py` still reports value net of failures. Payback divides the
build by operating net (before the amortised build share).

**Consequences.** Demo ROI moved from 141.6% to 157.6%; Returns handling is
no longer fragile. Both bugs are pinned by tests.
