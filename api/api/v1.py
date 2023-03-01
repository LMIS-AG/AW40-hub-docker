from fastapi import FastAPI
from .routers import health

api_v1 = FastAPI(
    title="AW4.0 Hub - API",
    version="1"
)

api_v1.include_router(health.router, prefix="/health")
