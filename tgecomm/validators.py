"""
Input validation utilities
"""
import re
from typing import Optional


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_positive_integer(value: str, field_name: str = "value") -> int:
    """
    Validate that value is a positive integer
    
    Args:
        value: String to validate
        field_name: Name of the field for error messages
    
    Returns:
        int: Validated integer value
    
    Raises:
        ValidationError: If validation fails
    """
    try:
        num = int(value)
        if num <= 0:
            raise ValidationError(f"{field_name} must be a positive number")
        return num
    except ValueError:
        raise ValidationError(f"{field_name} must be a valid integer")


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Basic validation: starts with +, followed by digits
    pattern = r'^\+\d{10,15}$'
    return bool(re.match(pattern, phone))


def validate_username(username: str) -> bool:
    """
    Validate Telegram username format
    
    Args:
        username: Username to validate (with or without @)
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Remove @ if present
    username = username.lstrip('@')
    
    # Username should be 5-32 characters, alphanumeric and underscores
    pattern = r'^[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, username))


def validate_recipient(recipient: str) -> bool:
    """
    Validate recipient (can be username, phone, or chat ID)
    
    Args:
        recipient: Recipient identifier
    
    Returns:
        bool: True if valid format
    """
    if not recipient or not recipient.strip():
        return False
    
    recipient = recipient.strip()
    
    # Check if it's a username
    if recipient.startswith('@'):
        return validate_username(recipient)
    
    # Check if it's a phone number
    if recipient.startswith('+'):
        return validate_phone_number(recipient)
    
    # Check if it's a numeric ID
    if recipient.lstrip('-').isdigit():
        return True
    
    # Otherwise, assume it's a username without @
    return validate_username(recipient)


def validate_api_id(api_id: Optional[str]) -> bool:
    """
    Validate API ID format
    
    Args:
        api_id: API ID to validate (can be None)
    
    Returns:
        bool: True if valid
    """
    if not api_id:
        return False
    
    try:
        api_id_str = api_id.strip() if isinstance(api_id, str) else str(api_id)
        if not api_id_str:
            return False
        int(api_id_str)
        return True
    except (ValueError, AttributeError):
        return False


def validate_api_hash(api_hash: str) -> bool:
    """
    Validate API Hash format (should be 32 hex characters)
    
    Args:
        api_hash: API Hash to validate
    
    Returns:
        bool: True if valid
    """
    if not api_hash or not api_hash.strip():
        return False
    
    api_hash = api_hash.strip()
    
    # Should be 32 characters, alphanumeric
    pattern = r'^[a-fA-F0-9]{32}$'
    return bool(re.match(pattern, api_hash))


def mask_sensitive_data(data: Optional[str], visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging
    
    Args:
        data: Data to mask (can be None)
        visible_chars: Number of characters to show at the end
    
    Returns:
        str: Masked string
    """
    if not data:
        return "***"
    
    if len(data) <= visible_chars:
        return "***"
    
    return "*" * (len(data) - visible_chars) + data[-visible_chars:]
