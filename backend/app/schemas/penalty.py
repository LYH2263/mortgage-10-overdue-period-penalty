from pydantic import BaseModel, Field

class PenaltyRuleIn(BaseModel):
    name: str = Field(default="罚息规则", min_length=1, max_length=50)
    grace_days: int = Field(default=0, ge=0, le=365)
    daily_rate: float = Field(default=0.0, ge=0, le=100)  # 日罚率，%/日
    enabled: bool = True
