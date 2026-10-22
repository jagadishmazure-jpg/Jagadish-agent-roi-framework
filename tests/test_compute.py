"""End-to-end ROI: net, ROI %, payback, break-even, sensitivity, rollup."""
import pytest

from demos.meridian import USE_CASES
from roi.compute import (
    UseCase,
    breakeven_containment,
    evaluate,
    payback_months,
    rollup,
    sensitivity,
)

# Hand-computed fixture (one month):
#   human cost/task = 10/60 * 60                       = 10
#   gross value     = .9*(2500*10) + .9*(2500*10*.2)   = 22500 + 4500 = 27000
#   inference       = 5000 * .08                       = 400
#   infra                                              = 250
#   escalation rate = (1-.5)*.5 = .25 -> 1250 reviews
#   review cost     = 1250 * (5/60) * 60               = 6250
#   failure rate    = .5*(1-.9) = .05 -> 250 redone
#   rework          = 250 * 10                         = 2500
#   build amortised = 24000 / 24                      = 1000
#   total cost                                         = 10400
#   net = 16600, ROI = 159.6%, payback = 24000/16600   = 1.45 months
#   correctly contained = 2250, cost/correct = 10400/2250 = 4.62
UC = UseCase(
    name="Fixture",
    volume=5000,
    baseline_minutes=10.0,
    loaded_hourly_rate=60.0,
    containment_rate=0.5,
    accuracy=0.9,
    assisted_time_saving=0.2,
    avg_cost_per_request=0.08,
    infra_monthly=250.0,
    review_minutes=5.0,
    escalation_share=0.5,
    build_cost=24000.0,
)

BY_NAME = {uc.name: uc for uc in USE_CASES}


def test_derived_rates_follow_containment_and_accuracy():
    ci = UC.cost_inputs()
    assert ci.escalation_rate == pytest.approx(0.25)
    assert ci.failure_rate == pytest.approx(0.05)


def test_evaluate_headline_numbers():
    r = evaluate(UC)
    assert r.gross_value == pytest.approx(27000.0)
    assert r.total_cost == pytest.approx(10400.0)
    assert r.net_value == pytest.approx(16600.0)
    assert r.roi_pct == pytest.approx(16600.0 / 10400.0 * 100.0)
    assert r.human_cost_per_task == pytest.approx(10.0)


def test_cost_per_correct_resolution():
    r = evaluate(UC)
    assert r.cost_per_correct_resolution == pytest.approx(10400.0 / 2250.0)


def test_payback_months():
    r = evaluate(UC)
    assert r.payback_months == pytest.approx(24000.0 / 16600.0)


def test_payback_zero_build_is_immediate():
    free_build = UC.with_changes(build_cost=0.0)
    assert payback_months(free_build, 1000.0) == 0.0


def test_payback_never_when_net_is_negative():
    it_help = BY_NAME["Internal IT help"]
    r = evaluate(it_help)
    assert r.net_value < 0
    assert r.payback_months is None


def test_breakeven_plug_back_nets_to_zero():
    for name in ("Support triage", "Returns handling", "Internal IT help"):
        uc = BY_NAME[name]
        solved = breakeven_containment(uc)
        assert solved is not None and 0.0 < solved < 1.0
        net_at_solved = evaluate(uc.with_changes(containment_rate=solved)).net_value
        assert abs(net_at_solved) < 5.0  # bisection tolerance, in dollars


def test_breakeven_unreachable_returns_none():
    hopeless = UseCase(
        name="Hopeless", volume=50, baseline_minutes=5.0, loaded_hourly_rate=30.0,
        containment_rate=0.4, accuracy=1.0, assisted_time_saving=0.0,
        avg_cost_per_request=0.05, infra_monthly=100.0, review_minutes=5.0,
        escalation_share=0.5, build_cost=500000.0)
    assert breakeven_containment(hopeless) is None
    assert evaluate(hopeless).breakeven_containment is None


