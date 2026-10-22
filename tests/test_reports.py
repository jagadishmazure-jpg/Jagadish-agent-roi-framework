"""Reports: rendered numbers must equal the engine's computed numbers."""

from demos.meridian import CANDIDATES, USE_CASES
from roi.compute import evaluate, rollup
from roi.costs import cost_breakdown
from roi.reports import build_report, fmt_money, fmt_pct, fmt_rate, render_html, render_markdown

REPORT = build_report(USE_CASES, CANDIDATES)
MD = render_markdown(REPORT, "Agent ROI report -- test")
HTML = render_html(REPORT, "Agent ROI report -- test")
RESULTS = {uc.name: evaluate(uc) for uc in USE_CASES}


def test_markdown_contains_every_use_case_net():
    for name, r in RESULTS.items():
        assert name in MD
        assert fmt_money(r.net_value) in MD


def test_markdown_contains_roi_and_unit_costs():
    for r in RESULTS.values():
        assert fmt_pct(r.roi_pct) in MD
        assert fmt_money(r.cost_per_correct_resolution) in MD
        assert fmt_money(r.human_cost_per_task) in MD


def test_markdown_rollup_matches_computed_rollup():
    p = rollup(USE_CASES)
    assert fmt_money(p.gross_value) in MD
    assert fmt_money(p.total_cost) in MD
    assert fmt_money(p.net_value) in MD
    assert fmt_pct(p.roi_pct) in MD


def test_markdown_cost_detail_matches_breakdown():
    returns = next(uc for uc in USE_CASES if uc.name == "Returns handling")
    costs = cost_breakdown(returns.cost_inputs())
    assert fmt_money(costs.human_review) in MD
    assert fmt_money(costs.failure_rework) in MD
    assert fmt_money(costs.build_amortized) in MD


def test_markdown_shows_breakeven_rates():
    for r in RESULTS.values():
        assert fmt_rate(r.breakeven_containment) in MD


def test_markdown_flags_fragile_and_stable_cases():
    assert "FRAGILE" in MD  # Internal IT help flips sign across the range
    fragile_row = next(line for line in MD.splitlines() if "Internal IT help" in line
                       and "FRAGILE" in line)
    assert fmt_money(RESULTS["Internal IT help"].net_value) in fragile_row


def test_markdown_shows_negative_net_for_it_help():
    r = RESULTS["Internal IT help"]
    assert r.net_value < 0
    assert fmt_money(r.net_value) in MD
    assert "never" in MD  # payback renders as "never" for the losing case


def test_markdown_intake_section_ranks_catalogue_first():
    intake_section = MD.split("## Intake ranking")[1]
    first_row = next(line for line in intake_section.splitlines() if line.startswith("| 1 |"))
    assert "Product questions on the catalogue" in first_row
    assert "poor" in intake_section  # the shift-swap verdict is visible


def test_html_is_a_page_and_carries_the_same_headline_numbers():
    assert HTML.startswith("<!DOCTYPE html>")
    p = rollup(USE_CASES)
    assert fmt_money(p.net_value) in HTML
    assert fmt_pct(p.roi_pct) in HTML
    for r in RESULTS.values():
        assert fmt_money(r.net_value) in HTML


def test_report_from_no_use_cases_still_renders():
    empty = render_markdown(build_report([], []), "Empty")
    assert "n/a" in empty  # portfolio ROI has no denominator
