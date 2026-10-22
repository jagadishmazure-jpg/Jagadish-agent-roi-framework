"""Render an ROI evaluation as Markdown or a self-contained HTML page.

Every figure in a report is formatted from a value the engine computed
in the same run -- the report layer does no arithmetic of its own, so a
report cannot quietly drift away from the model. Tests assert that the
headline numbers in the rendered text equal the computed ones.
"""
import html

from .compute import evaluate, rollup, sensitivity
from .costs import cost_breakdown
from .intake import rank_candidates


def fmt_money(value):
    if value is None:
        return "n/a"
    return "$%s" % format(round(value, 2), ",.2f")


def fmt_pct(value):
    if value is None:
        return "n/a"
    return "%.1f%%" % value


def fmt_months(value):
    if value is None:
        return "never"
    return "%.1f mo" % value


def fmt_rate(value):
    if value is None:
        return "unreachable"
    return "%.1f%%" % (value * 100.0)


def build_report(use_cases, candidates=()):
    """Compute everything once; both renderers consume this structure."""
    results = [evaluate(uc) for uc in use_cases]
    return {
        "use_cases": use_cases,
        "results": results,
        "sensitivities": [sensitivity(uc) for uc in use_cases],
        "costs": [cost_breakdown(uc.cost_inputs()) for uc in use_cases],
        "portfolio": rollup(use_cases),
        "intake": rank_candidates(list(candidates)),
    }


def render_markdown(report, title="Agent ROI report"):
    r = report["results"]
    p = report["portfolio"]
    lines = ["# %s" % title, ""]
    lines.append("## Per-use-case results (one month)")
    lines.append("")
    lines.append(
        "| Use case | Gross value | Total cost | Net value | ROI | "
        "Agent $/correct task | Human $/task | Payback | Break-even containment |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for res in r:
        lines.append(
            "| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                res.name,
                fmt_money(res.gross_value),
                fmt_money(res.total_cost),
                fmt_money(res.net_value),
                fmt_pct(res.roi_pct),
                fmt_money(res.cost_per_correct_resolution),
                fmt_money(res.human_cost_per_task),
                fmt_months(res.payback_months),
                fmt_rate(res.breakeven_containment),
            ))
    lines.append("")
    lines.append("## Portfolio rollup")
    lines.append("")
    lines.append("- Gross value: %s" % fmt_money(p.gross_value))
    lines.append("- Total cost: %s" % fmt_money(p.total_cost))
    lines.append("- Net value: %s" % fmt_money(p.net_value))
    lines.append("- Portfolio ROI: %s" % fmt_pct(p.roi_pct))
    lines.append("- Total build cost: %s" % fmt_money(p.total_build_cost))
    lines.append("- Portfolio payback: %s" % fmt_months(p.payback_months))
    lines.append("")
    lines.append("## Cost detail (where the money actually goes)")
    lines.append("")
    lines.append(
        "| Use case | Inference | Infrastructure | Human review | "
        "Failure rework | Build (amortised) |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for uc, costs in zip(report["use_cases"], report["costs"]):
        lines.append(
            "| %s | %s | %s | %s | %s | %s |" % (
                uc.name,
                fmt_money(costs.inference),
                fmt_money(costs.infrastructure),
                fmt_money(costs.human_review),
                fmt_money(costs.failure_rework),
                fmt_money(costs.build_amortized),
            ))
    lines.append("")
    lines.append("## Sensitivity (net value if the estimates are wrong)")
    lines.append("")
    lines.append("| Use case | Pessimistic | Expected | Optimistic | Verdict |")
    lines.append("| --- | ---: | ---: | ---: | --- |")
    for uc, s in zip(report["use_cases"], report["sensitivities"]):
        verdict = "FRAGILE -- sign flips inside the plausible range" if s.fragile else "stable"
        lines.append(
            "| %s | %s | %s | %s | %s |" % (
                uc.name, fmt_money(s.low_net), fmt_money(s.base_net),
                fmt_money(s.high_net), verdict))
    lines.append("")
    if report["intake"]:
        lines.append("## Intake ranking (candidates not yet built)")
        lines.append("")
        lines.append("| Rank | Candidate | Score | Verdict | Why |")
        lines.append("| ---: | --- | ---: | --- | --- |")
        for i, s in enumerate(report["intake"], start=1):
            lines.append(
                "| %d | %s | %.1f | %s | %s |" % (
                    i, s.candidate.name, s.score, s.verdict, "; ".join(s.reasons)))
        lines.append("")
    lines.append(
        "All figures are computed from the input data at run time. "
        "Telemetry and rates in the demo are fictional.")
    lines.append("")
    return "\n".join(lines)


def render_html(report, title="Agent ROI report"):
    md = render_markdown(report, title)
    # Deliberately simple: the Markdown is the source, wrapped in a
    # readable page with the tables preserved as preformatted text plus a
    # summary header built from the computed portfolio values.
    p = report["portfolio"]
    summary = (
        "<p><strong>Net value:</strong> %s &nbsp; <strong>ROI:</strong> %s &nbsp; "
        "<strong>Payback:</strong> %s</p>" % (
            html.escape(fmt_money(p.net_value)),
            html.escape(fmt_pct(p.roi_pct)),
            html.escape(fmt_months(p.payback_months)),
        )
    )
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head><meta charset=\"utf-8\">"
        "<title>%s</title></head>\n<body>\n<h1>%s</h1>\n%s\n<pre>\n%s\n</pre>\n"
        "</body>\n</html>\n" % (
            html.escape(title), html.escape(title), summary, html.escape(md))
    )
