"""PDF processing module for converting PDFs to images and managing temporary files."""
import os
import uuid
import time
import logging
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime, timedelta
from PIL import Image
from pdf2image import convert_from_path

from app.config import settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF to image conversion and temporary file management."""
    
    def __init__(self):
        """Initialize PDF processor with upload directory."""
        self.upload_dir = Path(settings.upload_dir)
        self.max_width = settings.max_image_width
        self.max_height = settings.max_image_height
        self.pdf_dpi = settings.pdf_dpi
        self.file_ttl = settings.file_ttl
        
        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PDF Processor initialized with upload_dir: {self.upload_dir}")
    
    def convert_pdf_to_image(self, pdf_path: str, dpi: Optional[int] = None) -> str:
        """
        Convert PDF file to image format.
        
        Args:
            pdf_path: Path to the PDF file
            dpi: DPI for conversion (default: from settings)
            
        Returns:
            Path to the converted image file
            
        Raises:
            ValueError: If PDF conversion fails
            FileNotFoundError: If PDF file doesn't exist
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        dpi = dpi or self.pdf_dpi
        
        try:
            logger.info(f"Converting PDF to image: {pdf_path} at {dpi} DPI")
            
            # Check for poppler path (Windows compatibility)
            poppler_path = None
            if os.name == 'nt':  # Windows
                # Check common locations for poppler
                possible_paths = [
                    Path(__file__).parent.parent.parent / "poppler" / "poppler-24.08.0" / "Library" / "bin",
                    Path(__file__).parent.parent.parent / "poppler" / "Library" / "bin",
                    Path(__file__).parent.parent.parent / "poppler" / "bin",
                    Path("C:/Program Files/poppler/Library/bin"),
                    Path("C:/Program Files/poppler/bin"),
                ]
                for path in possible_paths:
                    if path.exists():
                        poppler_path = str(path)
                        logger.info(f"Found poppler at: {poppler_path}")
                        break
                
                if not poppler_path:
                    logger.warning("Poppler not found in common locations. Attempting without poppler_path...")
                    logger.warning(f"Checked paths: {[str(p) for p in possible_paths]}")
            
            # Convert PDF to images (only first page)
            if poppler_path:
                images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1, poppler_path=poppler_path)
            else:
                images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
            
            if not images:
                raise ValueError("PDF conversion resulted in no images")
            
            # Get the first page
            image = images[0]
            
            # Use the same file_id from the PDF filename
            # PDF path format: upload_dir/file_id.pdf
            pdf_filename = Path(pdf_path).stem  # Get filename without extension
            image_filename = f"{pdf_filename}.png"
            image_path = self.upload_dir / image_filename
            
            # Save the image
            image.save(str(image_path), "PNG")
            logger.info(f"Image saved: {image_path}")
            
            # Resize if necessary
            resized_path = self._resize_image_if_needed(str(image_path))
            
            return resized_path
            
        except Exception as e:
            logger.error(f"Failed to convert PDF to image: {str(e)}")
            raise ValueError(f"PDF conversion failed: {str(e)}")
    
    def get_image_dimensions(self, image_path: str) -> Tuple[int, int]:
        """
        Get the dimensions of an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (width, height) in pixels
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image cannot be opened
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                logger.debug(f"Image dimensions: {width}x{height} for {image_path}")
                return width, height
        except Exception as e:
            logger.error(f"Failed to get image dimensions: {str(e)}")
            raise ValueError(f"Cannot read image dimensions: {str(e)}")
    
    def _resize_image_if_needed(self, image_path: str) -> str:
        """
        Resize image if it exceeds maximum dimensions.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Path to the (possibly resized) image file
        """
        try:
            width, height = self.get_image_dimensions(image_path)
            
            # Check if resizing is needed
            if width <= self.max_width and height <= self.max_height:
                logger.debug(f"Image size OK: {width}x{height}")
                return image_path
            
            # Calculate new dimensions maintaining aspect ratio
            aspect_ratio = width / height
            
            if width > self.max_width:
                new_width = self.max_width
                new_height = int(new_width / aspect_ratio)
            else:
                new_width = width
                new_height = height
            
            if new_height > self.max_height:
                new_height = self.max_height
                new_width = int(new_height * aspect_ratio)
            
            logger.info(f"Resizing image from {width}x{height} to {new_width}x{new_height}")
            
            # Resize the image
            with Image.open(image_path) as img:
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                resized_img.save(image_path, "PNG")
            
            logger.info(f"Image resized and saved: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Failed to resize image: {str(e)}")
            # Return original path if resize fails
            return image_path
    
    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> Tuple[str, str]:
        """
        Save uploaded file to temporary directory with UUID.
        
        Args:
            file_content: Binary content of the file
            original_filename: Original filename (for extension)
            
        Returns:
            Tuple of (file_id, file_path)
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Get file extension from original filename
        file_ext = Path(original_filename).suffix or ".pdf"
        filename = f"{file_id}{file_ext}"
        file_path = self.upload_dir / filename
        
        try:
            # Write file content
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"File saved: {file_path} (ID: {file_id})")
            return file_id, str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {str(e)}")
            raise ValueError(f"File save failed: {str(e)}")
    
    def get_file_path(self, file_id: str, extension: str = ".png") -> Optional[str]:
        """
        Get the file path for a given file ID.
        
        Args:
            file_id: UUID of the file
            extension: File extension (default: .png)
            
        Returns:
            Full path to the file if it exists, None otherwise
        """
        filename = f"{file_id}{extension}"
        file_path = self.upload_dir / filename
        
        if file_path.exists():
            return str(file_path)
        
        return None
    
    def cleanup_expired_files(self) -> int:
        """
        Remove files older than TTL from the upload directory.
        
        Returns:
            Number of files deleted
        """
        if not self.upload_dir.exists():
            return 0
        
        current_time = time.time()
        deleted_count = 0
        
        try:
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    # Check file age
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > self.file_ttl:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                            logger.debug(f"Deleted expired file: {file_path}")
                        except Exception as e:
                            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            
            if deleted_count > 0:
                logger.info(f"Cleanup completed: {deleted_count} files deleted")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            return deleted_count
    
    def delete_file(self, file_id: str, extension: str = ".png") -> bool:
        """
        Delete a specific file by ID.
        
        Args:
            file_id: UUID of the file
            extension: File extension (default: .png)
            
        Returns:
            True if file was deleted, False otherwise
        """
        file_path = self.get_file_path(file_id, extension)
        
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {str(e)}")
                return False
        
        return False
