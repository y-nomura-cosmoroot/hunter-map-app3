"""Test file upload API endpoint."""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io
from PIL import Image

from app.main import app
from app.config import settings

client = TestClient(app)


def create_test_pdf_bytes() -> bytes:
    """Create a simple test PDF file in memory."""
    # For testing, we'll create a minimal PDF
    # This is a minimal valid PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000317 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF
"""
    return pdf_content


def test_upload_valid_pdf():
    """Test uploading a valid PDF file."""
    pdf_content = create_test_pdf_bytes()
    
    response = client.post(
        "/api/upload",
        files={"file": ("test.pdf", pdf_content, "application/pdf")}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "file_id" in data
    assert "image_url" in data
    assert "width" in data
    assert "height" in data
    assert data["width"] > 0
    assert data["height"] > 0
    assert data["image_url"].startswith("/api/images/")


def test_upload_invalid_extension():
    """Test uploading a file with invalid extension."""
    content = b"fake content"
    
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", content, "text/plain")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "invalid_file_format"


def test_upload_invalid_mime_type():
    """Test uploading a file with invalid MIME type."""
    content = b"fake content"
    
    response = client.post(
        "/api/upload",
        files={"file": ("test.pdf", content, "text/plain")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "invalid_file_format"


def test_upload_file_too_large():
    """Test uploading a file that exceeds size limit."""
    # Create content larger than max_file_size
    large_content = b"x" * (settings.max_file_size + 1)
    
    response = client.post(
        "/api/upload",
        files={"file": ("test.pdf", large_content, "application/pdf")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "file_too_large"


def test_get_image_not_found():
    """Test getting an image that doesn't exist."""
    response = client.get("/api/images/nonexistent.png")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "file_not_found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
