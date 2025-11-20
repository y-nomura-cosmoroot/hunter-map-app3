"""Red box and blue box detection API endpoint."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from pathlib import Path
import logging
import json

from app.models.schemas import DetectionResponse, ErrorResponse
from app.models.errors import get_error_message
from app.services.red_box_detector import RedBoxDetector
from app.services.blue_box_detector import BlueBoxDetector
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["detection"])

# Initialize detectors
red_box_detector = RedBoxDetector()
blue_box_detector = BlueBoxDetector()


class DetectionRequest(BaseModel):
    """Request model for red box detection."""
    file_id: str


@router.post(
    "/detect-boxes",
    response_model=DetectionResponse,
    responses={
        404: {"model": ErrorResponse, "description": "File not found"},
        400: {"model": ErrorResponse, "description": "No boxes detected"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def detect_boxes(request: DetectionRequest) -> DetectionResponse:
    """
    Detect red boxes in the uploaded PDF image.
    
    Args:
        request: DetectionRequest containing file_id
        
    Returns:
        DetectionResponse with detected boxes and count
        
    Raises:
        HTTPException: If file is not found or detection fails
    """
    logger.info(f"Detecting red boxes for file_id: {request.file_id}")
    
    # Construct image file path
    # The image file should be in the upload directory with .png extension
    image_filename = f"{request.file_id}.png"
    image_path = Path(settings.upload_dir) / image_filename
    
    # Check if file exists
    if not image_path.exists() or not image_path.is_file():
        logger.warning(f"Image file not found: {image_path}")
        error_info = get_error_message("file_not_found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_info
        )
    
    # Detect red boxes and blue boxes
    try:
        red_boxes = red_box_detector.detect_red_boxes(str(image_path))
        logger.info(f"Detected {len(red_boxes)} red boxes")
        
        blue_boxes = blue_box_detector.detect_blue_boxes(str(image_path))
        logger.info(f"Detected {len(blue_boxes)} blue boxes")
        
        # Combine all detected boxes
        detected_boxes = red_boxes + blue_boxes
        logger.info(f"Total detected boxes: {len(detected_boxes)}")
    except FileNotFoundError as e:
        logger.error(f"File not found during detection: {str(e)}")
        error_info = get_error_message("file_not_found")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_info
        )
    except ValueError as e:
        logger.error(f"Detection failed: {str(e)}")
        error_info = get_error_message("image_processing_failed")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    except Exception as e:
        logger.error(f"Unexpected error during detection: {str(e)}")
        error_info = get_error_message("internal_error")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    
    # Check if any boxes were detected
    if len(detected_boxes) == 0:
        logger.warning("No red or blue boxes detected in the image")
        error_info = get_error_message("no_boxes_detected")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_info
        )
    
    logger.info(f"Detection successful - {len(detected_boxes)} boxes found")
    
    # Save detected boxes to JSON file for later transformation
    boxes_file_path = Path(settings.upload_dir) / f"{request.file_id}_boxes.json"
    try:
        with open(boxes_file_path, 'w', encoding='utf-8') as f:
            boxes_data = [box.model_dump() for box in detected_boxes]
            json.dump(boxes_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved detected boxes to {boxes_file_path}")
    except Exception as e:
        logger.warning(f"Failed to save detected boxes: {str(e)}")
        # Don't fail the request if saving fails
    
    return DetectionResponse(
        boxes=detected_boxes,
        count=len(detected_boxes)
    )
