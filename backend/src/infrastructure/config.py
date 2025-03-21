import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory for the application
BASE_DIR = Path(__file__).parent.parent.parent

# Logging configuration
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "detailed",
            "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "app.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "level": "INFO"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "error.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "level": "ERROR"
        }
    },
    "root": {
        "handlers": ["console", "file", "error_file"],
        "level": "INFO"
    }
}

# API URLs and Endpoints
API_V1_PREFIX = "/api/v1"
API_TITLE = "Bahtsul Masail API"
API_DESCRIPTION = "Backend API for Bahtsul Masail application"
API_VERSION = "1.0.0"

# Security Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Database Settings
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# CORS Settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
ALLOWED_HEADERS = ["*"]

# Rate Limiting
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour in seconds
MAX_REQUESTS_PER_WINDOW = int(os.getenv("MAX_REQUESTS_PER_WINDOW", "1000"))

def get_settings() -> Dict[str, Any]:
    """Get all settings as a dictionary."""
    return {
        "api": {
            "prefix": API_V1_PREFIX,
            "title": API_TITLE,
            "description": API_DESCRIPTION,
            "version": API_VERSION
        },
        "security": {
            "jwt_secret_key": JWT_SECRET_KEY,
            "jwt_algorithm": JWT_ALGORITHM,
            "access_token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": REFRESH_TOKEN_EXPIRE_DAYS
        },
        "database": {
            "url": DATABASE_URL
        },
        "cors": {
            "allowed_origins": ALLOWED_ORIGINS,
            "allowed_methods": ALLOWED_METHODS,
            "allowed_headers": ALLOWED_HEADERS
        },
        "rate_limit": {
            "window": RATE_LIMIT_WINDOW,
            "max_requests": MAX_REQUESTS_PER_WINDOW
        }
    }