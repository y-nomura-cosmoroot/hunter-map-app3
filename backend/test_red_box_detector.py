"""Test script for red box detector module."""
import os
import sys
from pathlib import Path
import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.red_box_detector import RedBoxDetector
from app.config import settings


def create_test_image_with_red_boxes(output_path: str) -> str:
    """
    Create a test image with red boxes for testing.
    
    Args:
        output_path: Path to save the test image
        
    Returns:
        Path to the created test image
    """
    # Create a white image
    width, height = 800, 600
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw a thick red border rectangle (dark red - BGR: 0, 0, 200)
    cv2.rectangle(image, (100, 100), (300, 250), (0, 0, 200), 3)
    
    # Draw a filled light red rectangle (light red - BGR: 180, 180, 255)
    cv2.rectangle(image, (400, 100), (600, 250), (180, 180, 255), -1)
    
    # Draw another thick red border rectangle (dark red - BGR: 0, 0, 220)
    cv2.rectangle(image, (100, 350), (300, 500), (0, 0, 220), 4)
    
    # Draw another filled light red rectangle
    cv2.rectangle(image, (400, 350), (600, 500), (200, 200, 255), -1)
    
    # Draw a polygon (pentagon) with red fill
    pentagon_points = np.array([
        [650, 100], [720, 130], [700, 200], [670, 220], [630, 180]
    ], dtype=np.int32)
    cv2.fillPoly(image, [pentagon_points], (190, 190, 255))
    
    # Draw a small red dot (should be filtered out)
    cv2.circle(image, (50, 50), 3, (0, 0, 200), -1)
    
    # Save the image
    cv2.imwrite(output_path, image)
    print(f"Test image created: {output_path}")
    
    return output_path


def test_detector_initialization():
    """Test red box detector initialization."""
    print("Testing red box detector initialization...")
    detector = RedBoxDetector()
    
    # Check that HSV parameters are set
    assert detector.filled_area_hsv_lower1 is not None, "HSV lower1 should be set"
    assert detector.filled_area_hsv_upper1 is not None, "HSV upper1 should be set"
    assert detector.filled_area_hsv_lower2 is not None, "HSV lower2 should be set"
    assert detector.filled_area_hsv_upper2 is not None, "HSV upper2 should be set"
    
    print("✓ Red box detector initialized successfully")
    
    # Test custom initialization (parameters are kept for compatibility but not used)
    custom_detector = RedBoxDetector(min_area=2000, min_perimeter=150)
    assert custom_detector.filled_area_hsv_lower1 is not None, "Custom detector should be initialized"
    print("✓ Custom detector initialization works")


def test_red_box_detection():
    """Test red box detection on a test image."""
    print("\nTesting red box detection...")
    
    # Create test image
    temp_dir = Path(settings.upload_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    test_image_path = str(temp_dir / "test_red_boxes.png")
    
    create_test_image_with_red_boxes(test_image_path)
    
    # Initialize detector
    detector = RedBoxDetector()
    
    # Detect red boxes
    detected_boxes = detector.detect_red_boxes(test_image_path)
    
    print(f"✓ Detection completed")
    print(f"  Total boxes detected: {len(detected_boxes)}")
    
    # Verify detection results
    assert len(detected_boxes) > 0, "Should detect at least one red box"
    
    # Check each detected box
    for i, box in enumerate(detected_boxes):
        print(f"\n  Box {i + 1}:")
        print(f"    ID: {box.id}")
        print(f"    Type: {box.box_type}")
        print(f"    Center: ({box.center.x:.1f}, {box.center.y:.1f})")
        print(f"    Corners: {len(box.corners)}")
        
        # Verify box structure
        assert box.id is not None, "Box should have an ID"
        assert len(box.corners) >= 3, "Box should have at least 3 corners"
        assert box.box_type in ["thick_border", "filled_area"], "Box type should be valid"
        assert box.center.x >= 0 and box.center.y >= 0, "Center should have valid coordinates"
    
    print(f"\n✓ All detected boxes have valid structure")
    
    # Clean up test image
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print(f"✓ Test image cleaned up")


def test_empty_image():
    """Test detection on an image without red boxes."""
    print("\nTesting detection on image without red boxes...")
    
    # Create a plain white image
    temp_dir = Path(settings.upload_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    test_image_path = str(temp_dir / "test_no_boxes.png")
    
    # Create white image
    image = np.ones((600, 800, 3), dtype=np.uint8) * 255
    cv2.imwrite(test_image_path, image)
    
    # Initialize detector
    detector = RedBoxDetector()
    
    # Detect red boxes
    detected_boxes = detector.detect_red_boxes(test_image_path)
    
    print(f"✓ Detection completed on empty image")
    print(f"  Boxes detected: {len(detected_boxes)}")
    
    # Clean up
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print(f"✓ Test image cleaned up")


def test_invalid_image_path():
    """Test detection with invalid image path."""
    print("\nTesting detection with invalid image path...")
    
    detector = RedBoxDetector()
    
    try:
        detector.detect_red_boxes("nonexistent_image.png")
        assert False, "Should raise FileNotFoundError"
    except FileNotFoundError as e:
        print(f"✓ Correctly raised FileNotFoundError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Red Box Detector Module Tests")
    print("=" * 60)
    
    try:
        test_detector_initialization()
        test_red_box_detection()
        test_empty_image()
        test_invalid_image_path()
        
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
