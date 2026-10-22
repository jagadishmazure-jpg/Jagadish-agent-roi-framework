# Value, break-even containment, and why scenarios move together

## Value is avoided handling cost, discounted by correctness

The value model (`roi/value.py`) counts two things. Contained tasks earn
their full baseline cost — the minutes a person no longer spends. Tasks
the agent could not finish still earn the measured fraction of handling
time the human saved by starting from the agent's work. Both terms are
multiplied by accuracy, because both depend on the agent's output being
right: a wrong resolution saves nothing, and a wrong draft does not
shorten anyone's handling time. At zero accuracy the model's value is
zero, however impressive the containment dashboard looks.

## Break-even containment is the most useful single number

Percentage ROI figures are hard to act on. Break-even containment is
not: it is the share of tasks the agent must resolve alone for the use
case to stop losing money, with everything else held at today's values.
Internal IT help in the demo sits at 30% containment against a 42.8%
break-even — a concrete gap a team can plan against, or a reason to
descope. The solver finds the crossing by bisection, and the test suite
verifies it the only way that matters: it plugs the solved rate back
into the model and checks that net value comes out at zero.

## Why scenarios must move the costs too

A common spreadsheet error is to ask "what if containment were 10
points higher?" while leaving the escalation bill frozen at last
month's figure. That double-counts the improvement: contained tasks are
drawn from the same pool that generates escalations and failures. This
framework therefore derives the cost rates from the drivers
(`compute.py`): escalations are a share of the *uncontained* remainder,
failures are the contained-but-wrong slice. Move containment and both
loads move with it, in opposite directions — fewer reviews, more
potential rework. Sensitivity analysis built any other way flatters the
agent, and reviewers who notice will discount everything else on the
page.

## A note on cost per correct resolution

Dividing total cost by correctly contained tasks gives a conservative
unit cost: every dollar — including reviews of tasks the agent never
claimed — is loaded onto the successes. It can exceed the human cost
per task while the use case still nets positive, because assisted tasks
contribute value without appearing in the divisor. Read it as a floor
on efficiency, not as the verdict; the verdict is net value.
