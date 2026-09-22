from pydantic import BaseModel, Field, model_validator

class OverdueInput(BaseModel):
    period: int = Field(gt=0)  # 逾期期序号
    days: int = Field(ge=0)    # 逾期天数

class ScheduleRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    loan_id: int | None = None
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=120)
    overdue: OverdueInput | None = None

    @model_validator(mode="after")
    def _overdue_within_term(self):
        if self.overdue and self.overdue.period > self.months:
            raise ValueError("overdue.period exceeds months")
        return self
