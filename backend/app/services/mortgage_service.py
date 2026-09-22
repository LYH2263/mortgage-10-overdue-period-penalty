from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.modules.late_penalty import apply_penalty
from app.repositories import loans, runs, settings
from app.repositories import late_penalty as penalty_repo


class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)

    def penalty_rules(self): return penalty_repo.list_all(self._c)
    def create_penalty_rule(self, name, grace_days, daily_rate, enabled):
        return penalty_repo.insert(self._c, name, grace_days, daily_rate, enabled)
    def update_penalty_rule(self, rule_id, **fields):
        return penalty_repo.update(self._c, rule_id, **fields)

    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12,
                 overdue_period=None, overdue_days=None):
        full = equal_payment_schedule(principal, annual_rate, months)
        out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])

        # 逾期罚息：仅在附带逾期期序号与天数，且命中启用规则时计算。
        penalty_block = {
            "overdue_period": overdue_period,
            "overdue_days": overdue_days,
            "base_monthly_payment": out["monthly_payment"],
            "chargeable_days": 0,
            "penalty": 0.0,
            "payment_with_penalty": out["monthly_payment"],
            "rule_id": None,
            "applied": False,
        }
        if overdue_period is not None and overdue_days is not None:
            rule = penalty_repo.active(self._c)
            if rule is not None and 1 <= overdue_period <= len(full["rows"]):
                period_payment = full["rows"][overdue_period - 1]["payment"]
                calc = apply_penalty(period_payment, overdue_days, rule["grace_days"], rule["daily_rate"])
                penalty_block.update(calc)
                penalty_block["overdue_period"] = overdue_period
                penalty_block["rule_id"] = rule["id"]
                penalty_block["applied"] = True
        out["penalty"] = penalty_block

        rid = None
        if persist:
            payload = {"principal": principal, "annual_rate": annual_rate, "months": months}
            if overdue_period is not None:
                payload["overdue_period"] = overdue_period
                payload["overdue_days"] = overdue_days
            # 罚息快照随结果一并写入；之后规则日罚率变动不影响历史记录。
            rid = runs.insert(self._c, "schedule", payload, out, loan_id)
        return {"run_id": rid, **out}

    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
