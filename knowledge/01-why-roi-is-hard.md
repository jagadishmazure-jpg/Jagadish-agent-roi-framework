# Why agent ROI is hard to state honestly

Every agent programme eventually faces the same meeting: someone senior
asks what the system returns for what it costs, and the room produces a
token bill and a deflection percentage. Neither number survives scrutiny,
for four separate reasons.

**The visible cost is the smallest cost.** Metering makes model spend
feel like the whole story because it arrives as an invoice. In this
repo's demo, inference is 4% of the returns agent's true monthly cost.
The dominant lines are people: reviewers finishing escalations, and
staff redoing work the agent got wrong. Those costs live in other teams'
budgets, so they vanish from the agent's ledger unless someone goes
looking for them. A framework that does not charge them to the agent is
marketing, not measurement.

**Deflection is not value.** Counting every conversation the agent
closed as money saved assumes each closure was correct. Some share of
them were wrong, and a wrongly closed task is worse than an untouched
one: the customer comes back angrier, and the work is done twice. Value
has to be discounted by measured accuracy, which means an ROI claim is
only ever as good as the evaluation programme feeding it.

**The baseline moves.** "What would this have cost without the agent?"
sounds static, but volumes grow, wages rise, and the mix of easy and
hard tasks shifts as the agent absorbs the easy ones. The remaining
human work gets harder on average, so a naive before/after comparison
overstates the saving. Modelling value per task, from handling time and
wage, at least makes the assumption explicit and arguable.

**Point estimates invite gaming.** Whoever funds the agent chooses the
containment assumption; whoever opposes it chooses another. A single
ROI figure is therefore a negotiation artifact. A range — here is the
answer if containment is ten points worse than hoped, and if it is ten
points better — converts the argument into a question about which
estimate is believable, and flags the cases where the decision flips
inside that range. Those fragile cases are where management attention
belongs.

The framework in this repo is built around these four failure modes:
charge every cost to the agent, discount value by correctness, derive
value from stated per-task baselines, and always report a range.
