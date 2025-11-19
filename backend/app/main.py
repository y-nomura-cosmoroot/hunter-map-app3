"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import settings
from app.utils.logging_config import setup_logging, get_logger
from app.api.upload import router as upload_router
from app.api.detection import router as detection_router
from app.api.transform import router as transform_router
from app.api.kml import router as kml_router

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)
app.include_router(detection_router)
app.include_router(transform_router)
app.include_router(kml_router)

# Create necessary directories
upload_dir = Path(settings.upload_dir)
upload_dir.mkdir(exist_ok=True)
logger.info(f"Upload directory created: {upload_dir.absolute()}")


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Max file size: {settings.max_file_size} bytes")
    logger.info(f"File TTL: {settings.file_ttl} seconds")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info(f"Shutting down {settings.app_name}")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "PDF Red Box KML Converter API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
