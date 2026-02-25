from fastapi import APIRouter

from app.api.v1.endpoints import auth, history, incidents, interventions, scenarios, simulation, users

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(scenarios.router)
api_router.include_router(incidents.router, tags=["incidents"])
api_router.include_router(interventions.router)
api_router.include_router(simulation.router, tags=["simulation"])
api_router.include_router(history.router)
