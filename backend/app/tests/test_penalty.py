import json
import os
import tempfile
from types import SimpleNamespace

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="mortgage-penalty-test-"))

import pytest

from app import seed
from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.services.mortgage_service import MortgageService

seed.init_db()

RULE = SimpleNamespace(name="测试规则", grace_days=0, daily_rate=0.05, enabled=True)


@pytest.fixture(autouse=True)
def clean_tables():
    c = connect()
    c.execute("DELETE FROM penalty_rules")
    c.execute("DELETE FROM calc_runs")
    c.execute("INSERT INTO penalty_rules(name,grace_days,daily_rate,enabled) VALUES ('测试规则',0,0.05,1)")
    c.commit()
    c.close()
    yield


def _overdue(period=1, days=10):
    return SimpleNamespace(period=period, days=days)


def test_penalty_hit_enabled_rule():
    with MortgageService() as s:
        out = s.schedule(1_000_000, 3.5, 360, None, False, overdue=_overdue(1, 10))
    assert out["monthly_payment"] == 4490.45
    p = out["penalty"]
    assert p["base_payment"] == 4490.45
    assert p["penalty"] == 22.45
    assert p["payment_with_penalty"] == 4512.9
    assert p["applied"] is True
    assert p["rule_id"] == 1


def test_penalty_respects_grace_days():
    with MortgageService() as s:
        s.update_penalty_rule(1, SimpleNamespace(name="测试规则", grace_days=10, daily_rate=0.05, enabled=True))
        within = s.schedule(1_000_000, 3.5, 360, None, False, overdue=_overdue(1, 10))
        beyond = s.schedule(1_000_000, 3.5, 360, None, False, overdue=_overdue(1, 13))
    assert within["penalty"]["penalty"] == 0.0
    assert within["penalty"]["payment_with_penalty"] == within["penalty"]["base_payment"]
    assert beyond["penalty"]["penalty"] == round(4490.45 * 0.0005 * 3, 2)


def test_penalty_uses_that_periods_payment():
    last_payment = equal_payment_schedule(1_000_000, 3.5, 360)["rows"][-1]["payment"]
    with MortgageService() as s:
        out = s.schedule(1_000_000, 3.5, 360, None, False, overdue=_overdue(360, 10))
    assert out["penalty"]["base_payment"] == last_payment
    assert out["penalty"]["penalty"] == round(last_payment * 0.0005 * 10, 2)


def test_disabled_rule_zero_penalty_and_unchanged_payment():
    with MortgageService() as s:
        s.set_penalty_enabled(1, False)
        out = s.schedule(1_000_000, 3.5, 360, None, False, overdue=_overdue(1, 30))
        plain = s.schedule(1_000_000, 3.5, 360, None, False)
    assert out["penalty"]["penalty"] == 0.0
    assert out["penalty"]["applied"] is False
    assert out["penalty"]["payment_with_penalty"] == out["penalty"]["base_payment"]
    assert out["monthly_payment"] == plain["monthly_payment"] == 4490.45


def test_no_overdue_zero_penalty():
    with MortgageService() as s:
        out = s.schedule(1_000_000, 3.5, 360, None, False)
    assert out["penalty"]["penalty"] == 0.0
    assert out["penalty"]["period"] is None
    assert out["monthly_payment"] == 4490.45


def test_persist_false_writes_nothing():
    with MortgageService() as s:
        before = len(s.history(100))
        out = s.schedule(1_000_000, 3.5, 360, None, False, overdue=_overdue(1, 10))
        after = len(s.history(100))
    assert out["run_id"] is None
    assert after == before


def test_persisted_penalty_is_snapshot_immune_to_rate_raise():
    with MortgageService() as s:
        out = s.schedule(1_000_000, 3.5, 360, None, True, overdue=_overdue(1, 10))
        assert out["penalty"]["penalty"] == 22.45
        s.update_penalty_rule(1, SimpleNamespace(name="测试规则", grace_days=0, daily_rate=0.5, enabled=True))
        stored = [h for h in s.history(100) if h["id"] == out["run_id"]][0]
        result = json.loads(stored["result_json"])
        assert result["penalty"]["penalty"] == 22.45
        assert result["penalty"]["payment_with_penalty"] == 4512.9
        fresh = s.schedule(1_000_000, 3.5, 360, None, False, overdue=_overdue(1, 10))
        assert fresh["penalty"]["penalty"] == 224.52
