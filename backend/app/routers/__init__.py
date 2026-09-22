from fastapi import APIRouter
from app.routers import dashboard, history, loans, penalty, schedule, settings
api = APIRouter(prefix="/api")
for r in (dashboard, loans, schedule, history, settings, penalty): api.include_router(r.router)
