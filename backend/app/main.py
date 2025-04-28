from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
import logging
from sqlalchemy.orm import Session
from logging.handlers import RotatingFileHandler
from app.api.api import api_router
from app.core.security import get_current_user
from app.api import deps
from sqlalchemy import text
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

from dotenv import load_dotenv
import os

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API pour l'application BerinIA",
    version="0.1.0",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# Exception handler middleware
@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal Server Error: {str(e)}"}
        )

# Configuration CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Inclure les routers API
app.include_router(api_router, prefix="/api")

# Route de base
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API BerinIA"}

@app.get("/debug/routes")
def list_routes():
    return [{"path": route.path, "name": route.name} for route in app.routes]

# Créer les tables dans la base de données
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)