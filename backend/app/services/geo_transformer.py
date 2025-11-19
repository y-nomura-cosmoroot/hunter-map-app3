"""Geographic coordinate transformation service."""
import numpy as np
from typing import List, Tuple
import logging
from math import radians, cos, sin, asin, sqrt

from app.models.schemas import Point, GeoPoint, ReferencePoint, DetectedBox, TransformedBox

logger = logging.getLogger(__name__)


class GeoTransformer:
    """Handles coordinate transformation from image pixels to geographic coordinates."""
    
    def __init__(self):
        """Initialize the GeoTransformer."""
        self.affine_matrix = None
        self.translation_vector = None
    
    def calculate_affine_matrix(
        self, 
        reference_points: List[ReferencePoint]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate affine transformation matrix using least squares method.
        
        Args:
            reference_points: List of reference points with image and geo coordinates
            
        Returns:
            Tuple of (affine_matrix, translation_vector)
            
        Raises:
            ValueError: If reference points are insufficient or collinear
        """
        if len(reference_points) < 3:
            raise ValueError("最低3つの基準点が必要です")
        
        # Validate reference point configuration
        is_valid, error_msg = self.validate_reference_points(reference_points)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Extract image points (x, y) and geo points (lng, lat)
        image_coords = np.array([[rp.image_point.x, rp.image_point.y] for rp in reference_points])
        geo_coords = np.array([[rp.geo_point.lng, rp.geo_point.lat] for rp in reference_points])
        
        # Add column of ones for affine transformation
        # [x, y, 1] * [a, b, c; d, e, f] = [lng, lat]
        ones = np.ones((len(reference_points), 1))
        A = np.hstack([image_coords, ones])
        
        # Solve for transformation parameters using least squares
        # A * params = geo_coords
        # params = (A^T * A)^-1 * A^T * geo_coords
        try:
            params, residuals, rank, s = np.linalg.lstsq(A, geo_coords, rcond=None)
        except np.linalg.LinAlgError as e:
            logger.error(f"Failed to calculate affine matrix: {e}")
            raise ValueError("アフィン変換行列の計算に失敗しました")
        
        # Extract affine matrix and translation vector
        # params shape: (3, 2) -> [[a, d], [b, e], [c, f]]
        affine_matrix = params[:2, :].T  # Shape: (2, 2)
        translation_vector = params[2, :]  # Shape: (2,)
        
        self.affine_matrix = affine_matrix
        self.translation_vector = translation_vector
        
        logger.info(f"Affine matrix calculated with {len(reference_points)} reference points")
        logger.debug(f"Affine matrix: {affine_matrix}")
        logger.debug(f"Translation vector: {translation_vector}")
        
        return affine_matrix, translation_vector
    
    def validate_reference_points(
        self, 
        reference_points: List[ReferencePoint]
    ) -> Tuple[bool, str]:
        """
        Validate reference point configuration (collinearity check).
        
        Args:
            reference_points: List of reference points
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(reference_points) < 3:
            return False, "最低3つの基準点が必要です"
        
        # Check collinearity using cross product for first 3 points
        p1 = reference_points[0].image_point
        p2 = reference_points[1].image_point
        p3 = reference_points[2].image_point
        
        # Vectors from p1 to p2 and p1 to p3
        v1 = np.array([p2.x - p1.x, p2.y - p1.y])
        v2 = np.array([p3.x - p1.x, p3.y - p1.y])
        
        # Cross product (in 2D, this is the z-component)
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        
        # If cross product is close to zero, points are collinear
        threshold = 1e-6
        if abs(cross_product) < threshold:
            return False, "基準点が一直線上に配置されています"
        
        logger.info("Reference points validation passed")
        return True, ""
    
    def transform_point(
        self, 
        point: Point
    ) -> GeoPoint:
        """
        Transform image coordinates to geographic coordinates.
        
        Args:
            point: Image coordinate point
            
        Returns:
            Geographic coordinate point
            
        Raises:
            ValueError: If affine matrix has not been calculated
        """
        if self.affine_matrix is None or self.translation_vector is None:
            raise ValueError("アフィン変換行列が計算されていません")
        
        # Apply affine transformation: [lng, lat] = A * [x, y] + b
        image_coord = np.array([point.x, point.y])
        geo_coord = self.affine_matrix @ image_coord + self.translation_vector
        
        # Round to 6 decimal places for precision
        lng = round(float(geo_coord[0]), 6)
        lat = round(float(geo_coord[1]), 6)
        
        return GeoPoint(lat=lat, lng=lng)
    
    def transform_box(
        self, 
        box: DetectedBox
    ) -> TransformedBox:
        """
        Transform all corners and center of a detected box to geographic coordinates.
        
        Args:
            box: Detected box with image coordinates
            
        Returns:
            Transformed box with geographic coordinates
        """
        # Transform all four corners
        transformed_corners = [self.transform_point(corner) for corner in box.corners]
        
        # Transform center point
        transformed_center = self.transform_point(box.center)
        
        return TransformedBox(
            id=box.id,
            corners=transformed_corners,
            center=transformed_center
        )
    
    def estimate_map_scale(
        self, 
        reference_points: List[ReferencePoint],
        image_dpi: int = 300
    ) -> float:
        """
        Estimate map scale using reference points and Haversine formula.
        
        Args:
            reference_points: List of reference points
            image_dpi: Image resolution in DPI (default: 300)
            
        Returns:
            Estimated map scale (e.g., 25000 for 1:25000)
        """
        if len(reference_points) < 2:
            logger.warning("Need at least 2 reference points to estimate scale")
            return 0.0
        
        # Calculate distances between consecutive reference points
        scales = []
        
        for i in range(len(reference_points) - 1):
            rp1 = reference_points[i]
            rp2 = reference_points[i + 1]
            
            # Image distance in pixels
            image_dist_pixels = self._calculate_pixel_distance(
                rp1.image_point, 
                rp2.image_point
            )
            
            # Real-world distance in meters using Haversine formula
            real_dist_meters = self._haversine_distance(
                rp1.geo_point, 
                rp2.geo_point
            )
            
            # Convert pixel distance to meters
            # DPI = dots per inch, 1 inch = 25.4 mm = 0.0254 m
            image_dist_meters = (image_dist_pixels / image_dpi) * 0.0254
            
            # Scale = real distance / image distance
            if image_dist_meters > 0:
                scale = real_dist_meters / image_dist_meters
                scales.append(scale)
                logger.debug(f"Scale between points {i} and {i+1}: 1:{scale:.0f}")
        
        # Return average scale
        if scales:
            avg_scale = sum(scales) / len(scales)
            logger.info(f"Estimated map scale: 1:{avg_scale:.0f}")
            return round(avg_scale, 2)
        
        return 0.0
    
    def _calculate_pixel_distance(self, p1: Point, p2: Point) -> float:
        """
        Calculate Euclidean distance between two image points.
        
        Args:
            p1: First point
            p2: Second point
            
        Returns:
            Distance in pixels
        """
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        return sqrt(dx * dx + dy * dy)
    
    def _haversine_distance(self, geo1: GeoPoint, geo2: GeoPoint) -> float:
        """
        Calculate distance between two geographic points using Haversine formula.
        
        Args:
            geo1: First geographic point
            geo2: Second geographic point
            
        Returns:
            Distance in meters
        """
        # Earth radius in meters
        R = 6371000
        
        # Convert to radians
        lat1, lng1 = radians(geo1.lat), radians(geo1.lng)
        lat2, lng2 = radians(geo2.lat), radians(geo2.lng)
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
        c = 2 * asin(sqrt(a))
        
        distance = R * c
        return distance
