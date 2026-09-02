from fastapi import APIRouter
from app.api.v1.endpoints import appointments, auth, health, health_library, journey

api_v1_router = APIRouter()

# Register core endpoints
api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(journey.router, prefix="/journey", tags=["My Journey"])
api_v1_router.include_router(health_library.router, prefix="/health-library", tags=["Health Library"])
api_v1_router.include_router(health_library.router, prefix="/library", tags=["Health Library"])
api_v1_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
