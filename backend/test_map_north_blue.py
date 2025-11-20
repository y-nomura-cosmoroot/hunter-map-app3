"""Test script to detect blue boxes in map_north.pdf"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.pdf_processor import PDFProcessor
from app.services.blue_box_detector import BlueBoxDetector
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test blue box detection on map_north.pdf"""
    
    # Initialize services
    pdf_processor = PDFProcessor()
    blue_detector = BlueBoxDetector()
    
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
        
        # Detect blue boxes
        blue_boxes = blue_detector.detect_blue_boxes(image_path)
        logger.info(f"Detected {len(blue_boxes)} blue boxes")
        
        # Print details
        for idx, box in enumerate(blue_boxes, 1):
            logger.info(f"Blue Box {idx}:")
            logger.info(f"  ID: {box.id}")
            logger.info(f"  Type: {box.box_type}")
            logger.info(f"  Center: ({box.center.x:.1f}, {box.center.y:.1f})")
            logger.info(f"  Vertices: {len(box.corners)}")
        
        if len(blue_boxes) == 0:
            logger.warning("No blue boxes detected. You may need to adjust HSV color ranges.")
            logger.info("Current HSV ranges:")
            logger.info(f"  Thick border: {blue_detector.thick_border_hsv_lower} - {blue_detector.thick_border_hsv_upper}")
            logger.info(f"  Filled area: {blue_detector.filled_area_hsv_lower} - {blue_detector.filled_area_hsv_upper}")
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
