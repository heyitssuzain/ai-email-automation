from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.database.init_db import init_database


setup_logging()
init_database()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": settings.APP_NAME,
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }