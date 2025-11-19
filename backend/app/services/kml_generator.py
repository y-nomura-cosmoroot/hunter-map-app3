"""KML file generation service."""
import simplekml
from datetime import datetime
from typing import List
from pathlib import Path
import logging

from app.models.schemas import TransformedBox

logger = logging.getLogger(__name__)


class KMLGenerator:
    """Service for generating KML files from transformed boxes."""
    
    def __init__(self, output_dir: str = "temp"):
        """
        Initialize KML generator.
        
        Args:
            output_dir: Directory to save generated KML files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"KMLGenerator initialized with output_dir: {output_dir}")
    
    def generate_kml(self, boxes: List[TransformedBox], base_filename: str = "red_boxes") -> str:
        """
        Generate KML file from transformed boxes.
        
        Args:
            boxes: List of transformed boxes with geographic coordinates
            base_filename: Base name for the KML file (without extension)
        
        Returns:
            Path to the generated KML file
        
        Raises:
            ValueError: If boxes list is empty
        """
        if not boxes:
            logger.error("Cannot generate KML: boxes list is empty")
            raise ValueError("少なくとも1つの赤枠が必要です")
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_filename}_{timestamp}.kml"
        filepath = self.output_dir / filename
        
        logger.info(f"Generating KML file: {filename} with {len(boxes)} boxes")
        
        # Create KML document
        kml = simplekml.Kml()
        kml.document.name = "PDF Red Boxes"
        
        # Add each box as a polygon
        for idx, box in enumerate(boxes, start=1):
            self._create_polygon(kml, box, idx)
        
        # Save KML file
        kml.save(str(filepath))
        logger.info(f"KML file saved successfully: {filepath}")
        
        return str(filepath)
    
    def _create_polygon(self, kml: simplekml.Kml, box: TransformedBox, index: int) -> None:
        """
        Create a polygon placemark in the KML document.
        
        Args:
            kml: KML document object
            box: Transformed box with geographic coordinates
            index: Box index for naming
        """
        # Create placemark
        placemark = kml.newpolygon(name=f"Box {index}")
        
        # Set polygon coordinates (must close the ring by repeating first point)
        # KML format: longitude, latitude, altitude
        coords = []
        for corner in box.corners:
            coords.append((corner.lng, corner.lat, 0))
        
        # Close the polygon by adding the first point again
        coords.append((box.corners[0].lng, box.corners[0].lat, 0))
        
        placemark.outerboundaryis = coords
        
        # Add description with center point
        placemark.description = (
            f"Box ID: {box.id}\n"
            f"Center: {box.center.lat:.6f}, {box.center.lng:.6f}"
        )
        
        # Style settings (optional - makes boxes visible)
        placemark.style.linestyle.color = simplekml.Color.red
        placemark.style.linestyle.width = 2
        placemark.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.red)
        
        logger.debug(f"Created polygon for Box {index} (ID: {box.id})")
