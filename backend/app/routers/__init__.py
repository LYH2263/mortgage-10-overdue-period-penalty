from fastapi import APIRouter
from app.routers import dashboard, history, loans, schedule, settings, penalty_rules
api = APIRouter(prefix="/api")
for r in (dashboard, loans, schedule, history, settings, penalty_rules): api.include_router(r.router)
