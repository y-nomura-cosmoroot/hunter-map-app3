"""Tests for coordinate transformation API endpoint."""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
import cv2
import numpy as np

from app.main import app
from app.config import settings

client = TestClient(app)


@pytest.fixture
def setup_test_env():
    """Setup test environment with temp directory."""
    # Create temp directory if it doesn't exist
    temp_dir = Path(settings.upload_dir)
    temp_dir.mkdir(exist_ok=True)
    
    yield temp_dir
    
    # Cleanup is handled by the test itself


def create_test_boxes_file(file_id: str, temp_dir: Path):
    """Create a test boxes JSON file."""
    boxes_data = [
        {
            "id": "box_1",
            "corners": [
                {"x": 100.0, "y": 100.0},
                {"x": 300.0, "y": 100.0},
                {"x": 300.0, "y": 300.0},
                {"x": 100.0, "y": 300.0}
            ],
            "center": {"x": 200.0, "y": 200.0},
            "box_type": "thick_border"
        },
        {
            "id": "box_2",
            "corners": [
                {"x": 350.0, "y": 100.0},
                {"x": 550.0, "y": 100.0},
                {"x": 550.0, "y": 300.0},
                {"x": 350.0, "y": 300.0}
            ],
            "center": {"x": 450.0, "y": 200.0},
            "box_type": "filled_area"
        }
    ]
    
    boxes_file_path = temp_dir / f"{file_id}_boxes.json"
    with open(boxes_file_path, 'w', encoding='utf-8') as f:
        json.dump(boxes_data, f, ensure_ascii=False, indent=2)
    
    return boxes_file_path


