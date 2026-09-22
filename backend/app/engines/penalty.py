def overdue_penalty(base_payment: float, daily_rate: float, days: int, grace_days: int) -> float:
    """单期逾期罚息：该期月供 × 日罚率(%) × 超出免罚的天数。"""
    extra = max(0, int(days) - int(grace_days))
    if extra <= 0 or daily_rate <= 0 or base_payment <= 0:
        return 0.0
    return round(float(base_payment) * float(daily_rate) / 100.0 * extra, 2)
