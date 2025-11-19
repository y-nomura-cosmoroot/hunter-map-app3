"""Coordinate transformation API endpoint."""
from fastapi import APIRouter, HTTPException, status
from pathlib import Path
import logging
import json

from app.models.schemas import (
    TransformRequest, 
    TransformResponse, 
    ErrorResponse,
    DetectedBox,
    TransformedBox
)
from app.models.errors import get_error_message
from app.services.geo_transformer import GeoTransformer
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["transform"])

# Initialize geo transformer
geo_transformer = GeoTransformer()


@router.post(
    "/transform",
    response_model=TransformResponse,
    responses={
        404: {"model": ErrorResponse, "description": "File not found"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def transform_coordinates(request: TransformRequest) -> TransformResponse:
    """
    Transform image coordinates to geographic coordinates.
    
    Args:
        request: TransformRequest containing file_id, reference_points, and box IDs
        
    Returns:
        TransformResponse with transformed boxes, map scale, and warnings
        
    Raises:
        HTTPException: If validation fails or transformation fails
    """
    logger.info(f"Transforming coordinates for file_id: {request.file_id}")
    logger.info(f"Reference points: {len(request.reference_points)}")
    logger.info(f"Boxes to transform: {len(request.boxes)}")
    
    warnings = []
    
    # Validate reference points count (should be caught by Pydantic, but double-check)
    if len(request.reference_points) < 3:
        logger.warning(f"Insufficient reference points: {len(request.reference_points)}")
        error_info = get_error_message(
            "insufficient_reference_points",
            count=len(request.reference_points)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_info
        )
    
    # Load detected boxes from file
    detected_boxes_path = Path(settings.upload_dir) / f"{request.file_id}_boxes.json"
    
    if not detected_boxes_path.exists():
        logger.warning(f"Detected boxes file not found: {detected_boxes_path}")
        error_info = get_error_message("file_not_found")
        error_info["details"] = "検出された赤枠データが見つかりません"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_info
        )
    
    # Load detected boxes
    try:
        with open(detected_boxes_path, 'r', encoding='utf-8') as f:
            boxes_data = json.load(f)
        detected_boxes = [DetectedBox(**box) for box in boxes_data]
        logger.info(f"Loaded {len(detected_boxes)} detected boxes")
    except Exception as e:
        logger.error(f"Failed to load detected boxes: {str(e)}")
        error_info = get_error_message("file_not_found")
        error_info["details"] = f"赤枠データの読み込みに失敗しました: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    
    # Filter boxes by requested IDs
    boxes_to_transform = [box for box in detected_boxes if box.id in request.boxes]
    
    if len(boxes_to_transform) == 0:
        logger.warning("No boxes found matching the requested IDs")
        error_info = get_error_message("file_not_found")
        error_info["message"] = "指定された赤枠が見つかりません"
        error_info["suggestion"] = "赤枠IDを確認してください"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_info
        )
    
    logger.info(f"Found {len(boxes_to_transform)} boxes to transform")
    
    # Calculate affine transformation matrix
    try:
        affine_matrix, translation_vector = geo_transformer.calculate_affine_matrix(
            request.reference_points
        )
        logger.info("Affine transformation matrix calculated successfully")
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Affine matrix calculation failed: {error_msg}")
        
        # Check if it's a collinearity error
        if "一直線上" in error_msg:
            error_info = get_error_message("collinear_points")
            error_info["details"] = error_msg
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_info
            )
        elif "基準点" in error_msg:
            error_info = get_error_message(
                "insufficient_reference_points",
                count=len(request.reference_points)
            )
            error_info["details"] = error_msg
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_info
            )
        else:
            error_info = get_error_message("transformation_failed")
            error_info["details"] = error_msg
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_info
            )
    except Exception as e:
        logger.error(f"Unexpected error during affine matrix calculation: {str(e)}")
        error_info = get_error_message("transformation_failed")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    
    # Transform selected boxes
    transformed_boxes = []
    try:
        for box in boxes_to_transform:
            transformed_box = geo_transformer.transform_box(box)
            transformed_boxes.append(transformed_box)
            logger.debug(f"Transformed box {box.id}")
        
        logger.info(f"Successfully transformed {len(transformed_boxes)} boxes")
    except ValueError as e:
        logger.error(f"Box transformation failed: {str(e)}")
        error_info = get_error_message("transformation_failed")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    except Exception as e:
        logger.error(f"Unexpected error during box transformation: {str(e)}")
        error_info = get_error_message("transformation_failed")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    
    # Estimate map scale
    try:
        map_scale = geo_transformer.estimate_map_scale(
            request.reference_points,
            image_dpi=settings.pdf_dpi
        )
        logger.info(f"Estimated map scale: 1:{map_scale:.0f}")
    except Exception as e:
        logger.warning(f"Failed to estimate map scale: {str(e)}")
        map_scale = 0.0
        warnings.append(f"地図縮尺の推定に失敗しました: {str(e)}")
    
    # Add warning if reference points might be poorly distributed
    if len(request.reference_points) == 3:
        warnings.append("基準点が3つのみです。精度向上のため、4つ以上の基準点を推奨します")
    
    logger.info(f"Transformation complete - {len(transformed_boxes)} boxes, scale: 1:{map_scale:.0f}")
    
    return TransformResponse(
        transformed_boxes=transformed_boxes,
        map_scale=map_scale,
        warnings=warnings
    )
