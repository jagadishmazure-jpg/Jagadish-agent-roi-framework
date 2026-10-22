# Threat model — agent ROI framework

The framework holds no personal data, so the main threat is to the
*integrity of the business case*: inputs or scenarios chosen to make an
agent look profitable.

| Threat | Example | Control | Residual risk |
| --- | --- | --- | --- |
| Tampering (inputs) | Accuracy or containment above 1, negative costs | Validation at construction raises immediately | Plausible-but-optimistic inputs are not detectable |
| Tampering (method) | Counting failed tasks as value, ignoring review or build cost | Five separate cost lines; failures billed once as rework; amortised build charged | — |
| Repudiation | "The model said so" with no traceable figures | Reports format engine outputs only; README demo block re-run in CI | — |
| Misleading output | One flattering number | Low/base/high sensitivity; FRAGILE flag; "never" payback; unreachable break-even | Ranges are ±10 pts containment, ±5 pts accuracy, ±20% wage; wider uncertainty is not modelled |
| Double counting | Build cost in net and again in payback | Payback uses operating net (fixed 2026-10-22, test-pinned) | — |
