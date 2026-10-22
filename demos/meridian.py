"""Fictional demo data: one invented retailer, four agent use cases.

Cinder Peak Outfitters is a made-up mid-size outdoor retailer used
across this portfolio's demos. Every figure below -- volumes, handling
times, wages, containment rates, model prices -- is invented for the
demo and labelled fictional wherever it is reported. The shape is the
point: two mature use cases that clearly pay, one that pays only if the
estimates hold, and one that loses money at its current scale.

Period is one month throughout.
"""
from roi.compute import UseCase
from roi.intake import Candidate

COMPANY = "Cinder Peak Outfitters (fictional)"

USE_CASES = [
    UseCase(
        name="Support triage",
        volume=18000,
        baseline_minutes=9.0,
        loaded_hourly_rate=38.0,
        containment_rate=0.62,
        accuracy=0.93,
        assisted_time_saving=0.35,
        avg_cost_per_request=0.11,
        infra_monthly=420.0,
        review_minutes=6.0,
        escalation_share=0.50,
        build_cost=48000.0,
    ),
    UseCase(
        name="Order status",
        volume=26000,
        baseline_minutes=4.0,
        loaded_hourly_rate=38.0,
        containment_rate=0.85,
        accuracy=0.97,
        assisted_time_saving=0.25,
        avg_cost_per_request=0.05,
        infra_monthly=300.0,
        review_minutes=3.0,
        escalation_share=0.40,
        build_cost=30000.0,
    ),
    UseCase(
        name="Returns handling",
        volume=7500,
        baseline_minutes=14.0,
        loaded_hourly_rate=38.0,
        containment_rate=0.45,
        accuracy=0.88,
        assisted_time_saving=0.30,
        avg_cost_per_request=0.16,
        infra_monthly=380.0,
        review_minutes=12.0,
        escalation_share=0.60,
        build_cost=85000.0,
    ),
    UseCase(
        name="Internal IT help",
        volume=2200,
        baseline_minutes=18.0,
        loaded_hourly_rate=52.0,
        containment_rate=0.30,
        accuracy=0.81,
        assisted_time_saving=0.20,
        avg_cost_per_request=0.22,
        infra_monthly=350.0,
        review_minutes=12.0,
        escalation_share=0.70,
        build_cost=55000.0,
    ),
]

CANDIDATES = [
    Candidate(
        name="Product questions on the catalogue",
        monthly_volume=21000,
        baseline_minutes=5.0,
        containment_plausibility=0.70,
        data_readiness=0.85,
        risk=0.35,
        complexity=0.35,
    ),
    Candidate(
        name="Warranty claim intake",
        monthly_volume=3200,
        baseline_minutes=16.0,
        containment_plausibility=0.55,
        data_readiness=0.70,
        risk=0.40,
        complexity=0.60,
    ),
    Candidate(
        name="Shift-swap helper for store staff",
        monthly_volume=900,
        baseline_minutes=6.0,
        containment_plausibility=0.50,
        data_readiness=0.50,
        risk=0.30,
        complexity=0.80,
    ),
]
