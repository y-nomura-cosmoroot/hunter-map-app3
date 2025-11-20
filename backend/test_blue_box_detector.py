"""Tests for blue box detector service."""
import pytest
import os
from pathlib import Path
import cv2
import numpy as np

from app.services.blue_box_detector import BlueBoxDetector
from app.models.schemas import DetectedBox


@pytest.fixture
def detector():
    """Create a BlueBoxDetector instance."""
    return BlueBoxDetector()


@pytest.fixture
def test_image_path(tmp_path):
    """Create a test image with blue boxes."""
    # Create a white image
    image = np.ones((800, 1000, 3), dtype=np.uint8) * 255
    
    # Draw a thick blue border box
    cv2.rectangle(image, (100, 100), (300, 300), (255, 0, 0), 5)  # BGR: blue
    
    # Draw a filled light blue area
    cv2.rectangle(image, (400, 400), (600, 600), (255, 200, 150), -1)  # BGR: light blue
    
    # Save image
    image_path = tmp_path / "test_blue_boxes.png"
    success = cv2.imwrite(str(image_path), image)
    
    if not success or not image_path.exists():
        raise RuntimeError(f"Failed to save test image to {image_path}")
    
    return str(image_path)


def test_detector_initialization():
    """Test that detector initializes correctly."""
    detector = BlueBoxDetector()
    assert detector is not None
    assert detector.thick_border_hsv_lower is not None
    assert detector.thick_border_hsv_upper is not None


def test_detect_blue_boxes_success(detector, test_image_path):
    """Test successful blue box detection."""
    boxes = detector.detect_blue_boxes(test_image_path)
    
    assert isinstance(boxes, list)
    assert len(boxes) > 0
    
    for box in boxes:
        assert isinstance(box, DetectedBox)
        assert box.id is not None
        assert len(box.corners) > 0
        assert box.center is not None
        assert box.box_type in ["blue_thick_border", "blue_filled_area"]


def test_detect_blue_boxes_file_not_found(detector):
    """Test detection with non-existent file."""
    with pytest.raises(FileNotFoundError):
        detector.detect_blue_boxes("nonexistent.png")


def test_detect_blue_boxes_invalid_image(detector, tmp_path):
    """Test detection with invalid image file."""
    # Create an empty file
    invalid_path = tmp_path / "invalid.png"
    invalid_path.write_text("not an image")
    
    with pytest.raises(ValueError):
        detector.detect_blue_boxes(str(invalid_path))


def test_detect_no_blue_boxes(detector, tmp_path):
    """Test detection when no blue boxes are present."""
    # Create a white image with no blue boxes
    image = np.ones((800, 1000, 3), dtype=np.uint8) * 255
    image_path = tmp_path / "no_boxes.png"
    success = cv2.imwrite(str(image_path), image)
    
    if not success or not image_path.exists():
        pytest.skip(f"Failed to save test image to {image_path}")
    
    boxes = detector.detect_blue_boxes(str(image_path))
    assert isinstance(boxes, list)
    assert len(boxes) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
