"""
Telegram client module
"""
import asyncio
from typing import Optional, List, Any
from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError,
    UserInvalidError,
    ChatInvalidError,
    ChannelPrivateError,
    MessageEmptyError,
    SessionPasswordNeededError,
    NotFoundError
)
from telethon.tl.types import User, Chat, Channel, Message, Dialog
from .config import Config
from .logger import setup_logger
from .media_handler import get_media_type, format_media_info
from .metrics import get_metrics, TimingContext

logger = setup_logger(__name__)
metrics = get_metrics()


class TGecommClient:
    """Telegram client wrapper for TGecomm"""
    
    def __init__(self) -> None:
        """Initialize the Telegram client"""
        Config.validate()
        
        self.client: TelegramClient = TelegramClient(
            Config.SESSION_NAME,
            Config.API_ID,
            Config.API_HASH
        )
    
    def _setup_handlers(self) -> None:
        """Setup event handlers"""
        
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_new_message(event: events.NewMessage.Event) -> None:
            """Handle incoming messages"""
            try:
                sender = await event.get_sender()
                chat = await event.get_chat()
                
                logger.info(f"New message received from {self._get_entity_name(sender)}")
                print(f"\n[New Message]")
                print(f"From: {self._get_entity_name(sender)}")
                print(f"Chat: {self._get_entity_name(chat)}")
                
                # Handle messages with or without text
                if event.message.text:
                    message_text = event.message.text
                elif event.message.media:
                    message_text = format_media_info(event.message.media)
                else:
                    message_text = "[Empty message]"
                
                print(f"Message: {message_text}")
            except Exception as e:
                logger.error(f"Error handling new message: {e}", exc_info=True)
                print(f"✗ Error handling new message: {e}")
    
    @staticmethod
    def _get_entity_name(entity: Optional[Any]) -> str:
        """Get name of an entity (user, chat, or channel)
        
        Args:
            entity: Telegram entity (User, Chat, or Channel)
            
        Returns:
            str: Entity name or "Unknown"
        """
        if entity is None:
            return "Unknown"
        
        if isinstance(entity, User):
            if entity.username:
                return f"@{entity.username}"
            name = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
            return name if name else f"User {entity.id}"
        elif isinstance(entity, (Chat, Channel)):
            return entity.title or "Unknown Chat"
        return "Unknown"
    
    async def __aenter__(self) -> 'TGecommClient':
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.disconnect()
    
    async def start(self) -> None:
        """Start the client
        
        Raises:
            SessionPasswordNeededError: If 2FA password is required
            Exception: If connection fails
        """
        try:
            await self.client.start(phone=Config.PHONE)
            logger.info("Client started successfully")
            print("✓ Client started successfully")
            
            me = await self.client.get_me()
            username = f"@{me.username}" if me.username else "No username"
            logger.info(f"Logged in as: {me.first_name} ({username})")
            print(f"✓ Logged in as: {me.first_name} ({username})")
            
            # Setup handlers after client is started
            self._setup_handlers()
        except SessionPasswordNeededError:
            # Use asyncio.to_thread() to avoid blocking event loop
            password = await asyncio.to_thread(input, "Enter your 2FA password: ")
            await self.client.sign_in(password=password)
            logger.info("2FA authentication successful")
            print("✓ 2FA authentication successful")
            
            # Setup handlers after 2FA authentication
            self._setup_handlers()
        except Exception as e:
            logger.error(f"Error starting client: {e}", exc_info=True)
            print(f"✗ Error starting client: {e}")
            raise
    
    async def send_message(self, recipient: str, message: str) -> bool:
        """Send a message to a recipient
        
        Args:
            recipient: Recipient identifier (username, phone, or chat_id)
            message: Message text to send (max 4096 characters)
            
        Returns:
            bool: True if message was sent successfully
        """
        if not message or not message.strip():
            logger.warning("Attempted to send empty message")
            metrics.record_error("ValidationError", "Empty message", {"recipient": recipient})
            print("✗ Error: Message cannot be empty")
            return False
        
        # Telegram message length limit
        if len(message) > Config.MAX_MESSAGE_LENGTH:
            logger.warning(f"Message length {len(message)} exceeds maximum {Config.MAX_MESSAGE_LENGTH}")
            metrics.record_error("ValidationError", "Message too long", {"length": len(message)})
            print(f"✗ Error: Message too long (max {Config.MAX_MESSAGE_LENGTH} characters)")
            return False
        
        try:
            with TimingContext("send_message", {"recipient": recipient}):
                await self.client.send_message(recipient, message)
            metrics.increment("messages_sent", tags={"recipient": recipient})
            logger.info(f"Message sent to {recipient}")
            print(f"✓ Message sent to {recipient}")
            return True
        except FloodWaitError as e:
            metrics.record_error("FloodWaitError", f"Rate limit: {e.seconds}s", {"recipient": recipient})
            logger.warning(f"Rate limit: wait {e.seconds} seconds")
            print(f"✗ Rate limit: Please wait {e.seconds} seconds before sending again")
            return False
        except (UserInvalidError, ChatInvalidError, NotFoundError) as e:
            metrics.record_error("NotFoundError", f"Recipient not found: {recipient}", {"recipient": recipient})
            logger.error(f"Recipient not found: {recipient}")
            print(f"✗ Error: Recipient '{recipient}' not found")
            return False
        except ChannelPrivateError:
            metrics.record_error("ChannelPrivateError", f"Channel is private: {recipient}", {"recipient": recipient})
            logger.error(f"Channel is private: {recipient}")
            print(f"✗ Error: Channel '{recipient}' is private or you don't have access")
            return False
        except MessageEmptyError:
            metrics.record_error("MessageEmptyError", "Message is empty", {"recipient": recipient})
            logger.warning("Attempted to send empty message")
            print("✗ Error: Message is empty")
            return False
        except Exception as e:
            metrics.record_error("Exception", str(e), {"recipient": recipient, "error_type": type(e).__name__})
            logger.error(f"Error sending message: {e}", exc_info=True)
            print(f"✗ Error sending message: {e}")
            return False
    
    async def get_dialogs(self, limit: int = 10) -> List[Dialog]:
        """Get list of dialogs (chats)
        
        Args:
            limit: Maximum number of dialogs to retrieve (max 10000)
            
        Returns:
            List of Dialog objects
        """
        if limit <= 0:
            logger.warning(f"Invalid limit: {limit}")
            print("✗ Error: Limit must be a positive number")
            return []
        
        # Limit maximum to prevent memory issues
        if limit > Config.MAX_DIALOGS_LIMIT:
            logger.warning(f"Limit {limit} exceeds maximum {Config.MAX_DIALOGS_LIMIT}, using {Config.MAX_DIALOGS_LIMIT}")
            limit = Config.MAX_DIALOGS_LIMIT
        
        try:
            with TimingContext("get_dialogs", {"limit": str(limit)}):
                dialogs = await self.client.get_dialogs(limit=limit)
            
            metrics.increment("dialogs_retrieved", value=len(dialogs) if dialogs else 0)
            
            if not dialogs:
                logger.info("No dialogs found")
                print("No dialogs found")
                return []
            
            logger.info(f"Retrieved {len(dialogs)} dialogs")
            print(f"\nYour dialogs (last {len(dialogs)}):")
            for i, dialog in enumerate(dialogs, 1):
                print(f"{i}. {dialog.name} (ID: {dialog.id})")
            
            return dialogs
        except Exception as e:
            logger.error(f"Error getting dialogs: {e}", exc_info=True)
            print(f"✗ Error getting dialogs: {e}")
            return []
    
    async def get_messages(self, chat: str, limit: int = 10) -> List[Message]:
        """Get messages from a chat
        
        Args:
            chat: Chat identifier (username, phone, or chat_id)
            limit: Maximum number of messages to retrieve (max 10000)
            
        Returns:
            List of Message objects
        """
        if limit <= 0:
            logger.warning(f"Invalid limit: {limit}")
            print("✗ Error: Limit must be a positive number")
            return []
        
        # Limit maximum to prevent memory issues
        if limit > Config.MAX_MESSAGES_LIMIT:
            logger.warning(f"Limit {limit} exceeds maximum {Config.MAX_MESSAGES_LIMIT}, using {Config.MAX_MESSAGES_LIMIT}")
            limit = Config.MAX_MESSAGES_LIMIT
        
        try:
            with TimingContext("get_messages", {"chat": chat, "limit": str(limit)}):
                messages = await self.client.get_messages(chat, limit=limit)
                
                if not messages:
                    logger.info(f"No messages found in {chat}")
                    print(f"No messages found in {chat}")
                    return []
                
                # Batch fetch senders to improve performance
                sender_tasks = [msg.get_sender() for msg in reversed(messages)]
                senders = await asyncio.gather(*sender_tasks, return_exceptions=True)
            
            metrics.increment("messages_retrieved", value=len(messages), tags={"chat": chat})
            
            logger.info(f"Retrieved {len(messages)} messages from {chat}")
            print(f"\nLast {len(messages)} messages from {chat}:")
            
            for msg, sender in zip(reversed(messages), senders):
                try:
                    if isinstance(sender, Exception):
                        sender_name = "Unknown"
                        logger.warning(f"Error getting sender: {sender}")
                    else:
                        sender_name = self._get_entity_name(sender) if sender else "Unknown"
                    
                    # Format date
                    date_str = msg.date.strftime("%Y-%m-%d %H:%M:%S") if msg.date else "Unknown date"
                    
                    # Handle different message types
                    if msg.text:
                        print(f"[{date_str}] {sender_name}: {msg.text}")
                    elif msg.media:
                        media_info = format_media_info(msg.media)
                        print(f"[{date_str}] {sender_name}: {media_info}")
                    else:
                        print(f"[{date_str}] {sender_name}: [Empty message]")
                except Exception as e:
                    logger.warning(f"Error displaying message: {e}")
                    print(f"[Error displaying message: {e}]")
            
            return messages
        except (ChatInvalidError, ChannelPrivateError, NotFoundError) as e:
            metrics.record_error("ChatNotFoundError", f"Chat not found: {chat}", {"chat": chat})
            logger.error(f"Chat not found or inaccessible: {chat}")
            print(f"✗ Error: Chat '{chat}' not found or you don't have access")
            return []
        except Exception as e:
            metrics.record_error("Exception", str(e), {"chat": chat, "error_type": type(e).__name__})
            logger.error(f"Error getting messages: {e}", exc_info=True)
            print(f"✗ Error getting messages: {e}")
            return []
    
    async def run(self) -> None:
        """Run the client until disconnected"""
        logger.info("Client is now running and listening for messages")
        print("\n✓ TGecomm is running... (Press Ctrl+C to stop)")
        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("Client interrupted by user")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect the client"""
        try:
            if self.client.is_connected():
                await self.client.disconnect()
                logger.info("Client disconnected successfully")
                print("✓ Client disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting client: {e}", exc_info=True)
            print(f"✗ Error disconnecting: {e}")
