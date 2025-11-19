"""Tests for KML generator service."""
import pytest
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime

from app.services.kml_generator import KMLGenerator
from app.models.schemas import TransformedBox, GeoPoint


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory."""
    output_dir = tmp_path / "kml_output"
    output_dir.mkdir()
    return str(output_dir)


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
                GeoPoint(lat=35.6752, lng=139.6503),
            ],
            center=GeoPoint(lat=35.6757, lng=139.6508)
        ),
        TransformedBox(
            id="box2",
            corners=[
                GeoPoint(lat=35.6800, lng=139.6600),
                GeoPoint(lat=35.6800, lng=139.6610),
                GeoPoint(lat=35.6790, lng=139.6610),
                GeoPoint(lat=35.6790, lng=139.6600),
            ],
            center=GeoPoint(lat=35.6795, lng=139.6605)
        ),
    ]


def test_kml_generator_initialization(temp_output_dir):
    """Test KML generator initialization."""
    generator = KMLGenerator(output_dir=temp_output_dir)
    assert generator.output_dir == Path(temp_output_dir)
    assert generator.output_dir.exists()


def test_generate_kml_creates_file(temp_output_dir, sample_transformed_boxes):
    """Test that KML file is created successfully."""
    generator = KMLGenerator(output_dir=temp_output_dir)
    filepath = generator.generate_kml(sample_transformed_boxes, base_filename="test_boxes")
    
    assert Path(filepath).exists()
    assert filepath.endswith(".kml")
    assert "test_boxes" in filepath


def test_generate_kml_filename_includes_timestamp(temp_output_dir, sample_transformed_boxes):
    """Test that generated filename includes timestamp."""
    generator = KMLGenerator(output_dir=temp_output_dir)
    filepath = generator.generate_kml(sample_transformed_boxes)
    
    filename = Path(filepath).name
    # Check format: red_boxes_YYYYMMDD_HHMMSS.kml
    assert filename.startswith("red_boxes_")
    assert filename.endswith(".kml")
    
    # Extract timestamp part
    timestamp_part = filename.replace("red_boxes_", "").replace(".kml", "")
    # Verify it can be parsed as a timestamp
    datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S")


def test_generate_kml_with_empty_boxes(temp_output_dir):
    """Test that generating KML with empty boxes raises error."""
    generator = KMLGenerator(output_dir=temp_output_dir)
    
    with pytest.raises(ValueError, match="少なくとも1つの赤枠が必要です"):
        generator.generate_kml([])


def test_kml_structure_is_valid(temp_output_dir, sample_transformed_boxes):
    """Test that generated KML has valid structure."""
    generator = KMLGenerator(output_dir=temp_output_dir)
    filepath = generator.generate_kml(sample_transformed_boxes)
    
    # Parse KML file
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # Check KML namespace
    assert "kml" in root.tag.lower()
    
    # Check Document element exists
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    document = root.find('kml:Document', ns)
    assert document is not None
    
    # Check document name
    doc_name = document.find('kml:name', ns)
    assert doc_name is not None
    assert doc_name.text == "PDF Red Boxes"


def test_kml_contains_correct_number_of_placemarks(temp_output_dir, sample_transformed_boxes):
    """Test that KML contains correct number of placemarks."""
    generator = KMLGenerator(output_dir=temp_output_dir)
    filepath = generator.generate_kml(sample_transformed_boxes)
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    placemarks = root.findall('.//kml:Placemark', ns)
    
    assert len(placemarks) == len(sample_transformed_boxes)


def test_kml_polygon_coordinates(temp_output_dir, sample_transformed_boxes):
    """Test that polygon coordinates are correctly formatted."""
    generator = KMLGenerator(output_dir=temp_output_dir)
    filepath = generator.generate_kml(sample_transformed_boxes)
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    coordinates = root.find('.//kml:coordinates', ns)
    
    assert coordinates is not None
    coord_text = coordinates.text.strip()
    
    # Check that coordinates are in lng,lat,alt format
    # simplekml formats coordinates on a single line separated by spaces
    coord_points = coord_text.split()
    
    # Should have 5 coordinate points (4 corners + closing point)
    assert len(coord_points) == 5
    
    # Verify first and last points are the same (closed polygon)
    assert coord_points[0] == coord_points[-1]
    
    # Verify coordinate format (lng,lat,alt)
    for coord_point in coord_points:
        parts = coord_point.split(',')
        assert len(parts) == 3
        lng, lat, alt = parts
        assert float(lng)  # Can parse as float
        assert float(lat)  # Can parse as float
        assert alt == '0'  # Altitude is 0


def test_kml_placemark_names(temp_output_dir, sample_transformed_boxes):
    """Test that placemarks have correct names."""
    generator = KMLGenerator(output_dir=temp_output_dir)
    filepath = generator.generate_kml(sample_transformed_boxes)
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    placemarks = root.findall('.//kml:Placemark', ns)
    
    for idx, placemark in enumerate(placemarks, start=1):
        name = placemark.find('kml:name', ns)
        assert name is not None
        assert name.text == f"Box {idx}"


def test_kml_placemark_descriptions(temp_output_dir, sample_transformed_boxes):
    """Test that placemarks have descriptions with box info."""
    generator = KMLGenerator(output_dir=temp_output_dir)
    filepath = generator.generate_kml(sample_transformed_boxes)
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    placemarks = root.findall('.//kml:Placemark', ns)
    
    for idx, placemark in enumerate(placemarks):
        description = placemark.find('kml:description', ns)
        assert description is not None
        
        desc_text = description.text
        box = sample_transformed_boxes[idx]
        
        # Check that description contains box ID and center coordinates
        assert box.id in desc_text
        assert "Center:" in desc_text
        assert str(round(box.center.lat, 6)) in desc_text
        assert str(round(box.center.lng, 6)) in desc_text
