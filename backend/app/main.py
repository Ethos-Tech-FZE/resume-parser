"""
FastAPI application entry point for ResuMate API.

This module initializes the FastAPI application with CORS middleware,
includes all API routers, and defines health check endpoints.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import db_manager, get_db
from app.api import resumes, shares
from app.api.websocket import manager

# Setup logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    
    This function manages the application startup and shutdown lifecycle:
    - Startup: Initializes the database engine
    - Shutdown: Closes database connections
    
    This ensures the database is ready before handling any requests,
    which is critical for local development and production deployments.
    
    For Vercel serverless deployments, the lifespan handler is ignored
    (lifespan="off" in Mangum), so lazy initialization is still used.
    
    Yields:
        None: Control is yielded to the application during its lifetime
    """
    # Startup: Initialize database
    logger.info("🚀 Application startup - Initializing database engine...")
    try:
        db_manager.init_engine(echo=settings.is_development)
        logger.info("✅ Database engine initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        # Don't raise - allow app to start in degraded mode
        # Health check will show database as disconnected
    
    yield
    
    # Shutdown: Close database connections
    logger.info("🛑 Application shutdown - Closing database connections...")
    try:
        await db_manager.close()
        logger.info("✅ Database connections closed successfully")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


# Create FastAPI application instance with lifespan manager
app = FastAPI(
    title="ResuMate API",
    description="Smart Resume Parser API",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,  # ← Add lifespan manager
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(resumes.router)
app.include_router(shares.router)


@app.websocket("/ws/resumes/{resume_id}")
async def websocket_endpoint(websocket: WebSocket, resume_id: str):
    """
    WebSocket endpoint for real-time resume parsing updates.

    This endpoint establishes a WebSocket connection for a specific resume
    and maintains it for the duration of the parsing operation, sending
    real-time progress updates to the client.

    Args:
        websocket: The WebSocket connection instance
        resume_id: The unique identifier for the resume being processed
    """
    await manager.connect(websocket, resume_id)
    try:
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Handle any client messages (like ping/pong)
            if data == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "message": "alive"},
                    websocket,
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket, resume_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, resume_id)


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns system status including database connectivity.
    This endpoint is used by Render, load balancers, and monitoring systems
    to verify the API is running and healthy.

    Implements graceful degradation - returns 200 OK even if database is
    unavailable, allowing the service to be monitored during outages.

    Returns:
        JSONResponse: Health status with database connectivity check

    Status Codes:
        200: System is running (database connected or degraded)
    """
    from sqlalchemy import text
    from fastapi.responses import JSONResponse
    from datetime import datetime

    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "unknown",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Check database connectivity (optional - don't crash if unavailable)
    try:
        # Try to get a database session using lazy initialization
        from app.core.database import get_session_factory

        factory = get_session_factory()
        async with factory() as db:
            # Simple query to verify database connection
            await db.execute(text("SELECT 1"))
            health_status["database"] = "connected"
    except Exception as e:
        # Database is unavailable, but service is still running
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"  # Not "unhealthy" - service is running!
        health_status["database_error"] = str(e)
        logger.warning(f"Health check: database unavailable - {e}")

    # Always return 200 - the service is running, even if degraded
    return JSONResponse(content=health_status, status_code=200)
