"""单期逾期罚息模块。

罚息 = 该期月供 × 日罚率 × 超出免罚天数的天数
超出免罚天数 = max(0, 逾期天数 - 免罚天数)
"""


def chargeable_days(overdue_days: int, grace_days: int) -> int:
    return max(0, int(overdue_days) - int(grace_days))


def penalty_amount(period_payment: float, overdue_days: int, grace_days: int, daily_rate: float) -> float:
    days = chargeable_days(overdue_days, grace_days)
    return round(float(period_payment) * float(daily_rate) * days, 2)


def apply_penalty(period_payment: float, overdue_days: int, grace_days: int, daily_rate: float) -> dict:
    days = chargeable_days(overdue_days, grace_days)
    penalty = penalty_amount(period_payment, overdue_days, grace_days, daily_rate)
    return {
        "base_monthly_payment": round(float(period_payment), 2),
        "chargeable_days": days,
        "penalty": penalty,
        "payment_with_penalty": round(float(period_payment) + penalty, 2),
    }
