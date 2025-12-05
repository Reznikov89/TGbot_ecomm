"""
Tests for validators module
"""
import pytest
from tgecomm.validators import (
    validate_api_id,
    validate_api_hash,
    validate_phone_number,
    validate_username,
    validate_recipient,
    validate_positive_integer,
    mask_sensitive_data,
    ValidationError
)


class TestAPIValidation:
    """Tests for API validation"""
    
    def test_validate_api_id_valid(self):
        assert validate_api_id("12345") is True
        assert validate_api_id("0") is True
    
    def test_validate_api_id_invalid(self):
        assert validate_api_id("") is False
        assert validate_api_id("abc") is False
        assert validate_api_id(None) is False
    
    def test_validate_api_hash_valid(self):
        assert validate_api_hash("a" * 32) is True
        assert validate_api_hash("A" * 32) is True
        assert validate_api_hash("1" * 32) is True
    
    def test_validate_api_hash_invalid(self):
        assert validate_api_hash("") is False
        assert validate_api_hash("a" * 31) is False
        assert validate_api_hash("a" * 33) is False
        assert validate_api_hash("g" * 32) is False  # Invalid hex char


class TestPhoneValidation:
    """Tests for phone number validation"""
    
    def test_validate_phone_valid(self):
        assert validate_phone_number("+1234567890") is True
        assert validate_phone_number("+123456789012345") is True
    
    def test_validate_phone_invalid(self):
        assert validate_phone_number("") is False
        assert validate_phone_number("1234567890") is False  # No +
        assert validate_phone_number("+123") is False  # Too short
        assert validate_phone_number("+1234567890123456") is False  # Too long


class TestUsernameValidation:
    """Tests for username validation"""
    
    def test_validate_username_valid(self):
        assert validate_username("username") is True
        assert validate_username("@username") is True
        assert validate_username("user_name") is True
        assert validate_username("user123") is True
    
    def test_validate_username_invalid(self):
        assert validate_username("") is False
        assert validate_username("user") is False  # Too short
        assert validate_username("a" * 33) is False  # Too long
        assert validate_username("user-name") is False  # Invalid char


class TestPositiveInteger:
    """Tests for positive integer validation"""
    
    def test_validate_positive_integer_valid(self):
        assert validate_positive_integer("1", "test") == 1
        assert validate_positive_integer("100", "test") == 100
    
    def test_validate_positive_integer_invalid(self):
        with pytest.raises(ValidationError):
            validate_positive_integer("0", "test")
        with pytest.raises(ValidationError):
            validate_positive_integer("-1", "test")
        with pytest.raises(ValidationError):
            validate_positive_integer("abc", "test")


class TestMaskSensitiveData:
    """Tests for data masking"""
    
    def test_mask_sensitive_data(self):
        assert mask_sensitive_data("1234567890", 4) == "******7890"
        assert mask_sensitive_data("abc", 4) == "***"
        assert mask_sensitive_data("", 4) == "***"
