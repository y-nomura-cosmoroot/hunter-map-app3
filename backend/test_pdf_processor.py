"""Test script for PDF processor module."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.pdf_processor import PDFProcessor
from app.config import settings


def test_pdf_processor_initialization():
    """Test PDF processor initialization."""
    print("Testing PDF processor initialization...")
    processor = PDFProcessor()
    
    assert processor.upload_dir.exists(), "Upload directory should be created"
    assert processor.max_width == settings.max_image_width
    assert processor.max_height == settings.max_image_height
    assert processor.pdf_dpi == settings.pdf_dpi
    
    print("✓ PDF processor initialized successfully")
    print(f"  Upload directory: {processor.upload_dir}")
    print(f"  Max dimensions: {processor.max_width}x{processor.max_height}")
    print(f"  PDF DPI: {processor.pdf_dpi}")
    print(f"  File TTL: {processor.file_ttl} seconds")


def test_file_management():
    """Test file save and retrieval."""
    print("\nTesting file management...")
    processor = PDFProcessor()
    
    # Test saving a file
    test_content = b"Test PDF content"
    file_id, file_path = processor.save_uploaded_file(test_content, "test.pdf")
    
    assert file_id is not None, "File ID should be generated"
    assert os.path.exists(file_path), "File should be saved"
    
    print(f"✓ File saved successfully")
    print(f"  File ID: {file_id}")
    print(f"  File path: {file_path}")
    
    # Test retrieving file path
    retrieved_path = processor.get_file_path(file_id, ".pdf")
    assert retrieved_path == file_path, "Retrieved path should match saved path"
    print(f"✓ File path retrieved successfully")
    
    # Test deleting file
    deleted = processor.delete_file(file_id, ".pdf")
    assert deleted, "File should be deleted"
    assert not os.path.exists(file_path), "File should no longer exist"
    print(f"✓ File deleted successfully")


def test_cleanup():
    """Test cleanup of expired files."""
    print("\nTesting cleanup functionality...")
    processor = PDFProcessor()
    
    # Create some test files
    test_files = []
    for i in range(3):
        file_id, file_path = processor.save_uploaded_file(
            f"Test content {i}".encode(), f"test_{i}.pdf"
        )
        test_files.append((file_id, file_path))
    
    print(f"✓ Created {len(test_files)} test files")
    
    # Run cleanup (should not delete recent files)
    deleted_count = processor.cleanup_expired_files()
    print(f"✓ Cleanup completed: {deleted_count} files deleted")
    
    # Clean up test files
    for file_id, _ in test_files:
        processor.delete_file(file_id, ".pdf")
    
    print(f"✓ Test files cleaned up")


if __name__ == "__main__":
    print("=" * 60)
    print("PDF Processor Module Tests")
    print("=" * 60)
    
    try:
        test_pdf_processor_initialization()
        test_file_management()
        test_cleanup()
        
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
