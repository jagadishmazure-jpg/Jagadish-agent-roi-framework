# Security policy

## Scope

This is a portfolio learning project. It runs fully offline on fictional,
aggregate data: there are no live services, no credentials, no transcripts
and no real customer or employee data anywhere in the repo. Inputs are
counts, minutes and rates — a deployment of this framework never needs
personal data to produce its numbers.

## Safety properties (tested, not just documented)

- Physically impossible inputs (rates outside [0, 1], negative money or
  volumes, zero-length periods) are rejected at construction instead of
  flowing into a report.
- Impossible answers are returned as `None` and rendered as "never" /
  "unreachable" — payback and break-even never fabricate a number for a
  use case that cannot reach one.
- The report layer performs no arithmetic of its own, and tests pin the
  rendered figures to the engine's computed figures, so a published
  report cannot silently diverge from the model it claims to summarise.

## Reporting a vulnerability

If you find a security issue in this demo code, please open a GitHub
issue. Do not include any real personal data in the report.
