"""Blue box detection module for identifying blue boxes in PDF images."""
import os
import uuid
import logging
from typing import List, Tuple, Optional
import cv2
import numpy as np

from app.models.schemas import DetectedBox, Point

logger = logging.getLogger(__name__)


class BlueBoxDetector:
    """Detects blue boxes (thick borders and filled areas) in images."""
    
    def __init__(self, min_area: Optional[int] = None, min_perimeter: Optional[int] = None):
        """
        Initialize blue box detector with configurable parameters.
        
        Args:
            min_area: Minimum area threshold in pixels (not used, kept for compatibility)
            min_perimeter: Minimum perimeter threshold in pixels (not used, kept for compatibility)
        """
        # Parameters for thick blue border detection (dark blue)
        self.thick_border_hsv_lower = np.array([100, 100, 100])
        self.thick_border_hsv_upper = np.array([130, 255, 255])
        
        # Parameters for filled blue area detection (light blue)
        self.filled_area_hsv_lower = np.array([90, 30, 180])
        self.filled_area_hsv_upper = np.array([130, 150, 255])
        
        logger.info("BlueBoxDetector initialized")
    
    def detect_blue_boxes(self, image_path: str) -> List[DetectedBox]:
        """
        Detect blue boxes in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of detected boxes
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image cannot be read
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot read image: {image_path}")
            
            logger.info(f"Detecting blue boxes in image: {image_path}")
            logger.debug(f"Image shape: {image.shape}")
            
            # Detect thick blue borders
            thick_border_boxes = self._detect_thick_blue_borders(image)
            logger.info(f"Detected {len(thick_border_boxes)} thick blue borders")
            
            # Detect filled blue areas
            filled_area_boxes = self._detect_filled_blue_areas(image)
            logger.info(f"Detected {len(filled_area_boxes)} filled blue areas")
            
            # Combine results and remove duplicates
            all_boxes = []
            
            # Convert thick border boxes to DetectedBox
            for box in thick_border_boxes:
                detected_box = self._create_detected_box(box, "blue_thick_border")
                all_boxes.append(detected_box)
            
            # Convert filled area boxes to DetectedBox
            for box in filled_area_boxes:
                detected_box = self._create_detected_box(box, "blue_filled_area")
                all_boxes.append(detected_box)
            
            # Remove overlapping boxes (keep larger ones)
            all_boxes = self._remove_overlapping_boxes(all_boxes)
            
            logger.info(f"Total detected blue boxes after filtering: {len(all_boxes)}")
            return all_boxes
            
        except Exception as e:
            logger.error(f"Failed to detect blue boxes: {str(e)}")
            raise ValueError(f"Blue box detection failed: {str(e)}")
    
    def _detect_thick_blue_borders(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Detect thick blue borders using morphological operations.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of contours representing blue borders (closed polygons)
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create mask for dark blue color
        blue_mask = cv2.inRange(hsv, self.thick_border_hsv_lower, self.thick_border_hsv_upper)
        
        # Step 1: Dilate to thicken lines and connect gaps
        kernel_dilate = np.ones((15, 15), np.uint8)
        mask_dilated = cv2.dilate(blue_mask, kernel_dilate, iterations=1)
        
        # Step 2: Fill holes to create closed regions
        mask_filled = mask_dilated.copy()
        contours_temp, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(mask_filled, contours_temp, -1, 255, -1)
        
        # Step 3: Erode to restore approximate original size
        kernel_erode = np.ones((10, 10), np.uint8)
        mask_final = cv2.erode(mask_filled, kernel_erode, iterations=1)
        
        # Find contours from the processed mask
        contours, _ = cv2.findContours(mask_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area
        boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Lower threshold to detect smaller regions (1000 pixels²)
            if area < 1000:
                logger.debug(f"Skipping small blue contour: area={area:.1f}")
                continue
            
            polygon = contour.reshape(-1, 2)
            boxes.append(polygon)
            logger.debug(f"Detected thick blue border: {len(contour)} vertices, area={area:.1f}")
        
        return boxes
    
    def _detect_filled_blue_areas(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Detect filled blue areas using color masking.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of contours representing filled blue areas (closed polygons)
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create mask for light blue color
        blue_mask = cv2.inRange(hsv, self.filled_area_hsv_lower, self.filled_area_hsv_upper)
        
        # Apply morphological closing to fill small gaps
        kernel_close = np.ones((5, 5), np.uint8)
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel_close, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area
        boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Lower threshold to detect smaller filled areas (2000 pixels²)
            if area < 2000:
                logger.debug(f"Skipping small filled blue area: area={area:.1f}")
                continue
            
            polygon = contour.reshape(-1, 2)
            boxes.append(polygon)
            logger.debug(f"Detected filled blue area: {len(contour)} vertices, area={area:.1f}")
        
        return boxes
    
    def _create_detected_box(self, box: np.ndarray, box_type: str) -> DetectedBox:
        """
        Create a DetectedBox model from a contour polygon.
        
        Args:
            box: Array of polygon corner points (N x 2)
            box_type: Type of box ("blue_thick_border" or "blue_filled_area")
            
        Returns:
            DetectedBox model instance
        """
        # Generate unique ID
        box_id = str(uuid.uuid4())
        
        # Convert to Point objects
        corners = [
            Point(x=float(point[0]), y=float(point[1]))
            for point in box
        ]
        
        # Calculate center point (centroid)
        center_x = sum(point[0] for point in box) / len(box)
        center_y = sum(point[1] for point in box) / len(box)
        center = Point(x=float(center_x), y=float(center_y))
        
        return DetectedBox(
            id=box_id,
            corners=corners,
            center=center,
            box_type=box_type
        )
    
    def _remove_overlapping_boxes(self, boxes: List[DetectedBox]) -> List[DetectedBox]:
        """
        Remove overlapping boxes, keeping the larger ones.
        
        Args:
            boxes: List of detected boxes
            
        Returns:
            Filtered list of boxes without significant overlaps
        """
        if len(boxes) <= 1:
            return boxes
        
        # Calculate area for each box
        box_areas = []
        for box in boxes:
            points = np.array([[c.x, c.y] for c in box.corners], dtype=np.float32)
            area = cv2.contourArea(points)
            box_areas.append((box, area))
        
        # Sort by area (largest first)
        box_areas.sort(key=lambda x: x[1], reverse=True)
        
        # Keep non-overlapping boxes
        kept_boxes = []
        for box, area in box_areas:
            is_duplicate = False
            box_points = np.array([[c.x, c.y] for c in box.corners], dtype=np.float32)
            
            for kept_box in kept_boxes:
                kept_points = np.array([[c.x, c.y] for c in kept_box.corners], dtype=np.float32)
                overlap_ratio = self._calculate_polygon_overlap(box_points, kept_points, area)
                
                if overlap_ratio > 0.5:
                    is_duplicate = True
                    logger.debug(f"Removing duplicate blue box with {overlap_ratio:.2%} overlap")
                    break
            
            if not is_duplicate:
                kept_boxes.append(box)
        
        return kept_boxes
    
    def _calculate_polygon_overlap(
        self, 
        poly1: np.ndarray, 
        poly2: np.ndarray, 
        area1: float
    ) -> float:
        """
        Calculate overlap ratio between two polygons.
        
        Args:
            poly1: First polygon points
            poly2: Second polygon points
            area1: Area of first polygon
            
        Returns:
            Overlap ratio (0.0 to 1.0)
        """
        try:
            center1 = np.mean(poly1, axis=0)
            if cv2.pointPolygonTest(poly2, tuple(center1), False) >= 0:
                return 0.8
            
            center2 = np.mean(poly2, axis=0)
            if cv2.pointPolygonTest(poly1, tuple(center2), False) >= 0:
                return 0.8
            
            overlap_count = 0
            for point in poly1:
                if cv2.pointPolygonTest(poly2, tuple(point), False) >= 0:
                    overlap_count += 1
            
            if overlap_count > len(poly1) * 0.5:
                return 0.7
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Error calculating polygon overlap: {e}")
            return 0.0