def test_breakeven_zero_when_already_profitable_without_containment():
    assistant_only = UseCase(
        name="Assistant only", volume=5000, baseline_minutes=10.0,
        loaded_hourly_rate=60.0, containment_rate=0.0, accuracy=1.0,
        assisted_time_saving=0.5, avg_cost_per_request=0.001,
        infra_monthly=10.0, review_minutes=5.0, escalation_share=0.0,
        build_cost=0.0)
    assert breakeven_containment(assistant_only) == 0.0


def test_sensitivity_orders_low_base_high_for_a_strong_case():
    s = sensitivity(BY_NAME["Support triage"])
    assert s.low_net < s.base_net < s.high_net
    assert s.fragile is False


def test_sensitivity_flags_the_fragile_demo_case():
    s = sensitivity(BY_NAME["Returns handling"])
    assert s.low_net < 0 < s.high_net
    assert s.fragile is True


def test_sensitivity_stable_negative_is_not_fragile_by_sign_alone():
    # A case negative in all three readings has a stable (bad) verdict
    # only if the optimistic swing also stays negative; craft one.
    weak = UseCase(
        name="Weak", volume=300, baseline_minutes=6.0, loaded_hourly_rate=30.0,
        containment_rate=0.2, accuracy=0.7, assisted_time_saving=0.1,
        avg_cost_per_request=0.30, infra_monthly=400.0, review_minutes=15.0,
        escalation_share=0.9, build_cost=90000.0)
    s = sensitivity(weak)
    assert s.high_net < 0
    assert s.fragile is False


def test_rollup_sums_then_ratios():
    p = rollup(USE_CASES)
    results = [evaluate(uc) for uc in USE_CASES]
    assert p.gross_value == pytest.approx(sum(r.gross_value for r in results))
    assert p.total_cost == pytest.approx(sum(r.total_cost for r in results))
    assert p.net_value == pytest.approx(sum(r.net_value for r in results))
    assert p.roi_pct == pytest.approx(p.net_value / p.total_cost * 100.0)
    assert p.total_build_cost == pytest.approx(218000.0)


def test_rollup_of_losing_portfolio_never_pays_back():
    p = rollup([BY_NAME["Internal IT help"]])
    assert p.net_value < 0
    assert p.payback_months is None


def test_rollup_empty_portfolio():
    p = rollup([])
    assert p.gross_value == 0.0 and p.total_cost == 0.0 and p.net_value == 0.0
    assert p.roi_pct is None


def test_zero_volume_use_case_does_not_crash():
    idle = UseCase(
        name="Idle", volume=0, baseline_minutes=10.0, loaded_hourly_rate=50.0,
        containment_rate=0.5, accuracy=0.9, assisted_time_saving=0.2,
        avg_cost_per_request=0.10, infra_monthly=100.0, review_minutes=5.0,
        escalation_share=0.5, build_cost=12000.0)
    r = evaluate(idle)
    assert r.gross_value == 0.0
    assert r.total_cost == pytest.approx(100.0 + 500.0)  # infra + amortised build
    assert r.net_value < 0
    assert r.cost_per_correct_resolution is None


def test_zero_containment_has_no_correct_resolutions():
    r = evaluate(UC.with_changes(containment_rate=0.0))
    assert r.cost_per_correct_resolution is None


def test_zero_accuracy_earns_nothing_but_still_costs():
    r = evaluate(UC.with_changes(accuracy=0.0))
    assert r.gross_value == 0.0
    assert r.net_value == pytest.approx(-r.total_cost)
    assert r.net_value < 0


def test_escalation_load_can_exceed_containment():
    # Internal IT help: 49% of all requests end up reviewed while only
    # 30% are contained -- the derived escalation rate exceeds the
    # containment rate and the model must still hold together.
    it_help = BY_NAME["Internal IT help"]
    ci = it_help.cost_inputs()
    assert ci.escalation_rate == pytest.approx(0.49)
    assert ci.escalation_rate > it_help.containment_rate
    assert evaluate(it_help).total_cost > 0


def test_demo_portfolio_has_both_winners_and_a_loser():
    nets = {uc.name: evaluate(uc).net_value for uc in USE_CASES}
    assert nets["Order status"] > 0
    assert nets["Support triage"] > 0
    assert nets["Internal IT help"] < 0
