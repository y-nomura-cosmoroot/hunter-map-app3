"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal


class Point(BaseModel):
    """Image coordinate point (pixels)."""
    x: float
    y: float


class GeoPoint(BaseModel):
    """Geographic coordinate point (latitude/longitude)."""
    lat: float = Field(ge=-90, le=90, description="Latitude in degrees")
    lng: float = Field(ge=-180, le=180, description="Longitude in degrees")


class ReferencePoint(BaseModel):
    """Reference point mapping image coordinates to geographic coordinates."""
    model_config = {"populate_by_name": True}
    
    image_point: Point = Field(alias="imagePoint")
    geo_point: GeoPoint = Field(alias="geoPoint")
    id: str


class DetectedBox(BaseModel):
    """Detected red box in the PDF image."""
    model_config = {"populate_by_name": True}
    
    id: str
    corners: List[Point] = Field(min_length=3)
    center: Point
    box_type: Literal["thick_border", "filled_area"] = Field(alias="boxType")
    
    @field_validator("corners")
    @classmethod
    def validate_corners(cls, v):
        """Validate that at least 3 corners are provided."""
        if len(v) < 3:
            raise ValueError("At least 3 corners are required")
        return v


class TransformedBox(BaseModel):
    """Red box with transformed geographic coordinates."""
    id: str
    corners: List[GeoPoint] = Field(min_length=3)
    center: GeoPoint
    
    @field_validator("corners")
    @classmethod
    def validate_corners(cls, v):
        """Validate that at least 3 corners are provided."""
        if len(v) < 3:
            raise ValueError("At least 3 corners are required")
        return v


# Request/Response Models

class UploadResponse(BaseModel):
    """Response for PDF upload."""
    file_id: str
    image_url: str
    width: int
    height: int


class DetectionResponse(BaseModel):
    """Response for red box detection."""
    boxes: List[DetectedBox]
    count: int


class TransformRequest(BaseModel):
    """Request for coordinate transformation."""
    model_config = {"populate_by_name": True}
    
    file_id: str = Field(alias="file_id")
    reference_points: List[ReferencePoint] = Field(min_length=3, alias="reference_points")
    boxes: List[str]  # box IDs to transform
    
    @field_validator("reference_points")
    @classmethod
    def validate_reference_points(cls, v):
        """Validate that at least 3 reference points are provided."""
        if len(v) < 3:
            raise ValueError("最低3つの基準点が必要です")
        return v


class TransformResponse(BaseModel):
    """Response for coordinate transformation."""
    transformed_boxes: List[TransformedBox]
    map_scale: float
    warnings: List[str] = []


class KMLRequest(BaseModel):
    """Request for KML file generation."""
    file_id: str
    boxes: List[TransformedBox]


class KMLResponse(BaseModel):
    """Response for KML file generation."""
    download_url: str
    filename: str


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: str = ""
    suggestion: str = ""
