"""Test script for geographic coordinate transformation module."""
import os
import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.geo_transformer import GeoTransformer
from app.models.schemas import Point, GeoPoint, ReferencePoint, DetectedBox


def create_test_reference_points() -> list:
    """
    Create test reference points for transformation testing.
    
    Returns:
        List of reference points with known mappings
    """
    # Create reference points that form a triangle (non-collinear)
    # Using Tokyo area coordinates as example
    reference_points = [
        ReferencePoint(
            id="ref1",
            image_point=Point(x=100.0, y=100.0),
            geo_point=GeoPoint(lat=35.6762, lng=139.6503)  # Tokyo Station
        ),
        ReferencePoint(
            id="ref2",
            image_point=Point(x=500.0, y=100.0),
            geo_point=GeoPoint(lat=35.6812, lng=139.7671)  # Tokyo Skytree
        ),
        ReferencePoint(
            id="ref3",
            image_point=Point(x=300.0, y=400.0),
            geo_point=GeoPoint(lat=35.6586, lng=139.7454)  # Tokyo Tower
        )
    ]
    
    return reference_points


def test_transformer_initialization():
    """Test geo transformer initialization."""
    print("Testing geo transformer initialization...")
    transformer = GeoTransformer()
    
    assert transformer.affine_matrix is None, "Affine matrix should be None initially"
    assert transformer.translation_vector is None, "Translation vector should be None initially"
    
    print("✓ Geo transformer initialized successfully")


def test_affine_matrix_calculation():
    """Test affine transformation matrix calculation."""
    print("\nTesting affine matrix calculation...")
    
    transformer = GeoTransformer()
    reference_points = create_test_reference_points()
    
    # Calculate affine matrix
    affine_matrix, translation_vector = transformer.calculate_affine_matrix(reference_points)
    
    print(f"✓ Affine matrix calculated successfully")
    print(f"  Matrix shape: {affine_matrix.shape}")
    print(f"  Translation vector shape: {translation_vector.shape}")
    
    # Verify matrix dimensions
    assert affine_matrix.shape == (2, 2), "Affine matrix should be 2x2"
    assert translation_vector.shape == (2,), "Translation vector should be 1D with 2 elements"
    
    # Verify matrix is stored in transformer
    assert transformer.affine_matrix is not None, "Affine matrix should be stored"
    assert transformer.translation_vector is not None, "Translation vector should be stored"
    
    print(f"✓ Matrix dimensions verified")


def test_reference_point_validation():
    """Test reference point validation (collinearity check)."""
    print("\nTesting reference point validation...")
    
    transformer = GeoTransformer()
    
    # Test with valid (non-collinear) points
    valid_points = create_test_reference_points()
    is_valid, error_msg = transformer.validate_reference_points(valid_points)
    
    assert is_valid, "Valid reference points should pass validation"
    assert error_msg == "", "No error message for valid points"
    print(f"✓ Valid reference points passed validation")
    
    # Test with collinear points (all on same line)
    collinear_points = [
        ReferencePoint(
            id="ref1",
            image_point=Point(x=100.0, y=100.0),
            geo_point=GeoPoint(lat=35.6762, lng=139.6503)
        ),
        ReferencePoint(
            id="ref2",
            image_point=Point(x=200.0, y=100.0),
            geo_point=GeoPoint(lat=35.6812, lng=139.7671)
        ),
        ReferencePoint(
            id="ref3",
            image_point=Point(x=300.0, y=100.0),
            geo_point=GeoPoint(lat=35.6586, lng=139.7454)
        )
    ]
    
    is_valid, error_msg = transformer.validate_reference_points(collinear_points)
    
    assert not is_valid, "Collinear points should fail validation"
    assert "一直線" in error_msg, "Error message should mention collinearity"
    print(f"✓ Collinear points correctly rejected")
    print(f"  Error message: {error_msg}")
    
    # Test with insufficient points
    insufficient_points = create_test_reference_points()[:2]
    is_valid, error_msg = transformer.validate_reference_points(insufficient_points)
    
    assert not is_valid, "Insufficient points should fail validation"
    assert "3つ" in error_msg, "Error message should mention minimum 3 points"
    print(f"✓ Insufficient points correctly rejected")
    print(f"  Error message: {error_msg}")


def test_point_transformation():
    """Test transformation of individual points."""
    print("\nTesting point transformation...")
    
    transformer = GeoTransformer()
    reference_points = create_test_reference_points()
    
    # Calculate affine matrix first
    transformer.calculate_affine_matrix(reference_points)
    
    # Transform a test point
    test_point = Point(x=250.0, y=200.0)
    transformed = transformer.transform_point(test_point)
    
    print(f"✓ Point transformed successfully")
    print(f"  Input: ({test_point.x}, {test_point.y})")
    print(f"  Output: ({transformed.lat}, {transformed.lng})")
    
    # Verify output is a valid GeoPoint
    assert isinstance(transformed, GeoPoint), "Output should be GeoPoint"
    assert -90 <= transformed.lat <= 90, "Latitude should be in valid range"
    assert -180 <= transformed.lng <= 180, "Longitude should be in valid range"
    
    # Verify precision (6 decimal places)
    lat_str = str(transformed.lat)
    lng_str = str(transformed.lng)
    if '.' in lat_str:
        lat_decimals = len(lat_str.split('.')[1])
        assert lat_decimals <= 6, "Latitude should have at most 6 decimal places"
    if '.' in lng_str:
        lng_decimals = len(lng_str.split('.')[1])
        assert lng_decimals <= 6, "Longitude should have at most 6 decimal places"
    
    print(f"✓ Output validation passed")


