# The cost model: five components, no blending

`roi/costs.py` splits an agent's period cost into five components and
refuses to merge them, because each has a different owner, a different
growth curve, and a different lever.

1. **Inference.** Requests served times the average model cost per
   request. This is the number observability pipelines already emit,
   and in most portfolios it is the *smallest* line — which is precisely
   why quoting it alone misleads.
2. **Infrastructure.** The agent's allocated share of platform, hosting,
   vector stores, licences and tooling for the period. Allocation is an
   accounting choice; the model takes the allocated figure as an input
   rather than pretending to derive it.
3. **Human review.** Escalated requests times review minutes times the
   loaded hourly rate of the reviewer. This is the component teams most
   often forget, and in the demo it is the largest for three of the four
   use cases (59–69% of total cost). The lever is escalation design:
   what the agent attempts alone, and how much context it hands over.
4. **Failure rework.** Failed tasks redone from scratch at the full
   human baseline cost. A failure is not free and not merely "no value":
   the work is performed twice, once badly and once properly, and the
   customer experiences both.
5. **Build, amortised.** The one-time build cost spread across a stated
   horizon (24 months by default). Without this line, a programme can
   claim monthly profit while never recovering what it spent — the
   payback calculation in `compute.py` exists to catch exactly that.

Two properties are enforced in code. Components are computed from raw
drivers (counts, minutes, rates), so a report can always be traced back
to an assumption a person can challenge. And the breakdown object sums
its own components for the total — there is no second, separately
maintained total anywhere in the codebase to drift out of sync.
