"""
Script to download and setup Poppler for Windows.
Run this script to automatically download and configure Poppler.
"""
import os
import sys
import zipfile
import urllib.request
from pathlib import Path

POPPLER_VERSION = "24.08.0-0"
POPPLER_URL = f"https://github.com/oschwartz10612/poppler-windows/releases/download/v{POPPLER_VERSION}/Release-{POPPLER_VERSION}.zip"

def download_poppler():
    """Download and extract Poppler for Windows."""
    backend_dir = Path(__file__).parent
    poppler_dir = backend_dir / "poppler"
    
    if poppler_dir.exists():
        print(f"✓ Poppler already exists at: {poppler_dir}")
        bin_path = poppler_dir / "Library" / "bin"
        if not bin_path.exists():
            bin_path = poppler_dir / "poppler-24.08.0" / "Library" / "bin"
        if bin_path.exists():
            print(f"✓ Poppler binaries found at: {bin_path}")
            return True
        else:
            print("⚠ Poppler directory exists but binaries not found. Re-downloading...")
            import shutil
            shutil.rmtree(poppler_dir)
    
    print(f"Downloading Poppler from: {POPPLER_URL}")
    print("This may take a few minutes...")
    
    zip_path = backend_dir / "poppler.zip"
    
    try:
        # Download with progress
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            sys.stdout.write(f"\rDownloading: {percent:.1f}%")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(POPPLER_URL, zip_path, reporthook=report_progress)
        print("\n✓ Download complete")
        
        # Extract
        print("Extracting Poppler...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(poppler_dir)
        print(f"✓ Extracted to: {poppler_dir}")
        
        # Clean up
        zip_path.unlink()
        print("✓ Cleaned up temporary files")
        
        # Verify installation
        bin_path = poppler_dir / "Library" / "bin"
        if not bin_path.exists():
            bin_path = poppler_dir / "poppler-24.08.0" / "Library" / "bin"
        
        if bin_path.exists():
            pdftoppm = bin_path / "pdftoppm.exe"
            if pdftoppm.exists():
                print(f"\n✓ Poppler successfully installed!")
                print(f"  Binary path: {bin_path}")
                return True
            else:
                print(f"\n⚠ Warning: pdftoppm.exe not found in {bin_path}")
                return False
        else:
            print(f"\n⚠ Warning: Binary directory not found")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Poppler Setup for Windows")
    print("=" * 60)
    print()
    
    if os.name != 'nt':
        print("This script is for Windows only.")
        print("On Linux/Mac, install poppler using your package manager:")
        print("  Ubuntu/Debian: sudo apt-get install poppler-utils")
        print("  Mac: brew install poppler")
        sys.exit(0)
    
    success = download_poppler()
    
    print()
    print("=" * 60)
    if success:
        print("✓ Setup complete! You can now run the backend server.")
        print("  Run: uvicorn app.main:app --reload")
    else:
        print("✗ Setup failed. Please install Poppler manually:")
        print("  1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("  2. Extract to: backend/poppler/")
        print("  3. Ensure pdftoppm.exe is in: backend/poppler/Library/bin/")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
