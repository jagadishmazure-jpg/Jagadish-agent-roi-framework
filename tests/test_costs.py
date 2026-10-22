"""Cost model: every component checked against hand-computed fixtures."""
import pytest

from roi.costs import (
    CostInputs,
    build_amortized_cost,
    cost_breakdown,
    escalated_requests,
    failed_tasks,
    failure_rework_cost,
    human_review_cost,
    inference_cost,
    infrastructure_cost,
)

# Hand-computed fixture:
#   inference   = 1000 * 0.10                       = 100
#   infra       = 200 * 2 months                    = 400
#   escalations = 1000 * 0.20 = 200 reviews
#   review      = 200 * (12/60) * 50                = 2000
#   failures    = 1000 * 0.05 = 50 tasks
#   rework      = 50 * 8                            = 400
#   build       = 12000 / 12 * 2                    = 2000
#   total                                           = 4900
CI = CostInputs(
    requests=1000,
    avg_cost_per_request=0.10,
    infra_monthly=200.0,
    months=2,
    escalation_rate=0.20,
    review_minutes=12.0,
    loaded_hourly_rate=50.0,
    failure_rate=0.05,
    baseline_cost_per_task=8.0,
    build_cost=12000.0,
    amortize_months=12,
)


def test_inference_cost():
    assert inference_cost(CI) == pytest.approx(100.0)


def test_infrastructure_cost_scales_with_months():
    assert infrastructure_cost(CI) == pytest.approx(400.0)
    one_month = CostInputs(requests=0, avg_cost_per_request=0.0, infra_monthly=200.0)
    assert infrastructure_cost(one_month) == pytest.approx(200.0)


def test_escalated_request_count():
    assert escalated_requests(CI) == pytest.approx(200.0)


def test_human_review_cost():
    assert human_review_cost(CI) == pytest.approx(2000.0)


def test_failed_task_count():
    assert failed_tasks(CI) == pytest.approx(50.0)


def test_failure_rework_cost():
    assert failure_rework_cost(CI) == pytest.approx(400.0)


def test_build_amortized_cost():
    assert build_amortized_cost(CI) == pytest.approx(2000.0)


def test_breakdown_total_is_sum_of_components():
    b = cost_breakdown(CI)
    assert b.total == pytest.approx(4900.0)
    assert b.total == pytest.approx(
        b.inference + b.infrastructure + b.human_review
        + b.failure_rework + b.build_amortized)


def test_defaults_charge_only_inference_and_infra():
    bare = CostInputs(requests=500, avg_cost_per_request=0.02, infra_monthly=90.0)
    b = cost_breakdown(bare)
    assert b.human_review == 0.0
    assert b.failure_rework == 0.0
    assert b.build_amortized == 0.0
    assert b.total == pytest.approx(500 * 0.02 + 90.0)


def test_zero_requests_still_charges_infra_and_build():
    idle = CostInputs(
        requests=0, avg_cost_per_request=0.10, infra_monthly=150.0,
        escalation_rate=0.5, review_minutes=10.0, loaded_hourly_rate=40.0,
        failure_rate=0.5, baseline_cost_per_task=9.0,
        build_cost=2400.0, amortize_months=24)
    b = cost_breakdown(idle)
    assert b.inference == 0.0
    assert b.human_review == 0.0
    assert b.failure_rework == 0.0
    assert b.total == pytest.approx(150.0 + 100.0)


def test_high_escalation_rate_is_valid_telemetry():
    # Rates in this module are measured independently; an escalation rate
    # above any particular containment figure is not an error here.
    heavy = CostInputs(
        requests=100, avg_cost_per_request=0.0, infra_monthly=0.0,
        escalation_rate=0.9, review_minutes=6.0, loaded_hourly_rate=30.0)
    assert human_review_cost(heavy) == pytest.approx(100 * 0.9 * 0.1 * 30.0)


def test_negative_requests_rejected():
    with pytest.raises(ValueError):
        CostInputs(requests=-1, avg_cost_per_request=0.0, infra_monthly=0.0)


def test_rate_above_one_rejected():
    with pytest.raises(ValueError):
        CostInputs(requests=1, avg_cost_per_request=0.0, infra_monthly=0.0,
                   escalation_rate=1.5)


def test_zero_months_rejected():
    with pytest.raises(ValueError):
        CostInputs(requests=1, avg_cost_per_request=0.0, infra_monthly=0.0, months=0)


def test_zero_amortisation_rejected():
    with pytest.raises(ValueError):
        CostInputs(requests=1, avg_cost_per_request=0.0, infra_monthly=0.0,
                   build_cost=100.0, amortize_months=0)
