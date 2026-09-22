import pytest
from app.engines.amortization import equal_payment_schedule
from app.engines.penalty import overdue_penalty

def test_monthly_payment():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["monthly_payment"] == 4490.45

def test_first_period_interest():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["rows"][0]["interest"] == 2916.67
    assert s["rows"][0]["period"] == 1

def test_zero_rate():
    s = equal_payment_schedule(120000, 0, 12)
    assert s["monthly_payment"] == 10000.0

def test_bad_months():
    with pytest.raises(ValueError):
        equal_payment_schedule(100, 3, 0)

def test_penalty_basic():
    assert overdue_penalty(4490.45, 0.05, 10, 0) == 22.45

def test_penalty_only_days_beyond_grace():
    assert overdue_penalty(4490.45, 0.05, 13, 10) == round(4490.45 * 0.0005 * 3, 2)

def test_penalty_within_grace_is_zero():
    assert overdue_penalty(4490.45, 0.05, 10, 10) == 0.0
    assert overdue_penalty(4490.45, 0.05, 3, 10) == 0.0

def test_penalty_zero_rate_or_days():
    assert overdue_penalty(4490.45, 0.0, 30, 0) == 0.0
    assert overdue_penalty(4490.45, 0.05, 0, 0) == 0.0
