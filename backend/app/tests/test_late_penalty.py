from app.modules.late_penalty import apply_penalty, chargeable_days, penalty_amount


def test_chargeable_days_within_grace():
    assert chargeable_days(3, 3) == 0
    assert chargeable_days(2, 3) == 0


def test_chargeable_days_over_grace():
    assert chargeable_days(13, 3) == 10


def test_penalty_amount():
    # 月供 4490.45，日罚率 0.0005，超免罚 10 天
    assert penalty_amount(4490.45, 13, 3, 0.0005) == round(4490.45 * 0.0005 * 10, 2)


def test_apply_penalty_block():
    block = apply_penalty(4490.45, 13, 3, 0.0005)
    assert block["base_monthly_payment"] == 4490.45
    assert block["chargeable_days"] == 10
    assert block["penalty"] == round(4490.45 * 0.0005 * 10, 2)
    assert block["payment_with_penalty"] == round(4490.45 + block["penalty"], 2)


def test_zero_penalty_within_grace_keeps_payment():
    block = apply_penalty(5000.0, 3, 3, 0.0005)
    assert block["penalty"] == 0.0
    assert block["payment_with_penalty"] == 5000.0
