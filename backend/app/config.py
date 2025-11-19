"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    app_name: str = "PDF Red Box KML Converter"
    debug: bool = False
    
    # File upload settings
    upload_dir: str = "temp"
    max_file_size: int = 52428800  # 50MB in bytes
    file_ttl: int = 3600  # 1 hour in seconds
    
    # Logging settings
    log_level: str = "INFO"
    
    # CORS settings
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Image processing settings
    max_image_width: int = 4000
    max_image_height: int = 4000
    pdf_dpi: int = 300
    
    # Red box detection settings
    min_box_area: int = 500  # Minimum area in pixels
    min_box_perimeter: int = 50  # Minimum perimeter in pixels
    min_box_vertices: int = 3  # Minimum polygon vertices
    max_box_vertices: int = 50  # Maximum polygon vertices
    approx_epsilon: float = 0.01  # Polygon approximation epsilon
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
