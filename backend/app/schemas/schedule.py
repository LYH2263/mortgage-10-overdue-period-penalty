from pydantic import BaseModel, Field


class ScheduleRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    loan_id: int | None = None
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=120)
    overdue_period: int | None = Field(default=None, ge=1)
    overdue_days: int | None = Field(default=None, ge=0)


class PenaltyRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    grace_days: int = Field(ge=0, le=365)
    daily_rate: float = Field(ge=0)
    enabled: bool = True


class PenaltyRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    grace_days: int | None = Field(default=None, ge=0, le=365)
    daily_rate: float | None = Field(default=None, ge=0)
    enabled: bool | None = None
