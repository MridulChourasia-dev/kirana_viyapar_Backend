"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.openapi_docs import TAGS_METADATA

# ─────────────────────────────────────────
# FastAPI Application Setup
# ─────────────────────────────────────────

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_tags=TAGS_METADATA,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# ─────────────────────────────────────────
# Middleware Setup
# ─────────────────────────────────────────

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# Health Check Endpoints
# ─────────────────────────────────────────


@app.get("/", tags=["root"], summary="Welcome")
async def root():
    """Root endpoint - returns API information"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "api_docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health", tags=["health"], summary="Health Check")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION}


# ─────────────────────────────────────────
# API Router
# ─────────────────────────────────────────

app.include_router(api_router, prefix=settings.API_V1_STR)

# ─────────────────────────────────────────
# Application Entry Point
# ─────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )
