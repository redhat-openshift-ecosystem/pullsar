from fastapi import FastAPI
from app.routers import v1
from contextlib import asynccontextmanager

from app.database import initialize_db_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_db_config()
    yield


app = FastAPI(
    title="Pullsar API",
    description="API for the Pullsar operator statistics dashboard.",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(v1.router, prefix="/v1")
