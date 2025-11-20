"""Test script to detect red boxes in map_north.pdf"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.pdf_processor import PDFProcessor
from app.services.red_box_detector import RedBoxDetector
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test red box detection on map_north.pdf"""
    
    # Initialize services
    pdf_processor = PDFProcessor()
    red_detector = RedBoxDetector()
    
    # Process PDF
    pdf_path = "map_north.pdf"
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return
    
    logger.info(f"Processing PDF: {pdf_path}")
    
    try:
        # Convert PDF to image
        image_path = pdf_processor.convert_pdf_to_image(pdf_path)
        logger.info(f"PDF converted to image: {image_path}")
        
        # Detect red boxes
        red_boxes = red_detector.detect_red_boxes(image_path)
        logger.info(f"Detected {len(red_boxes)} red boxes")
        
        # Print details
        for idx, box in enumerate(red_boxes, 1):
            logger.info(f"Red Box {idx}:")
            logger.info(f"  ID: {box.id}")
            logger.info(f"  Type: {box.box_type}")
            logger.info(f"  Center: ({box.center.x:.1f}, {box.center.y:.1f})")
            logger.info(f"  Vertices: {len(box.corners)}")
        
        if len(red_boxes) == 0:
            logger.warning("No red boxes detected. You may need to adjust HSV color ranges.")
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
