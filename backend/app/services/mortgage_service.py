from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.engines.penalty import overdue_penalty
from app.repositories import loans, penalty_rules, runs, settings

def _rule_out(row):
    return {**row, "enabled": bool(row["enabled"])} if row else None

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def penalty_rules(self): return [_rule_out(r) for r in penalty_rules.list_all(self._c)]
    def create_penalty_rule(self, body):
        return _rule_out(penalty_rules.create(self._c, body.name, body.grace_days, body.daily_rate, body.enabled))
    def update_penalty_rule(self, rid, body):
        return _rule_out(penalty_rules.update(self._c, rid, body.name, body.grace_days, body.daily_rate, body.enabled))
    def set_penalty_enabled(self, rid, enabled):
        return _rule_out(penalty_rules.set_enabled(self._c, rid, enabled))
    def _penalty(self, full, overdue):
        if not overdue:
            return {"period": None, "days": 0, "base_payment": full["monthly_payment"],
                    "penalty": 0.0, "payment_with_penalty": full["monthly_payment"],
                    "rule_id": None, "applied": False}
        base = full["rows"][overdue.period - 1]["payment"]
        rule = penalty_rules.active(self._c)
        amount = overdue_penalty(base, rule["daily_rate"], overdue.days, rule["grace_days"]) if rule else 0.0
        return {"period": overdue.period, "days": overdue.days, "base_payment": base,
                "penalty": amount, "payment_with_penalty": round(base + amount, 2),
                "rule_id": rule["id"] if rule else None, "applied": rule is not None}
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12, overdue=None):
        full = equal_payment_schedule(principal, annual_rate, months)
        out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        out["penalty"] = self._penalty(full, overdue)
        rid = None
        if persist:
            payload = {"principal": principal, "annual_rate": annual_rate, "months": months}
            if overdue: payload["overdue"] = {"period": overdue.period, "days": overdue.days}
            rid = runs.insert(self._c, "schedule", payload, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
