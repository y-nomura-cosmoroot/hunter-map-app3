"""Tests for KML generation API endpoint."""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json

from app.main import app
from app.models.schemas import GeoPoint, TransformedBox

client = TestClient(app)


@pytest.fixture
def sample_transformed_boxes():
    """Create sample transformed boxes for testing."""
    return [
        TransformedBox(
            id="box1",
            corners=[
                GeoPoint(lat=35.6762, lng=139.6503),
                GeoPoint(lat=35.6762, lng=139.6513),
                GeoPoint(lat=35.6752, lng=139.6513),
                GeoPoint(lat=35.6752, lng=139.6503)
            ],
            center=GeoPoint(lat=35.6757, lng=139.6508)
        ),
        TransformedBox(
            id="box2",
            corners=[
                GeoPoint(lat=35.6772, lng=139.6523),
                GeoPoint(lat=35.6772, lng=139.6533),
                GeoPoint(lat=35.6762, lng=139.6533),
                GeoPoint(lat=35.6762, lng=139.6523)
            ],
            center=GeoPoint(lat=35.6767, lng=139.6528)
        )
    ]


def test_generate_kml_success(sample_transformed_boxes, tmp_path):
    """Test successful KML generation."""
    # Prepare request
    request_data = {
        "file_id": "test_file_123",
        "boxes": [box.model_dump() for box in sample_transformed_boxes]
    }
    
    # Send request
    response = client.post("/api/generate-kml", json=request_data)
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    assert "download_url" in data
    assert "filename" in data
    assert data["filename"].endswith(".kml")
    assert "red_boxes_test_file_123" in data["filename"]
    assert data["download_url"].startswith("/api/download/")


def test_generate_kml_empty_boxes():
    """Test KML generation with empty boxes list."""
    request_data = {
        "file_id": "test_file_123",
        "boxes": []
    }
    
    response = client.post("/api/generate-kml", json=request_data)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
    assert "message" in data["detail"]


def test_generate_kml_invalid_coordinates():
    """Test KML generation with invalid coordinates."""
    request_data = {
        "file_id": "test_file_123",
        "boxes": [
            {
                "id": "box1",
                "corners": [
                    {"lat": 91.0, "lng": 139.6503},  # Invalid latitude
                    {"lat": 35.6762, "lng": 139.6513},
                    {"lat": 35.6752, "lng": 139.6513},
                    {"lat": 35.6752, "lng": 139.6503}
                ],
                "center": {"lat": 35.6757, "lng": 139.6508}
            }
        ]
    }
    
    response = client.post("/api/generate-kml", json=request_data)
    
    # Should fail validation
    assert response.status_code == 422


def test_download_kml_success(sample_transformed_boxes):
    """Test successful KML file download."""
    # First generate a KML file
    request_data = {
        "file_id": "test_download_123",
        "boxes": [box.model_dump() for box in sample_transformed_boxes]
    }
    
    gen_response = client.post("/api/generate-kml", json=request_data)
    assert gen_response.status_code == 200
    
    filename = gen_response.json()["filename"]
    
    # Now download the file
    download_response = client.get(f"/api/download/{filename}")
    
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/vnd.google-earth.kml+xml"
    assert "attachment" in download_response.headers.get("content-disposition", "")
    
    # Verify KML content
    content = download_response.content.decode("utf-8")
    assert '<?xml version="1.0"' in content
    assert 'xmlns="http://www.opengis.net/kml/2.2"' in content
    assert "<Polygon" in content  # May have id attribute
    assert "Box 1" in content
    assert "Box 2" in content


def test_download_kml_not_found():
    """Test downloading non-existent KML file."""
    response = client.get("/api/download/nonexistent_file.kml")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
    assert "message" in data["detail"]


def test_download_invalid_extension():
    """Test downloading file with invalid extension."""
    response = client.get("/api/download/test_file.txt")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "error" in data["detail"]
