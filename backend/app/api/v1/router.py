from fastapi import APIRouter
from app.api.v1.endpoints import appointments, auth, care, health, health_library, journey, voice

api_v1_router = APIRouter()

# Register core endpoints
api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(journey.router, prefix="/journey", tags=["My Journey"])
api_v1_router.include_router(health_library.router, prefix="/health-library", tags=["Health Library"])
api_v1_router.include_router(health_library.router, prefix="/library", tags=["Health Library"])
api_v1_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_v1_router.include_router(care.router, prefix="/care", tags=["Baby & Parent Care"])
api_v1_router.include_router(care.router, prefix="/baby-care", tags=["Baby & Parent Care"])
api_v1_router.include_router(voice.router, prefix="/voice", tags=["Voice Journey"])
