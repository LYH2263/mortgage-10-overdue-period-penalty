from fastapi import APIRouter, HTTPException
from app.schemas.penalty import PenaltyRuleIn
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/penalty-rules")
def list_rules():
    with MortgageService() as s: return {"items": s.penalty_rules()}
@router.post("/penalty-rules", status_code=201)
def create_rule(body: PenaltyRuleIn):
    with MortgageService() as s: return s.create_penalty_rule(body)
@router.put("/penalty-rules/{rid}")
def update_rule(rid: int, body: PenaltyRuleIn):
    with MortgageService() as s:
        rule = s.update_penalty_rule(rid, body)
        if not rule: raise HTTPException(404)
        return rule
@router.post("/penalty-rules/{rid}/disable")
def disable_rule(rid: int):
    with MortgageService() as s:
        rule = s.set_penalty_enabled(rid, False)
        if not rule: raise HTTPException(404)
        return rule
