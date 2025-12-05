"""
Tests for config module
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from tgecomm.config import Config


class TestConfig:
    """Tests for Config class"""
    
    def test_load_env(self):
        """Test load_env method"""
        with patch('config.load_dotenv') as mock_load:
            Config.load_env('.env.test')
            
            mock_load.assert_called_once_with('.env.test')
    
    @patch('os.getenv')
    @patch('config.validate_api_id', return_value=True)
    @patch('config.validate_api_hash', return_value=True)
    @patch('config.validate_phone_number', return_value=True)
    def test_validate_success(self, mock_phone, mock_hash, mock_id, mock_getenv):
        """Test successful validation"""
        mock_getenv.side_effect = lambda key: {
            'API_ID': '12345',
            'API_HASH': 'a' * 32,
            'PHONE': '+1234567890'
        }.get(key)
        
        result = Config.validate()
        
        assert result is True
        assert Config.API_ID == 12345
        assert Config.API_HASH == 'a' * 32
        assert Config.PHONE == '+1234567890'
    
    @patch('os.getenv', return_value=None)
    def test_validate_missing_api_id(self, mock_getenv):
        """Test validation with missing API_ID"""
        with pytest.raises(ValueError, match="API_ID is not set"):
            Config.validate()
    
    @patch('os.getenv')
    def test_validate_invalid_api_id(self, mock_getenv):
        """Test validation with invalid API_ID"""
        mock_getenv.side_effect = lambda key: {
            'API_ID': 'invalid',
            'API_HASH': 'a' * 32,
            'PHONE': '+1234567890'
        }.get(key)
        
        with patch('config.validate_api_id', return_value=False):
            with pytest.raises(ValueError, match="API_ID must be a valid integer"):
                Config.validate()
    
    @patch('os.getenv')
    def test_validate_missing_api_hash(self, mock_getenv):
        """Test validation with missing API_HASH"""
        mock_getenv.side_effect = lambda key: {
            'API_ID': '12345',
            'API_HASH': None,
            'PHONE': '+1234567890'
        }.get(key)
        
        with patch('config.validate_api_id', return_value=True):
            with pytest.raises(ValueError, match="API_HASH is not set"):
                Config.validate()
    
    @patch('os.getenv')
    def test_validate_invalid_api_hash(self, mock_getenv):
        """Test validation with invalid API_HASH"""
        mock_getenv.side_effect = lambda key: {
            'API_ID': '12345',
            'API_HASH': 'invalid',
            'PHONE': '+1234567890'
        }.get(key)
        
        with patch('config.validate_api_id', return_value=True), \
             patch('config.validate_api_hash', return_value=False):
            with pytest.raises(ValueError, match="API_HASH must be a 32-character"):
                Config.validate()
    
    @patch('os.getenv')
    def test_validate_missing_phone(self, mock_getenv):
        """Test validation with missing PHONE"""
        mock_getenv.side_effect = lambda key: {
            'API_ID': '12345',
            'API_HASH': 'a' * 32,
            'PHONE': None
        }.get(key)
        
        with patch('config.validate_api_id', return_value=True), \
             patch('config.validate_api_hash', return_value=True):
            with pytest.raises(ValueError, match="PHONE is not set"):
                Config.validate()
    
    @patch('os.getenv')
    def test_validate_invalid_phone(self, mock_getenv):
        """Test validation with invalid PHONE"""
        mock_getenv.side_effect = lambda key: {
            'API_ID': '12345',
            'API_HASH': 'a' * 32,
            'PHONE': 'invalid'
        }.get(key)
        
        with patch('config.validate_api_id', return_value=True), \
             patch('config.validate_api_hash', return_value=True), \
             patch('config.validate_phone_number', return_value=False):
            with pytest.raises(ValueError, match="PHONE format is invalid"):
                Config.validate()
    
    def test_get_masked_config(self):
        """Test get_masked_config"""
        Config.API_ID = 12345
        Config.API_HASH = 'a' * 32
        Config.PHONE = '+1234567890'
        Config.SESSION_NAME = 'test_session'
        
        with patch('config.mask_sensitive_data', side_effect=lambda x, **kwargs: f"***{x[-4:]}"):
            result = Config.get_masked_config()
            
            assert result['API_ID'] == '12345'
            assert result['SESSION_NAME'] == 'test_session'
            assert '***' in result['API_HASH']
            assert '***' in result['PHONE']
    
    def test_get_masked_config_none_values(self):
        """Test get_masked_config with None values"""
        Config.API_ID = None
        Config.API_HASH = None
        Config.PHONE = None
        Config.SESSION_NAME = 'test_session'
        
        result = Config.get_masked_config()
        
        assert result['API_ID'] is None
        assert result['API_HASH'] is None
        assert result['PHONE'] is None
        assert result['SESSION_NAME'] == 'test_session'

