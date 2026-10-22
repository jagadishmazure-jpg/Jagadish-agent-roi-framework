"""Intake gate: ranking, verdicts, and the blunt poor-candidate marker."""
import pytest

from demos.meridian import CANDIDATES
from roi.intake import Candidate, is_poor, rank_candidates, score_candidate

BY_NAME = {c.name: c for c in CANDIDATES}


def test_demo_ranking_order():
    ranked = rank_candidates(CANDIDATES)
    assert [s.candidate.name for s in ranked] == [
        "Product questions on the catalogue",
        "Warranty claim intake",
        "Shift-swap helper for store staff",
    ]


def test_scores_are_in_bounds_and_descending():
    ranked = rank_candidates(CANDIDATES)
    scores = [s.score for s in ranked]
    assert all(0.0 <= s <= 100.0 for s in scores)
    assert scores == sorted(scores, reverse=True)


def test_low_volume_high_complexity_is_marked_poor():
    shift_swap = BY_NAME["Shift-swap helper for store staff"]
    scored = score_candidate(shift_swap)
    assert is_poor(shift_swap) is True
    assert scored.poor is True
    assert scored.verdict == "poor"
    assert any("marked poor" in reason for reason in scored.reasons)


def test_high_volume_high_complexity_is_not_poor():
    big_hard = Candidate(
        name="Big and hard", monthly_volume=25000, baseline_minutes=15.0,
        containment_plausibility=0.5, data_readiness=0.6, risk=0.4, complexity=0.95)
    scored = score_candidate(big_hard)
    assert scored.poor is False
    assert scored.verdict != "poor"


def test_low_volume_low_complexity_is_not_poor():
    small_easy = Candidate(
        name="Small and easy", monthly_volume=800, baseline_minutes=8.0,
        containment_plausibility=0.6, data_readiness=0.8, risk=0.2, complexity=0.3)
    assert score_candidate(small_easy).poor is False


def test_warranty_candidate_is_viable_not_poor():
    scored = score_candidate(BY_NAME["Warranty claim intake"])
    assert scored.verdict == "viable"
    assert scored.poor is False


def test_catalogue_candidate_is_strong():
    scored = score_candidate(BY_NAME["Product questions on the catalogue"])
    assert scored.verdict == "strong"
    assert scored.score >= 65


def test_every_demo_candidate_gets_reasons():
    for scored in rank_candidates(CANDIDATES):
        assert scored.reasons, scored.candidate.name


def test_perfect_candidate_scores_near_the_top():
    ideal = Candidate(
        name="Ideal", monthly_volume=50000, baseline_minutes=30.0,
        containment_plausibility=1.0, data_readiness=1.0, risk=0.0, complexity=0.1)
    assert score_candidate(ideal).score == pytest.approx(100.0)


def test_worst_candidate_scores_near_zero():
    worst = Candidate(
        name="Worst", monthly_volume=0, baseline_minutes=0.0,
        containment_plausibility=0.0, data_readiness=0.0, risk=1.0, complexity=0.5)
    scored = score_candidate(worst)
    assert scored.score == pytest.approx(0.0)
    assert scored.verdict == "weak"


def test_ranking_is_stable_for_ties():
    twin_a = Candidate(
        name="Twin A", monthly_volume=5000, baseline_minutes=10.0,
        containment_plausibility=0.5, data_readiness=0.5, risk=0.5, complexity=0.5)
    twin_b = Candidate(
        name="Twin B", monthly_volume=5000, baseline_minutes=10.0,
        containment_plausibility=0.5, data_readiness=0.5, risk=0.5, complexity=0.5)
    ranked = rank_candidates([twin_a, twin_b])
    assert [s.candidate.name for s in ranked] == ["Twin A", "Twin B"]


def test_risk_above_one_rejected():
    with pytest.raises(ValueError):
        Candidate(
            name="Bad", monthly_volume=10, baseline_minutes=1.0,
            containment_plausibility=0.5, data_readiness=0.5, risk=1.2, complexity=0.5)
