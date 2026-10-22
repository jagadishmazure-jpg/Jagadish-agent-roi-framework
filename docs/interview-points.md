# Interview points: agent ROI framework

**The one-liner.** "Everyone can tell you what their agent costs in
tokens. I built the framework that answers what it's *worth* — value
modelled from handling time and wages, discounted by measured accuracy,
against a cost model that charges the agent for its human reviewers,
its failures, and its own build."

**Why it exists.** In the demo portfolio, inference is 4% of the
returns agent's true monthly cost. The biggest line is human review of
escalations — 59–69% of total cost in three of four use cases. Any ROI
conversation that starts with model pricing is looking at the smallest
number on the page.

**Design choices to talk about.**

- *Accuracy multiplies all value.* A task resolved wrong is not
  deflection, it's a rework bill. At zero accuracy the model says the
  agent creates zero value, whatever its containment dashboard claims.
  That makes the eval programme a financial control, not a nicety.
- *Break-even containment beats ROI % as a planning number.* "This use
  case breaks even at 43% containment and sits at 30%" gives a team a
  target and a go/no-go rule. ROI percentages give them a poster.
- *Scenarios derive rates from drivers.* Raise containment and
  escalations fall while failures rise, because both come from the same
  task pool. Freezing last month's escalation bill while assuming next
  quarter's containment is the classic spreadsheet double-count.
- *Fragile is a first-class output.* If the plausible range straddles
  zero, the honest deliverable is "narrow the estimates", not a point
  figure with more decimals.
- *Impossible answers are `None`.* Payback for a losing agent is
  "never", break-even for a hopeless one is "unreachable" — the code
  refuses to manufacture comforting numbers.

**Numbers to quote (fictional demo, computed by the code).** Portfolio
net $115,295.64/month at 157.6% ROI, 1.8-month payback across four use
cases; order status pays back in 0.6 months; internal IT help loses
$2,105.22/month (−12.9%) and never pays back at 30% containment against a
35.5% break-even. Human review is the biggest cost line in every case.
Review story: an earlier version billed failed tasks twice and
double-counted the build in payback; fixing both moved ROI from 141.6% to
157.6% and showed Returns was never actually fragile.

**How it connects.** Trace observability supplies cost per successful
request; evals supply accuracy; FinOps work supplies the infrastructure
allocation. This framework is the layer that joins them into the
business case — and its intake gate is where the portfolio decides what
*not* to build.
