"""
Tests for logger module
"""
import pytest
import logging
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from tgecomm.logger import setup_logger


class TestLogger:
    """Tests for logger setup"""
    
    def test_setup_logger_basic(self):
        """Test basic logger setup"""
        logger = setup_logger('test_logger')
        
        assert logger.name == 'test_logger'
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1  # Console handler
    
    def test_setup_logger_custom_level(self):
        """Test logger setup with custom level"""
        logger = setup_logger('test_logger', level=logging.DEBUG)
        
        assert logger.level == logging.DEBUG
    
    @patch('logging.FileHandler')
    @patch('pathlib.Path')
    def test_setup_logger_with_file(self, mock_path, mock_file_handler):
        """Test logger setup with file handler"""
        mock_path_instance = MagicMock()
        mock_path_instance.parent = MagicMock()
        mock_path.return_value = mock_path_instance
        
        logger = setup_logger('test_logger', log_file='test.log')
        
        assert len(logger.handlers) == 2  # Console + File handler
        mock_file_handler.assert_called_once()
    
    @patch('logging.FileHandler')
    @patch('pathlib.Path')
    def test_setup_logger_file_creation_error(self, mock_path, mock_file_handler):
        """Test logger setup when file creation fails"""
        mock_path_instance = MagicMock()
        mock_path_instance.parent = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_file_handler.side_effect = PermissionError("Access denied")
        
        logger = setup_logger('test_logger', log_file='test.log')
        
        # Should still have console handler
        assert len(logger.handlers) == 1
    
    @patch('logging.FileHandler')
    @patch('pathlib.Path')
    def test_setup_logger_os_error(self, mock_path, mock_file_handler):
        """Test logger setup when OSError occurs"""
        mock_path_instance = MagicMock()
        mock_path_instance.parent = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_file_handler.side_effect = OSError("Disk full")
        
        logger = setup_logger('test_logger', log_file='test.log')
        
        # Should still have console handler
        assert len(logger.handlers) == 1
    
    def test_setup_logger_removes_existing_handlers(self):
        """Test that setup_logger removes existing handlers"""
        logger = logging.getLogger('test_logger')
        logger.addHandler(logging.StreamHandler())
        
        assert len(logger.handlers) == 1
        
        setup_logger('test_logger')
        
        # Should have only the new console handler
        assert len(logger.handlers) == 1
    
    def test_setup_logger_console_handler_level(self):
        """Test that console handler has correct level"""
        logger = setup_logger('test_logger', level=logging.WARNING)
        
        console_handler = logger.handlers[0]
        assert console_handler.level == logging.WARNING
    
    @patch('logging.FileHandler')
    @patch('pathlib.Path')
    def test_setup_logger_file_handler_level(self, mock_path, mock_file_handler):
        """Test that file handler has DEBUG level"""
        mock_path_instance = MagicMock()
        mock_path_instance.parent = MagicMock()
        mock_path.return_value = mock_path_instance
        
        logger = setup_logger('test_logger', log_file='test.log')
        
        # File handler should be set to DEBUG level
        file_handler = logger.handlers[1]
        assert file_handler.level == logging.DEBUG

