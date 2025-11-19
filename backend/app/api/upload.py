"""File upload API endpoint."""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from app.models.schemas import UploadResponse, ErrorResponse
from app.models.errors import get_error_message
from app.services.pdf_processor import PDFProcessor
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

# Initialize PDF processor
pdf_processor = PDFProcessor()

# Allowed MIME types for PDF files
ALLOWED_MIME_TYPES = ["application/pdf"]
ALLOWED_EXTENSIONS = [".pdf"]


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file format or size"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a PDF file and convert it to an image.
    
    Args:
        file: PDF file uploaded via multipart/form-data
        
    Returns:
        UploadResponse with file_id, image_url, width, and height
        
    Raises:
        HTTPException: If file validation fails or processing error occurs
    """
    logger.info(f"Received file upload: {file.filename}")
    
    # Validate file format by extension
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Invalid file extension: {file_ext}")
        error_info = get_error_message("invalid_file_format")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_info
        )
    
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning(f"Invalid MIME type: {file.content_type}")
        error_info = get_error_message("invalid_file_format")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_info
        )
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {str(e)}")
        error_info = get_error_message("internal_error")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    
    # Validate file size
    file_size = len(file_content)
    logger.info(f"File size: {file_size} bytes")
    
    if file_size > settings.max_file_size:
        logger.warning(f"File size exceeds limit: {file_size} > {settings.max_file_size}")
        error_info = get_error_message("file_too_large")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_info
        )
    
    # Save uploaded file
    try:
        file_id, pdf_path = pdf_processor.save_uploaded_file(
            file_content,
            file.filename or "upload.pdf"
        )
        logger.info(f"File saved with ID: {file_id}")
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {str(e)}")
        error_info = get_error_message("internal_error")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    
    # Convert PDF to image
    try:
        image_path = pdf_processor.convert_pdf_to_image(pdf_path)
        logger.info(f"PDF converted to image: {image_path}")
    except FileNotFoundError as e:
        logger.error(f"PDF file not found: {str(e)}")
        error_info = get_error_message("file_not_found")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_info
        )
    except ValueError as e:
        logger.error(f"PDF conversion failed: {str(e)}")
        error_info = get_error_message("pdf_conversion_failed")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_info
        )
    except Exception as e:
        logger.error(f"Unexpected error during PDF conversion: {str(e)}")
        error_info = get_error_message("internal_error")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    
    # Get image dimensions
    try:
        width, height = pdf_processor.get_image_dimensions(image_path)
        logger.info(f"Image dimensions: {width}x{height}")
    except Exception as e:
        logger.error(f"Failed to get image dimensions: {str(e)}")
        error_info = get_error_message("image_processing_failed")
        error_info["details"] = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info
        )
    
    # Generate image URL (relative path)
    image_filename = Path(image_path).name
    image_url = f"/api/images/{image_filename}"
    
    logger.info(f"Upload successful - file_id: {file_id}, image_url: {image_url}")
    
    return UploadResponse(
        file_id=file_id,
        image_url=image_url,
        width=width,
        height=height
    )



@router.get(
    "/images/{filename}",
    response_class=FileResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Image not found"}
    }
)
async def get_image(filename: str) -> FileResponse:
    """
    Serve converted image files.
    
    Args:
        filename: Name of the image file
        
    Returns:
        FileResponse with the image file
        
    Raises:
        HTTPException: If image file is not found
    """
    image_path = Path(settings.upload_dir) / filename
    
    if not image_path.exists() or not image_path.is_file():
        logger.warning(f"Image not found: {filename}")
        error_info = get_error_message("file_not_found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_info
        )
    
    return FileResponse(
        path=str(image_path),
        media_type="image/png",
        filename=filename
    )
