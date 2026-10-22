# Agent ROI report -- Cinder Peak Outfitters (fictional)

## Per-use-case results (one month)

| Use case | Gross value | Total cost | Net value | ROI | Agent $/correct task | Human $/task | Payback | Break-even containment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Support triage | $71,849.75 | $21,848.84 | $50,000.91 | 228.8% | $2.11 | $5.70 | 1.0 mo | 5.8% |
| Order status | $56,702.97 | $7,493.60 | $49,209.37 | 656.7% | $0.35 | $2.53 | 0.6 mo | 10.1% |
| Returns handling | $35,989.80 | $27,522.67 | $8,467.13 | 30.8% | $9.27 | $8.87 | 10.0 mo | 32.4% |
| Internal IT help | $12,231.65 | $16,293.11 | $-4,061.46 | -24.9% | $30.48 | $15.60 | never | 42.8% |

## Portfolio rollup

- Gross value: $176,774.17
- Total cost: $73,158.21
- Net value: $103,615.96
- Portfolio ROI: 141.6%
- Total build cost: $218,000.00
- Portfolio payback: 2.1 mo

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
| Support triage | $27,039.92 | $50,000.91 | $81,033.79 | stable |
| Order status | $29,424.67 | $49,209.37 | $72,040.40 | stable |
| Returns handling | $-2,006.05 | $8,467.13 | $24,174.62 | FRAGILE -- sign flips inside the plausible range |
| Internal IT help | $-7,181.83 | $-4,061.46 | $1,453.99 | FRAGILE -- sign flips inside the plausible range |

## Intake ranking (candidates not yet built)

| Rank | Candidate | Score | Verdict | Why |
| ---: | --- | ---: | --- | --- |
| 1 | Product questions on the catalogue | 71.7 | strong | volume is high enough for savings to compound monthly; unaided handling is already quick, limiting the saving per task; a large share of the work looks containable by an agent |
| 2 | Warranty claim intake | 51.0 | viable | no single dominant factor; a mid-range case on every driver |
| 3 | Shift-swap helper for store staff | 34.4 | poor | monthly volume is low, so total savings stay small; marked poor: low volume paired with high build complexity rarely repays the build |

All figures are computed from the input data at run time. Telemetry and rates in the demo are fictional.
