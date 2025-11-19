"""KML file generation and download API endpoints."""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from app.models.schemas import KMLRequest, KMLResponse, ErrorResponse
from app.models.errors import get_error_message
from app.services.kml_generator import KMLGenerator
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["kml"])

# Initialize KML generator
kml_generator = KMLGenerator(output_dir=settings.upload_dir)


@router.post(
    "/generate-kml",
    response_model=KMLResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def generate_kml(request: KMLRequest) -> KMLResponse:
    """
    Generate KML file from transformed boxes.
    
    Args:
        request: KMLRequest containing file_id and transformed boxes
        
    Returns:
        KMLResponse with download_url and filename
        
    Raises:
        HTTPException: If KML generation fails
    """
    logger.info(f"Generating KML for file_id: {request.file_id}")
    logger.info(f"Number of boxes: {len(request.boxes)}")
    
    # Validate that boxes list is not empty
    if len(request.boxes) == 0:
        logger.warning("Cannot generate KML: no boxes provided")
        error_info = get_error_message("no_boxes_detected")
        error_info["message"] = "KMLファイルを生成するには少なくとも1つの赤枠が必要です"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_info
        )
    
    # Generate KML file
    try:
        kml_filepath = kml_generator.generate_kml(
            boxes=request.boxes,
            base_filename=f"red_boxes_{request.file_id}"
        )
        logger.info(f"KML file generated: {kml_filepath}")
    except ValueError as e:
        logger.error(f"KML generation failed (validation error): {str(e)}")
        error_info = get_error_message("kml_generation_failed")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_info
        )
    except Exception as e:
        logger.error(f"Unexpected error during KML generation: {str(e)}")
        error_info = get_error_message("kml_generation_failed")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    
    # Extract filename from path
    filename = Path(kml_filepath).name
    
    # Generate download URL
    download_url = f"/api/download/{filename}"
    
    logger.info(f"KML generation successful - filename: {filename}")
    
    return KMLResponse(
        download_url=download_url,
        filename=filename
    )


@router.get(
    "/download/{filename}",
    response_class=FileResponse,
    responses={
        404: {"model": ErrorResponse, "description": "File not found"}
    }
)
async def download_kml(filename: str) -> FileResponse:
    """
    Download generated KML file.
    
    Args:
        filename: Name of the KML file to download
        
    Returns:
        FileResponse with the KML file
        
    Raises:
        HTTPException: If file is not found
    """
    logger.info(f"Download request for file: {filename}")
    
    # Validate filename extension
    if not filename.endswith('.kml'):
        logger.warning(f"Invalid file extension: {filename}")
        error_info = get_error_message("file_not_found")
        error_info["message"] = "無効なファイル形式です"
        error_info["suggestion"] = "KMLファイルのみダウンロード可能です"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_info
        )
    
    # Construct file path
    file_path = Path(settings.upload_dir) / filename
    
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"KML file not found: {filename}")
        error_info = get_error_message("file_not_found")
        error_info["message"] = "KMLファイルが見つかりません"
        error_info["suggestion"] = "ファイルが削除されたか、URLが正しくない可能性があります"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_info
        )
    
    logger.info(f"Serving KML file: {filename}")
    
    # Return file with appropriate headers
    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.google-earth.kml+xml",
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
