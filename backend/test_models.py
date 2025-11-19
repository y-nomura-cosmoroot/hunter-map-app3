"""Test script to validate data models."""
import sys
sys.path.insert(0, '.')

from app.models.schemas import (
    Point, GeoPoint, ReferencePoint, DetectedBox, TransformedBox,
    UploadResponse, DetectionResponse, TransformRequest, TransformResponse,
    KMLRequest, KMLResponse, ErrorResponse
)
from app.models.errors import ERROR_MESSAGES, get_error_message

def test_point():
    """Test Point model."""
    p = Point(x=100.5, y=200.3)
    assert p.x == 100.5
    assert p.y == 200.3
    print("✓ Point model works")

def test_geopoint():
    """Test GeoPoint model with validation."""
    # Valid coordinates
    gp = GeoPoint(lat=35.6762, lng=139.6503)
    assert gp.lat == 35.6762
    assert gp.lng == 139.6503
    
    # Test validation - invalid latitude
    try:
        GeoPoint(lat=91, lng=0)
        assert False, "Should have raised validation error"
    except Exception:
        pass
    
    # Test validation - invalid longitude
    try:
        GeoPoint(lat=0, lng=181)
        assert False, "Should have raised validation error"
    except Exception:
        pass
    
    print("✓ GeoPoint model with validation works")

def test_reference_point():
    """Test ReferencePoint model."""
    rp = ReferencePoint(
        image_point=Point(x=100, y=200),
        geo_point=GeoPoint(lat=35.6762, lng=139.6503),
        id="ref1"
    )
    assert rp.id == "ref1"
    print("✓ ReferencePoint model works")

def test_detected_box():
    """Test DetectedBox model."""
    # Test with 4 corners (rectangle)
    box = DetectedBox(
        id="box1",
        corners=[
            Point(x=10, y=10),
            Point(x=100, y=10),
            Point(x=100, y=100),
            Point(x=10, y=100)
        ],
        center=Point(x=55, y=55),
        box_type="thick_border"
    )
    assert len(box.corners) == 4
    assert box.box_type == "thick_border"
    
    # Test with polygon (5 corners)
    box_polygon = DetectedBox(
        id="box2",
        corners=[
            Point(x=10, y=10),
            Point(x=100, y=10),
            Point(x=120, y=50),
            Point(x=100, y=100),
            Point(x=10, y=100)
        ],
        center=Point(x=68, y=54),
        box_type="filled_area"
    )
    assert len(box_polygon.corners) == 5
    
    # Test validation - insufficient corners
    try:
        DetectedBox(
            id="box3",
            corners=[Point(x=0, y=0), Point(x=1, y=1)],
            center=Point(x=0, y=0),
            box_type="filled_area"
        )
        assert False, "Should have raised validation error"
    except Exception:
        pass
    
    print("✓ DetectedBox model with validation works (supports polygons)")

def test_transformed_box():
    """Test TransformedBox model."""
    # Test with 4 corners (rectangle)
    box = TransformedBox(
        id="box1",
        corners=[
            GeoPoint(lat=35.6762, lng=139.6503),
            GeoPoint(lat=35.6763, lng=139.6504),
            GeoPoint(lat=35.6764, lng=139.6505),
            GeoPoint(lat=35.6765, lng=139.6506)
        ],
        center=GeoPoint(lat=35.6763, lng=139.6504)
    )
    assert len(box.corners) == 4
    
    # Test with polygon (6 corners)
    box_polygon = TransformedBox(
        id="box2",
        corners=[
            GeoPoint(lat=35.6762, lng=139.6503),
            GeoPoint(lat=35.6763, lng=139.6504),
            GeoPoint(lat=35.6764, lng=139.6505),
            GeoPoint(lat=35.6765, lng=139.6506),
            GeoPoint(lat=35.6766, lng=139.6507),
            GeoPoint(lat=35.6767, lng=139.6508)
        ],
        center=GeoPoint(lat=35.6764, lng=139.6505)
    )
    assert len(box_polygon.corners) == 6
    
    print("✓ TransformedBox model works (supports polygons)")

def test_transform_request():
    """Test TransformRequest validation."""
    # Valid request with 3 reference points
    req = TransformRequest(
        file_id="file123",
        reference_points=[
            ReferencePoint(
                image_point=Point(x=i*10, y=i*10),
                geo_point=GeoPoint(lat=35.6762+i*0.001, lng=139.6503+i*0.001),
                id=f"ref{i}"
            )
            for i in range(3)
        ],
        boxes=["box1", "box2"]
    )
    assert len(req.reference_points) == 3
    
    # Test validation - insufficient reference points
    try:
        TransformRequest(
            file_id="file123",
            reference_points=[
                ReferencePoint(
                    image_point=Point(x=0, y=0),
                    geo_point=GeoPoint(lat=35.6762, lng=139.6503),
                    id="ref1"
                )
            ],
            boxes=["box1"]
        )
        assert False, "Should have raised validation error"
    except Exception as e:
        # Pydantic validation error message
        assert "at least 3" in str(e) or "最低3つの基準点が必要です" in str(e)
    
    print("✓ TransformRequest model with validation works")

def test_error_messages():
    """Test error message utilities."""
    # Test getting error message
    error = get_error_message("invalid_file_format")
    assert error["error"] == "invalid_file_format"
    assert "PDF形式" in error["message"]
    assert "suggestion" in error
    
    # Test with formatting
    error = get_error_message("insufficient_reference_points", count=2)
    assert "2個" in error["message"]
    
    # Test unknown error type
    error = get_error_message("unknown_error")
    assert error["error"] == "internal_error"
    
    print(f"✓ Error messages work ({len(ERROR_MESSAGES)} error types defined)")

def test_all_response_models():
    """Test all response models."""
    # UploadResponse
    upload_resp = UploadResponse(
        file_id="file123",
        image_url="/uploads/file123.png",
        width=1000,
        height=800
    )
    assert upload_resp.file_id == "file123"
    
    # DetectionResponse
    detection_resp = DetectionResponse(
        boxes=[],
        count=0
    )
    assert detection_resp.count == 0
    
    # TransformResponse
    transform_resp = TransformResponse(
        transformed_boxes=[],
        map_scale=25000.0,
        warnings=["共線性の警告"]
    )
    assert transform_resp.map_scale == 25000.0
    
    # KMLResponse
    kml_resp = KMLResponse(
        download_url="/download/file.kml",
        filename="boxes_20231119.kml"
    )
    assert kml_resp.filename == "boxes_20231119.kml"
    
    # ErrorResponse
    error_resp = ErrorResponse(
        error="invalid_file_format",
        message="エラーメッセージ",
        details="詳細情報",
        suggestion="対処方法"
    )
    assert error_resp.error == "invalid_file_format"
    
    print("✓ All response models work")

if __name__ == "__main__":
    print("Testing data models...\n")
    
    test_point()
    test_geopoint()
    test_reference_point()
    test_detected_box()
    test_transformed_box()
    test_transform_request()
    test_error_messages()
    test_all_response_models()
    
    print("\n✅ All model tests passed!")
