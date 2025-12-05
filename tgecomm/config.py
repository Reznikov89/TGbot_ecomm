"""
Configuration module for TGecomm
"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from .validators import (
    validate_api_id,
    validate_api_hash,
    validate_phone_number,
    mask_sensitive_data
)


class Config:
    """Application configuration"""
    
    API_ID: Optional[int] = None
    API_HASH: Optional[str] = None
    PHONE: Optional[str] = None
    SESSION_NAME: str = 'tgecomm_session'
    
    # Limits configuration
    MAX_MESSAGE_LENGTH: int = 4096  # Telegram message length limit
    MAX_DIALOGS_LIMIT: int = 10000  # Maximum dialogs to retrieve
    MAX_MESSAGES_LIMIT: int = 10000  # Maximum messages to retrieve
    
    @classmethod
    def load_env(cls, env_file: str = '.env') -> None:
        """Load environment variables from file
        
        Args:
            env_file: Path to .env file (default: .env)
        """
        load_dotenv(env_file)
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration with security checks
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        # Load .env if not already loaded
        if cls.API_ID is None and cls.API_HASH is None and cls.PHONE is None:
            cls.load_env()
        
        errors = []
        
        # Check API_ID
        api_id_str = os.getenv('API_ID')
        if not api_id_str:
            errors.append("API_ID is not set in .env file")
        elif not validate_api_id(api_id_str):
            errors.append("API_ID must be a valid integer")
        else:
            cls.API_ID = int(api_id_str)
        
        # Check API_HASH
        cls.API_HASH = os.getenv('API_HASH')
        if not cls.API_HASH:
            errors.append("API_HASH is not set in .env file")
        elif not validate_api_hash(cls.API_HASH):
            errors.append("API_HASH must be a 32-character hexadecimal string")
        
        # Check PHONE
        cls.PHONE = os.getenv('PHONE')
        if not cls.PHONE:
            errors.append("PHONE is not set in .env file")
        elif not validate_phone_number(cls.PHONE):
            errors.append(f"PHONE format is invalid. Must be in format +1234567890")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    @classmethod
    def get_masked_config(cls) -> Dict[str, Optional[str]]:
        """Get configuration with masked sensitive data for logging
        
        Returns:
            Dict containing masked configuration values
        """
        return {
            'API_ID': str(cls.API_ID) if cls.API_ID else None,
            'API_HASH': mask_sensitive_data(cls.API_HASH) if cls.API_HASH else None,
            'PHONE': mask_sensitive_data(cls.PHONE, visible_chars=2) if cls.PHONE else None,
            'SESSION_NAME': cls.SESSION_NAME
        }
