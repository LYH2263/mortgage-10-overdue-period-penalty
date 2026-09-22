from fastapi import APIRouter, HTTPException
from app.schemas.schedule import PenaltyRuleCreate, PenaltyRuleUpdate
from app.services.mortgage_service import MortgageService

router = APIRouter(prefix="/penalty-rules")


@router.get("")
def list_rules():
    with MortgageService() as s:
        return {"items": s.penalty_rules()}


@router.post("")
def create_rule(body: PenaltyRuleCreate):
    with MortgageService() as s:
        return s.create_penalty_rule(body.name, body.grace_days, body.daily_rate, body.enabled)


@router.put("/{rule_id}")
def update_rule(rule_id: int, body: PenaltyRuleUpdate):
    fields = body.model_dump(exclude_none=True)
    with MortgageService() as s:
        row = s.update_penalty_rule(rule_id, **fields)
        if not row:
            raise HTTPException(404)
        return row


@router.post("/{rule_id}/disable")
def disable_rule(rule_id: int):
    with MortgageService() as s:
        row = s.update_penalty_rule(rule_id, enabled=False)
        if not row:
            raise HTTPException(404)
        return row