def test_transform_success(setup_test_env):
    """Test successful coordinate transformation."""
    file_id = "test_transform_success"
    boxes_file = create_test_boxes_file(file_id, setup_test_env)
    
    try:
        # Create transform request with 3 reference points
        request_data = {
            "file_id": file_id,
            "reference_points": [
                {
                    "id": "ref_1",
                    "image_point": {"x": 0.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 139.0}
                },
                {
                    "id": "ref_2",
                    "image_point": {"x": 600.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 140.0}
                },
                {
                    "id": "ref_3",
                    "image_point": {"x": 0.0, "y": 800.0},
                    "geo_point": {"lat": 34.0, "lng": 139.0}
                }
            ],
            "boxes": ["box_1", "box_2"]
        }
        
        # Make request
        response = client.post(
            "/api/transform",
            json=request_data
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert "transformed_boxes" in data
        assert "map_scale" in data
        assert "warnings" in data
        
        # Verify transformed boxes
        assert len(data["transformed_boxes"]) == 2
        
        for box in data["transformed_boxes"]:
            assert "id" in box
            assert "corners" in box
            assert "center" in box
            assert len(box["corners"]) == 4
            
            # Verify corner structure
            for corner in box["corners"]:
                assert "lat" in corner
                assert "lng" in corner
                assert -90 <= corner["lat"] <= 90
                assert -180 <= corner["lng"] <= 180
            
            # Verify center structure
            assert "lat" in box["center"]
            assert "lng" in box["center"]
        
        # Verify map scale is calculated
        assert data["map_scale"] >= 0
    
    finally:
        # Cleanup
        if boxes_file.exists():
            boxes_file.unlink()


def test_transform_insufficient_reference_points(setup_test_env):
    """Test transformation with insufficient reference points."""
    file_id = "test_insufficient_refs"
    boxes_file = create_test_boxes_file(file_id, setup_test_env)
    
    try:
        # Create request with only 2 reference points
        request_data = {
            "file_id": file_id,
            "reference_points": [
                {
                    "id": "ref_1",
                    "image_point": {"x": 0.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 139.0}
                },
                {
                    "id": "ref_2",
                    "image_point": {"x": 600.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 140.0}
                }
            ],
            "boxes": ["box_1"]
        }
        
        # Make request
        response = client.post(
            "/api/transform",
            json=request_data
        )
        
        # Should return 422 validation error (Pydantic validation)
        assert response.status_code == 422
    
    finally:
        # Cleanup
        if boxes_file.exists():
            boxes_file.unlink()


def test_transform_collinear_points(setup_test_env):
    """Test transformation with collinear reference points."""
    file_id = "test_collinear"
    boxes_file = create_test_boxes_file(file_id, setup_test_env)
    
    try:
        # Create request with collinear reference points (all on same line)
        request_data = {
            "file_id": file_id,
            "reference_points": [
                {
                    "id": "ref_1",
                    "image_point": {"x": 0.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 139.0}
                },
                {
                    "id": "ref_2",
                    "image_point": {"x": 100.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 139.1}
                },
                {
                    "id": "ref_3",
                    "image_point": {"x": 200.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 139.2}
                }
            ],
            "boxes": ["box_1"]
        }
        
        # Make request
        response = client.post(
            "/api/transform",
            json=request_data
        )
        
        # Should return 400 with collinear_points error
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"] == "collinear_points"
    
    finally:
        # Cleanup
        if boxes_file.exists():
            boxes_file.unlink()


def test_transform_file_not_found(setup_test_env):
    """Test transformation with non-existent boxes file."""
    request_data = {
        "file_id": "nonexistent_file",
        "reference_points": [
            {
                "id": "ref_1",
                "image_point": {"x": 0.0, "y": 0.0},
                "geo_point": {"lat": 35.0, "lng": 139.0}
            },
            {
                "id": "ref_2",
                "image_point": {"x": 600.0, "y": 0.0},
                "geo_point": {"lat": 35.0, "lng": 140.0}
            },
            {
                "id": "ref_3",
                "image_point": {"x": 0.0, "y": 800.0},
                "geo_point": {"lat": 34.0, "lng": 139.0}
            }
        ],
        "boxes": ["box_1"]
    }
    
    response = client.post(
        "/api/transform",
        json=request_data
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
    assert data["detail"]["error"] == "file_not_found"


def test_transform_no_matching_boxes(setup_test_env):
    """Test transformation with box IDs that don't exist."""
    file_id = "test_no_matching"
    boxes_file = create_test_boxes_file(file_id, setup_test_env)
    
    try:
        request_data = {
            "file_id": file_id,
            "reference_points": [
                {
                    "id": "ref_1",
                    "image_point": {"x": 0.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 139.0}
                },
                {
                    "id": "ref_2",
                    "image_point": {"x": 600.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 140.0}
                },
                {
                    "id": "ref_3",
                    "image_point": {"x": 0.0, "y": 800.0},
                    "geo_point": {"lat": 34.0, "lng": 139.0}
                }
            ],
            "boxes": ["nonexistent_box"]
        }
        
        response = client.post(
            "/api/transform",
            json=request_data
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    finally:
        # Cleanup
        if boxes_file.exists():
            boxes_file.unlink()


def test_transform_with_warnings(setup_test_env):
    """Test transformation that generates warnings."""
    file_id = "test_warnings"
    boxes_file = create_test_boxes_file(file_id, setup_test_env)
    
    try:
        # Use exactly 3 reference points to trigger warning
        request_data = {
            "file_id": file_id,
            "reference_points": [
                {
                    "id": "ref_1",
                    "image_point": {"x": 0.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 139.0}
                },
                {
                    "id": "ref_2",
                    "image_point": {"x": 600.0, "y": 0.0},
                    "geo_point": {"lat": 35.0, "lng": 140.0}
                },
                {
                    "id": "ref_3",
                    "image_point": {"x": 0.0, "y": 800.0},
                    "geo_point": {"lat": 34.0, "lng": 139.0}
                }
            ],
            "boxes": ["box_1"]
        }
        
        response = client.post(
            "/api/transform",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have warning about only 3 reference points
        assert len(data["warnings"]) > 0
        assert any("3つ" in warning for warning in data["warnings"])
    
    finally:
        # Cleanup
        if boxes_file.exists():
            boxes_file.unlink()
