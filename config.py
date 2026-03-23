"""
Configuration module
Loads environment variables and provides configuration
"""

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration"""
    
    # Outlook/Microsoft 365
    TENANT_ID = os.getenv("TENANT_ID", "")
    CLIENT_ID = os.getenv("CLIENT_ID", "")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "./config/firebase-credentials.json")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./email_calendar.db")
    
    # Notification Settings
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "5"))
    NOTIFICATION_ADVANCE_HOURS = int(os.getenv("NOTIFICATION_ADVANCE_HOURS", "24"))
    
    # Email Settings
    EMAIL_USER = os.getenv("EMAIL_USER", "")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        required_fields = ["TENANT_ID", "CLIENT_ID", "CLIENT_SECRET"]
        missing = []
        
        for field in required_fields:
            if not getattr(Config, field):
                missing.append(field)
        
        if missing:
            logger.warning(f"Missing required configuration: {', '.join(missing)}")
            raise ValueError(f"Missing configuration: {', '.join(missing)}")
        
        logger.info("Configuration validated successfully")


def setup_logging():
    """Setup application logging"""
    os.makedirs("./logs", exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Logging configured successfully")
