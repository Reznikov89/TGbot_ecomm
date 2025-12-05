"""
Tests for client module
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from telethon.errors import (
    FloodWaitError,
    UserInvalidError,
    ChatInvalidError,
    ChannelPrivateError,
    MessageEmptyError,
    SessionPasswordNeededError,
    NotFoundError
)
from tgecomm.client import TGecommClient
from tgecomm.config import Config


@pytest.fixture
def mock_config():
    """Mock configuration"""
    with patch.object(Config, 'validate'), \
         patch.object(Config, 'API_ID', 12345), \
         patch.object(Config, 'API_HASH', 'a' * 32), \
         patch.object(Config, 'PHONE', '+1234567890'), \
         patch.object(Config, 'SESSION_NAME', 'test_session'):
        yield Config


@pytest.fixture
def mock_telegram_client():
    """Mock TelegramClient"""
    mock_client = AsyncMock()
    mock_client.is_connected.return_value = True
    return mock_client


@pytest.fixture
def client(mock_config, mock_telegram_client):
    """Create TGecommClient instance with mocked dependencies"""
    with patch('client.TelegramClient', return_value=mock_telegram_client):
        client = TGecommClient()
        client.client = mock_telegram_client
        return client


@pytest.mark.asyncio
async def test_start_success(client):
    """Test successful client start"""
    mock_me = MagicMock()
    mock_me.username = "testuser"
    mock_me.first_name = "Test"
    client.client.get_me = AsyncMock(return_value=mock_me)
    client.client.start = AsyncMock()
    
    await client.start()
    
    client.client.start.assert_called_once_with(phone=Config.PHONE)
    client.client.get_me.assert_called_once()


@pytest.mark.asyncio
async def test_start_with_2fa(client):
    """Test client start with 2FA"""
    client.client.start = AsyncMock(side_effect=SessionPasswordNeededError())
    client.client.sign_in = AsyncMock()
    
    with patch('asyncio.to_thread', return_value='password123'):
        await client.start()
    
    client.client.sign_in.assert_called_once_with(password='password123')


@pytest.mark.asyncio
async def test_send_message_success(client):
    """Test successful message sending"""
    client.client.send_message = AsyncMock()
    
    result = await client.send_message("testuser", "Hello")
    
    assert result is True
    client.client.send_message.assert_called_once_with("testuser", "Hello")


@pytest.mark.asyncio
async def test_send_message_empty(client):
    """Test sending empty message"""
    result = await client.send_message("testuser", "")
    
    assert result is False
    client.client.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_message_too_long(client):
    """Test sending message that exceeds length limit"""
    long_message = "a" * 5000
    
    result = await client.send_message("testuser", long_message)
    
    assert result is False
    client.client.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_send_message_flood_wait(client):
    """Test sending message with flood wait error"""
    error = FloodWaitError(request=MagicMock(), seconds=60)
    client.client.send_message = AsyncMock(side_effect=error)
    
    result = await client.send_message("testuser", "Hello")
    
    assert result is False


    @pytest.mark.asyncio
    async def test_send_message_user_not_found(client):
        """Test sending message to non-existent user"""
        client.client.send_message = AsyncMock(side_effect=UserInvalidError(request=MagicMock()))
        
        result = await client.send_message("nonexistent", "Hello")
        
        assert result is False


@pytest.mark.asyncio
async def test_get_dialogs_success(client):
    """Test getting dialogs successfully"""
    mock_dialog1 = MagicMock()
    mock_dialog1.name = "Dialog 1"
    mock_dialog1.id = 1
    mock_dialog2 = MagicMock()
    mock_dialog2.name = "Dialog 2"
    mock_dialog2.id = 2
    
    client.client.get_dialogs = AsyncMock(return_value=[mock_dialog1, mock_dialog2])
    
    result = await client.get_dialogs(limit=2)
    
    assert len(result) == 2
    client.client.get_dialogs.assert_called_once_with(limit=2)


@pytest.mark.asyncio
async def test_get_dialogs_invalid_limit(client):
    """Test getting dialogs with invalid limit"""
    result = await client.get_dialogs(limit=0)
    
    assert result == []
    client.client.get_dialogs.assert_not_called()


@pytest.mark.asyncio
async def test_get_dialogs_limit_exceeds_max(client):
    """Test getting dialogs with limit exceeding maximum"""
    client.client.get_dialogs = AsyncMock(return_value=[])
    
    await client.get_dialogs(limit=20000)
    
    # Should be limited to MAX_DIALOGS_LIMIT
    client.client.get_dialogs.assert_called_once()


@pytest.mark.asyncio
async def test_get_messages_success(client):
    """Test getting messages successfully"""
    mock_msg = MagicMock()
    mock_msg.text = "Test message"
    mock_msg.date = None
    mock_msg.media = None
    mock_msg.get_sender = AsyncMock(return_value=None)
    
    client.client.get_messages = AsyncMock(return_value=[mock_msg])
    
    result = await client.get_messages("testchat", limit=1)
    
    assert len(result) == 1
    client.client.get_messages.assert_called_once_with("testchat", limit=1)


@pytest.mark.asyncio
async def test_get_messages_invalid_limit(client):
    """Test getting messages with invalid limit"""
    result = await client.get_messages("testchat", limit=-1)
    
    assert result == []
    client.client.get_messages.assert_not_called()


    @pytest.mark.asyncio
    async def test_get_messages_chat_not_found(client):
        """Test getting messages from non-existent chat"""
        client.client.get_messages = AsyncMock(side_effect=ChatInvalidError(request=MagicMock()))
        
        result = await client.get_messages("nonexistent", limit=10)
        
        assert result == []


@pytest.mark.asyncio
async def test_disconnect_success(client):
    """Test successful disconnection"""
    client.client.is_connected.return_value = True
    client.client.disconnect = AsyncMock()
    
    await client.disconnect()
    
    client.client.disconnect.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_not_connected(client):
    """Test disconnection when not connected"""
    client.client.is_connected.return_value = False
    client.client.disconnect = AsyncMock()
    
    await client.disconnect()
    
    client.client.disconnect.assert_not_called()


@pytest.mark.asyncio
async def test_context_manager(client):
    """Test async context manager"""
    client.start = AsyncMock()
    client.disconnect = AsyncMock()
    
    async with client:
        pass
    
    client.start.assert_called_once()
    client.disconnect.assert_called_once()


def test_get_entity_name_user_with_username():
    """Test _get_entity_name for user with username"""
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_user.first_name = None
    mock_user.last_name = None
    
    result = TGecommClient._get_entity_name(mock_user)
    
    assert result == "@testuser"


def test_get_entity_name_user_without_username():
    """Test _get_entity_name for user without username"""
    mock_user = MagicMock()
    mock_user.username = None
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.id = 123
    
    result = TGecommClient._get_entity_name(mock_user)
    
    assert result == "John Doe"


def test_get_entity_name_chat():
    """Test _get_entity_name for chat"""
    mock_chat = MagicMock()
    mock_chat.title = "Test Chat"
    
    result = TGecommClient._get_entity_name(mock_chat)
    
    assert result == "Test Chat"


def test_get_entity_name_none():
    """Test _get_entity_name with None"""
    result = TGecommClient._get_entity_name(None)
    
    assert result == "Unknown"

