"""
Tests for UI module
"""
import pytest
from unittest.mock import patch, MagicMock
from tgecomm.ui import ConsoleUI
from tgecomm.validators import ValidationError


class TestConsoleUI:
    """Tests for ConsoleUI class"""
    
    def test_print_header_with_colorama(self):
        """Test print_header when colorama is available"""
        with patch('ui.COLORAMA_AVAILABLE', True), \
             patch('ui.Fore') as mock_fore, \
             patch('ui.Style') as mock_style, \
             patch('builtins.print') as mock_print:
            mock_fore.CYAN = '\033[36m'
            mock_style.RESET_ALL = '\033[0m'
            
            ConsoleUI.print_header()
            
            assert mock_print.call_count == 3
    
    def test_print_header_without_colorama(self):
        """Test print_header when colorama is not available"""
        with patch('ui.COLORAMA_AVAILABLE', False), \
             patch('builtins.print') as mock_print:
            ConsoleUI.print_header()
            
            assert mock_print.call_count == 3
    
    def test_print_menu(self):
        """Test print_menu"""
        with patch('builtins.print') as mock_print:
            ConsoleUI.print_menu()
            
            assert mock_print.call_count >= 6
    
    @patch('builtins.input', return_value='1')
    def test_get_choice(self, mock_input):
        """Test get_choice"""
        result = ConsoleUI.get_choice()
        
        assert result == '1'
        mock_input.assert_called_once()
    
    @patch('builtins.input', side_effect=['@testuser', 'Hello'])
    @patch('ui.validate_recipient', return_value=True)
    def test_get_send_message_input_valid(self, mock_validate, mock_input):
        """Test get_send_message_input with valid input"""
        recipient, message = ConsoleUI.get_send_message_input()
        
        assert recipient == '@testuser'
        assert message == 'Hello'
    
    @patch('builtins.input', return_value='invalid')
    @patch('ui.validate_recipient', return_value=False)
    @patch('ui.ConsoleUI.print_error')
    def test_get_send_message_input_invalid_recipient(self, mock_print_error, mock_validate, mock_input):
        """Test get_send_message_input with invalid recipient"""
        recipient, message = ConsoleUI.get_send_message_input()
        
        assert recipient is None
        assert message is None
        mock_print_error.assert_called_once()
    
    @patch('builtins.input', side_effect=['@testuser', ''])
    @patch('ui.validate_recipient', return_value=True)
    @patch('ui.ConsoleUI.print_error')
    def test_get_send_message_input_empty_message(self, mock_print_error, mock_validate, mock_input):
        """Test get_send_message_input with empty message"""
        recipient, message = ConsoleUI.get_send_message_input()
        
        assert recipient is None
        assert message is None
        mock_print_error.assert_called_once()
    
    @patch('builtins.input', side_effect=['@testchat', '10'])
    @patch('ui.validate_recipient', return_value=True)
    @patch('ui.validate_positive_integer', return_value=10)
    def test_get_view_messages_input_valid(self, mock_validate_int, mock_validate_recipient, mock_input):
        """Test get_view_messages_input with valid input"""
        chat, limit = ConsoleUI.get_view_messages_input()
        
        assert chat == '@testchat'
        assert limit == 10
    
    @patch('builtins.input', side_effect=['@testchat', ''])
    @patch('ui.validate_recipient', return_value=True)
    def test_get_view_messages_input_default_limit(self, mock_validate_recipient, mock_input):
        """Test get_view_messages_input with default limit"""
        chat, limit = ConsoleUI.get_view_messages_input()
        
        assert chat == '@testchat'
        assert limit == 10
    
    @patch('builtins.input', return_value='invalid')
    @patch('ui.validate_recipient', return_value=False)
    @patch('ui.ConsoleUI.print_error')
    def test_get_view_messages_input_invalid_chat(self, mock_print_error, mock_validate, mock_input):
        """Test get_view_messages_input with invalid chat"""
        chat, limit = ConsoleUI.get_view_messages_input()
        
        assert chat is None
        assert limit is None
    
    @patch('builtins.input', return_value='abc')
    @patch('ui.validate_recipient', return_value=True)
    @patch('ui.validate_positive_integer', side_effect=ValidationError("Invalid"))
    @patch('ui.ConsoleUI.print_error')
    def test_get_view_messages_input_invalid_limit(self, mock_print_error, mock_validate_int, mock_validate_recipient, mock_input):
        """Test get_view_messages_input with invalid limit"""
        chat, limit = ConsoleUI.get_view_messages_input()
        
        assert chat is None
        assert limit is None
    
    @patch('builtins.input', return_value='10')
    @patch('ui.validate_positive_integer', return_value=10)
    def test_get_list_dialogs_input_valid(self, mock_validate, mock_input):
        """Test get_list_dialogs_input with valid input"""
        result = ConsoleUI.get_list_dialogs_input()
        
        assert result == 10
    
    @patch('builtins.input', return_value='')
    def test_get_list_dialogs_input_default(self, mock_input):
        """Test get_list_dialogs_input with default value"""
        result = ConsoleUI.get_list_dialogs_input()
        
        assert result == 10
    
    @patch('builtins.input', return_value='abc')
    @patch('ui.validate_positive_integer', side_effect=ValidationError("Invalid"))
    @patch('ui.ConsoleUI.print_error')
    def test_get_list_dialogs_input_invalid(self, mock_print_error, mock_validate, mock_input):
        """Test get_list_dialogs_input with invalid input"""
        result = ConsoleUI.get_list_dialogs_input()
        
        assert result is None
    
    @patch('ui.COLORAMA_AVAILABLE', True)
    @patch('ui.Fore')
    @patch('ui.Style')
    @patch('builtins.print')
    def test_print_success_with_colorama(self, mock_print, mock_style, mock_fore):
        """Test print_success with colorama"""
        mock_fore.GREEN = '\033[32m'
        mock_style.RESET_ALL = '\033[0m'
        
        ConsoleUI.print_success("Test message")
        
        mock_print.assert_called_once()
    
    @patch('ui.COLORAMA_AVAILABLE', False)
    @patch('builtins.print')
    def test_print_success_without_colorama(self, mock_print):
        """Test print_success without colorama"""
        ConsoleUI.print_success("Test message")
        
        mock_print.assert_called_once()
    
    @patch('ui.COLORAMA_AVAILABLE', True)
    @patch('ui.Fore')
    @patch('ui.Style')
    @patch('builtins.print')
    def test_print_error_with_colorama(self, mock_print, mock_style, mock_fore):
        """Test print_error with colorama"""
        mock_fore.RED = '\033[31m'
        mock_style.RESET_ALL = '\033[0m'
        
        ConsoleUI.print_error("Test error")
        
        mock_print.assert_called_once()
    
    @patch('builtins.print')
    def test_print_info(self, mock_print):
        """Test print_info"""
        ConsoleUI.print_info("Test info")
        
        mock_print.assert_called_once_with("Test info")
    
    @patch('ui.COLORAMA_AVAILABLE', True)
    @patch('ui.Fore')
    @patch('ui.Style')
    @patch('builtins.print')
    def test_print_warning_with_colorama(self, mock_print, mock_style, mock_fore):
        """Test print_warning with colorama"""
        mock_fore.YELLOW = '\033[33m'
        mock_style.RESET_ALL = '\033[0m'
        
        ConsoleUI.print_warning("Test warning")
        
        mock_print.assert_called_once()

