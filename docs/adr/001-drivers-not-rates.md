# ADR 001 — Model scenarios from drivers, not frozen rates

**Status:** accepted (2026-10-22)

**Decision.** A `UseCase` is described by volume, handling time,
containment, accuracy and wage; escalation and failure rates are derived.

**Consequences.** What-if questions move every dependent line together.
Measured rates can still be fed directly into `roi/costs.py`.
