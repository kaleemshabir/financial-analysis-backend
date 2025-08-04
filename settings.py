# app/config.py (or settings.py)
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache # For caching settings
import os
from pathlib import Path

# Get the absolute path to the directory containing this file
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'

# Print debug info
print(f"Looking for .env file at: {ENV_FILE}")
print(f"File exists: {ENV_FILE.exists()}")
if ENV_FILE.exists():
    with open(ENV_FILE, 'r') as f:
        content = f.read()
        print(f".env file content length: {len(content)} characters")
        if not content.strip():
            print("WARNING: .env file exists but is empty!")

class Settings(BaseSettings):
    # Model for Pydantic V2+
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    database_url: str = "postgresql://postgres:12345678@localhost/financial_analysis_system"  # Default fallback
    secret_key: str = "skdfdkdkskecert"  # Default fallback
    debug: bool = False  # Default value if not found in .env or env vars
    api_version: str = "v1"

@lru_cache()
def get_settings():
    """
    Caches the settings object to avoid reading .env multiple times per request.
    """
    return Settings()