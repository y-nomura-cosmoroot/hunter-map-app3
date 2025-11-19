"""Models package."""
from app.models.schemas import (
    Point,
    GeoPoint,
    ReferencePoint,
    DetectedBox,
    TransformedBox,
    UploadResponse,
    DetectionResponse,
    TransformRequest,
    TransformResponse,
    KMLRequest,
    KMLResponse,
    ErrorResponse,
)
from app.models.errors import ERROR_MESSAGES, get_error_message

__all__ = [
    # Data models
    "Point",
    "GeoPoint",
    "ReferencePoint",
    "DetectedBox",
    "TransformedBox",
    # Request/Response models
    "UploadResponse",
    "DetectionResponse",
    "TransformRequest",
    "TransformResponse",
    "KMLRequest",
    "KMLResponse",
    "ErrorResponse",
    # Error utilities
    "ERROR_MESSAGES",
    "get_error_message",
]