def test_box_transformation():
    """Test transformation of detected boxes."""
    print("\nTesting box transformation...")
    
    transformer = GeoTransformer()
    reference_points = create_test_reference_points()
    
    # Calculate affine matrix
    transformer.calculate_affine_matrix(reference_points)
    
    # Create a test detected box
    test_box = DetectedBox(
        id="box1",
        corners=[
            Point(x=150.0, y=150.0),
            Point(x=250.0, y=150.0),
            Point(x=250.0, y=250.0),
            Point(x=150.0, y=250.0)
        ],
        center=Point(x=200.0, y=200.0),
        box_type="thick_border"
    )
    
    # Transform the box
    transformed_box = transformer.transform_box(test_box)
    
    print(f"✓ Box transformed successfully")
    print(f"  Box ID: {transformed_box.id}")
    print(f"  Center: ({transformed_box.center.lat}, {transformed_box.center.lng})")
    print(f"  Corners: {len(transformed_box.corners)}")
    
    # Verify transformed box structure
    assert transformed_box.id == test_box.id, "Box ID should be preserved"
    assert len(transformed_box.corners) == 4, "Should have 4 corners"
    assert isinstance(transformed_box.center, GeoPoint), "Center should be GeoPoint"
    
    # Verify all corners are valid GeoPoints
    for i, corner in enumerate(transformed_box.corners):
        assert isinstance(corner, GeoPoint), f"Corner {i} should be GeoPoint"
        assert -90 <= corner.lat <= 90, f"Corner {i} latitude should be valid"
        assert -180 <= corner.lng <= 180, f"Corner {i} longitude should be valid"
    
    print(f"✓ Transformed box structure validated")


def test_map_scale_estimation():
    """Test map scale estimation using Haversine formula."""
    print("\nTesting map scale estimation...")
    
    transformer = GeoTransformer()
    reference_points = create_test_reference_points()
    
    # Estimate map scale
    scale = transformer.estimate_map_scale(reference_points, image_dpi=300)
    
    print(f"✓ Map scale estimated successfully")
    print(f"  Scale: 1:{scale:.0f}")
    
    # Verify scale is a positive number
    assert scale > 0, "Scale should be positive"
    assert isinstance(scale, float), "Scale should be a float"
    
    # Test with different DPI
    scale_150dpi = transformer.estimate_map_scale(reference_points, image_dpi=150)
    print(f"  Scale at 150 DPI: 1:{scale_150dpi:.0f}")
    
    # Higher DPI should result in different scale
    assert scale != scale_150dpi, "Different DPI should produce different scales"
    
    print(f"✓ Scale estimation validated")


def test_haversine_distance():
    """Test Haversine distance calculation."""
    print("\nTesting Haversine distance calculation...")
    
    transformer = GeoTransformer()
    
    # Test with known distance (Tokyo Station to Tokyo Skytree ~7.5 km)
    point1 = GeoPoint(lat=35.6762, lng=139.6503)  # Tokyo Station
    point2 = GeoPoint(lat=35.6812, lng=139.7671)  # Tokyo Skytree
    
    distance = transformer._haversine_distance(point1, point2)
    
    print(f"✓ Haversine distance calculated")
    print(f"  Distance: {distance:.2f} meters ({distance/1000:.2f} km)")
    
    # Verify distance is reasonable (should be around 10-11 km based on actual coordinates)
    assert 9000 < distance < 12000, "Distance should be approximately 10-11 km"
    
    # Test with same point (distance should be 0)
    distance_zero = transformer._haversine_distance(point1, point1)
    assert distance_zero == 0, "Distance between same point should be 0"
    
    print(f"✓ Haversine distance validation passed")


def test_pixel_distance():
    """Test pixel distance calculation."""
    print("\nTesting pixel distance calculation...")
    
    transformer = GeoTransformer()
    
    # Test with known distance
    p1 = Point(x=0.0, y=0.0)
    p2 = Point(x=3.0, y=4.0)
    
    distance = transformer._calculate_pixel_distance(p1, p2)
    
    print(f"✓ Pixel distance calculated")
    print(f"  Distance: {distance:.2f} pixels")
    
    # Verify distance (should be 5.0 by Pythagorean theorem)
    assert abs(distance - 5.0) < 0.001, "Distance should be 5.0 pixels"
    
    # Test with same point
    distance_zero = transformer._calculate_pixel_distance(p1, p1)
    assert distance_zero == 0, "Distance between same point should be 0"
    
    print(f"✓ Pixel distance validation passed")


def test_transformation_without_matrix():
    """Test that transformation fails without calculating matrix first."""
    print("\nTesting transformation without matrix calculation...")
    
    transformer = GeoTransformer()
    test_point = Point(x=100.0, y=100.0)
    
    try:
        transformer.transform_point(test_point)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "計算されていません" in str(e), "Error should mention matrix not calculated"
        print(f"✓ Correctly raised ValueError: {e}")


def test_insufficient_reference_points():
    """Test that calculation fails with insufficient reference points."""
    print("\nTesting with insufficient reference points...")
    
    transformer = GeoTransformer()
    insufficient_points = create_test_reference_points()[:2]
    
    try:
        transformer.calculate_affine_matrix(insufficient_points)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "3つ" in str(e), "Error should mention minimum 3 points"
        print(f"✓ Correctly raised ValueError: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Geographic Coordinate Transformation Module Tests")
    print("=" * 60)
    
    try:
        test_transformer_initialization()
        test_affine_matrix_calculation()
        test_reference_point_validation()
        test_point_transformation()
        test_box_transformation()
        test_map_scale_estimation()
        test_haversine_distance()
        test_pixel_distance()
        test_transformation_without_matrix()
        test_insufficient_reference_points()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
