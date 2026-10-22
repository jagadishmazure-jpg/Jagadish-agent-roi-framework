"""Value model: baseline avoidance, adjusted for correctness."""
import pytest

from roi.value import (
    ValueInputs,
    assisted_tasks,
    baseline_cost_per_task,
    contained_tasks,
    correctly_contained,
    total_baseline_cost,
    value_breakdown,
)

# Hand-computed fixture:
#   cost per task   = 12/60 * 45          = 9
#   period baseline = 2000 * 9            = 18000
#   contained       = 1000, assisted      = 1000
#   correctly held  = 1000 * 0.9          = 900
#   contained value = 0.9 * 1000 * 9      = 8100
#   assisted value  = 0.9 * 1000 * 9 * .25 = 2025
#   gross                                 = 10125
VI = ValueInputs(
    volume=2000,
    baseline_minutes=12.0,
    loaded_hourly_rate=45.0,
    containment_rate=0.5,
    accuracy=0.9,
    assisted_time_saving=0.25,
)


def test_baseline_cost_per_task():
    assert baseline_cost_per_task(VI) == pytest.approx(9.0)


def test_total_baseline_cost():
    assert total_baseline_cost(VI) == pytest.approx(18000.0)


def test_task_split():
    assert contained_tasks(VI) == pytest.approx(1000.0)
    assert assisted_tasks(VI) == pytest.approx(1000.0)


def test_correctly_contained_applies_accuracy():
    assert correctly_contained(VI) == pytest.approx(900.0)


def test_value_breakdown_components():
    b = value_breakdown(VI)
    assert b.contained_value == pytest.approx(8100.0)
    assert b.assisted_value == pytest.approx(2025.0)
    assert b.gross == pytest.approx(10125.0)


def test_zero_accuracy_means_zero_value():
    wrong = ValueInputs(
        volume=2000, baseline_minutes=12.0, loaded_hourly_rate=45.0,
        containment_rate=0.5, accuracy=0.0, assisted_time_saving=0.25)
    assert value_breakdown(wrong).gross == 0.0


def test_perfect_accuracy_recovers_full_modelled_value():
    perfect = ValueInputs(
        volume=2000, baseline_minutes=12.0, loaded_hourly_rate=45.0,
        containment_rate=0.5, accuracy=1.0, assisted_time_saving=0.25)
    assert value_breakdown(perfect).gross == pytest.approx(9000.0 + 2250.0)


def test_zero_containment_still_earns_assisted_value():
    helper_only = ValueInputs(
        volume=2000, baseline_minutes=12.0, loaded_hourly_rate=45.0,
        containment_rate=0.0, accuracy=1.0, assisted_time_saving=0.25)
    b = value_breakdown(helper_only)
    assert b.contained_value == 0.0
    assert b.assisted_value == pytest.approx(2000 * 9.0 * 0.25)


def test_full_containment_earns_no_assisted_value():
    solo = ValueInputs(
        volume=2000, baseline_minutes=12.0, loaded_hourly_rate=45.0,
        containment_rate=1.0, accuracy=1.0, assisted_time_saving=0.25)
    b = value_breakdown(solo)
    assert b.assisted_value == 0.0
    assert b.gross == pytest.approx(18000.0)


def test_zero_volume_is_zero_value():
    empty = ValueInputs(
        volume=0, baseline_minutes=12.0, loaded_hourly_rate=45.0,
        containment_rate=0.5, accuracy=0.9, assisted_time_saving=0.25)
    assert value_breakdown(empty).gross == 0.0
    assert total_baseline_cost(empty) == 0.0


def test_no_time_saving_means_no_assisted_value():
    b = value_breakdown(ValueInputs(
        volume=2000, baseline_minutes=12.0, loaded_hourly_rate=45.0,
        containment_rate=0.5, accuracy=0.9, assisted_time_saving=0.0))
    assert b.assisted_value == 0.0


def test_accuracy_above_one_rejected():
    with pytest.raises(ValueError):
        ValueInputs(volume=1, baseline_minutes=1.0, loaded_hourly_rate=1.0,
                    containment_rate=0.5, accuracy=1.1)


def test_negative_volume_rejected():
    with pytest.raises(ValueError):
        ValueInputs(volume=-5, baseline_minutes=1.0, loaded_hourly_rate=1.0,
                    containment_rate=0.5, accuracy=0.5)
