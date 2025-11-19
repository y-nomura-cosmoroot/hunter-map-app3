"""Tests for red box detection API endpoint."""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil
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


def create_test_image_with_red_box(output_path: str):
    """Create a test image with a red box."""
    # Create a white image
    image = np.ones((800, 600, 3), dtype=np.uint8) * 255
    
    # Draw a thick red border rectangle
    cv2.rectangle(image, (100, 100), (300, 300), (0, 0, 255), 5)
    
    # Draw a filled red rectangle
    cv2.rectangle(image, (350, 100), (550, 300), (180, 180, 255), -1)
    
    # Save image
    cv2.imwrite(output_path, image)


def test_detect_boxes_success(setup_test_env):
    """Test successful red box detection."""
    # Create test image with red boxes
    file_id = "test_detect_success"
    image_path = setup_test_env / f"{file_id}.png"
    create_test_image_with_red_box(str(image_path))
    
    try:
        # Make request
        response = client.post(
            "/api/detect-boxes",
            json={"file_id": file_id}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert "boxes" in data
        assert "count" in data
        assert data["count"] > 0
        assert len(data["boxes"]) == data["count"]
        
        # Verify box structure
        for box in data["boxes"]:
            assert "id" in box
            assert "corners" in box
            assert "center" in box
            assert "boxType" in box  # camelCase in API response
            assert len(box["corners"]) >= 3  # At least 3 corners for a polygon
            assert box["boxType"] in ["thick_border", "filled_area"]
            
            # Verify corner structure
            for corner in box["corners"]:
                assert "x" in corner
                assert "y" in corner
            
            # Verify center structure
            assert "x" in box["center"]
            assert "y" in box["center"]
    
    finally:
        # Cleanup
        if image_path.exists():
            image_path.unlink()


def test_detect_boxes_file_not_found(setup_test_env):
    """Test detection with non-existent file."""
    response = client.post(
        "/api/detect-boxes",
        json={"file_id": "nonexistent_file"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
    assert data["detail"]["error"] == "file_not_found"


def test_detect_boxes_no_boxes_detected(setup_test_env):
    """Test detection when no red boxes are present."""
    # Create test image without red boxes (all white)
    file_id = "test_no_boxes"
    image_path = setup_test_env / f"{file_id}.png"
    
    # Create a white image with no red boxes
    image = np.ones((800, 600, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(image_path), image)
    
    try:
        response = client.post(
            "/api/detect-boxes",
            json={"file_id": file_id}
        )
        
        # Should return 400 with no_boxes_detected error
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"] == "no_boxes_detected"
    
    finally:
        # Cleanup
        if image_path.exists():
            image_path.unlink()


def test_detect_boxes_invalid_request():
    """Test detection with invalid request (missing file_id)."""
    response = client.post(
        "/api/detect-boxes",
        json={}
    )
    
    assert response.status_code == 422  # Validation error
