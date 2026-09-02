from fastapi import APIRouter
from app.api.v1.endpoints import auth, health

api_v1_router = APIRouter()

# Register core health and authentication routers
api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
