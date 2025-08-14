from fastapi import FastAPI
from app.routers import v1

app = FastAPI(
    title="Pullsar API",
    description="API for the Pullsar operator statistics dashboard.",
    version="0.1.0",
)

app.include_router(v1.router, prefix="/v1")
