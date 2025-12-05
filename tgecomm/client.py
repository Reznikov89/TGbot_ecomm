import asyncio
import getpass
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
    """Telegram client wrapper for TGecomm with improved reliability"""
    
    def __init__(self) -> None:
        """Initialize the Telegram client"""
        Config.validate()
        
        if not all([Config.API_ID, Config.API_HASH, Config.PHONE]):
            raise ValueError(
                "Missing required configuration: API_ID, API_HASH, PHONE"
            )
        
        self.client: TelegramClient = TelegramClient(
            Config.SESSION_NAME,
            Config.API_ID,
            Config.API_HASH
        )
        
        # FIX: Флаг для предотвращения дублирования handlers
        self._handlers_setup = False
        self._send_lock = asyncio.Lock()
        self._handlers_lock = asyncio.Lock()
    
    async def _setup_handlers(self) -> None:
        """Setup event handlers (called once only) - thread-safe"""
        
        # Double-checked locking pattern для предотвращения race condition
        if self._handlers_setup:
            logger.debug("Handlers already setup, skipping")
            return
        
        async with self._handlers_lock:
            # Проверяем еще раз после получения блокировки
            if self._handlers_setup:
                logger.debug("Handlers already setup, skipping (double-check)")
                return
            
            @self.client.on(events.NewMessage(incoming=True))
            async def handle_new_message(event: events.NewMessage.Event) -> None:   
                """Handle incoming messages"""
                try:
                    sender = await event.get_sender()
                    chat = await event.get_chat()
                except Exception as e:
                    logger.error(f"Error handling new message: {e}", exc_info=True)
            
            self._handlers_setup = True
            logger.debug("Handlers setup completed")
    
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
    
    async def _batch_fetch_senders(self, messages: List[Message], batch_size: int = 5) -> List[Any]:
        """Fetch senders in batches to avoid rate limiting
        
        Args:
            messages: List of message objects
            batch_size: Number of messages per batch (default: 5)
            
        Returns:
            List of sender objects (or exceptions)
        """
        senders = []
        total_batches = (len(messages) + batch_size - 1) // batch_size
        
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.debug(f"Fetching senders batch {batch_num}/{total_batches} ({len(batch)} messages)")
            
            batch_senders = await asyncio.gather(
                *[msg.get_sender() for msg in batch],
                return_exceptions=True
            )
            senders.extend(batch_senders)
            
            # Небольшая задержка между батчами для предотвращения rate limiting
            # (кроме последнего батча)
            if i + batch_size < len(messages):
                await asyncio.sleep(0.1)  # 100ms задержка между батчами
        
        return senders
    
    async def send_message(self, recipient: str, message: str) -> bool:
        """Send a message to a recipient (thread-safe)
        
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
            async with self._send_lock:
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
                
                # Batch fetch senders to avoid rate limiting
                senders = await self._batch_fetch_senders(
                    list(reversed(messages)),
                    batch_size=5
                )
            
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
    
    async def run(self, max_retries: int = 5) -> None:
        """Run the client until disconnected with automatic reconnection
        
        Args:
            max_retries: Maximum number of reconnection attempts (default: 5)
        """
        logger.info("Client is now running and listening for messages")
        print("\n✓ TGecomm is running... (Press Ctrl+C to stop)")
        
        for attempt in range(max_retries):
            try:
                await self.client.run_until_disconnected()
                break
            except KeyboardInterrupt:
                logger.info("Client interrupted by user")
                raise
            except Exception as e:
                logger.error(f"Connection lost: {e}", exc_info=True)
                metrics.record_error("ConnectionError", str(e), {"attempt": attempt + 1})
                
                if attempt < max_retries - 1:
                    wait_time = 5 * 60  # 5 минут в секундах
                    logger.info(f"Attempting to reconnect in {wait_time // 60} minutes... (attempt {attempt + 1}/{max_retries})")
                    print(f"⚠ Connection lost. Reconnecting in {wait_time // 60} minutes... (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    
                    # Попытка переподключения
                    try:
                        if not self.client.is_connected():
                            logger.info("Reconnecting to Telegram...")
                            await self.client.connect()
                            if not await self.client.is_user_authorized():
                                await self.client.start(phone=Config.PHONE)
                            logger.info("Reconnected successfully")
                            print("✓ Reconnected successfully")
                    except Exception as reconnect_error:
                        logger.error(f"Reconnection failed: {reconnect_error}", exc_info=True)
                        print(f"✗ Reconnection failed: {reconnect_error}")
                else:
                    logger.error(f"Max retries ({max_retries}) reached. Giving up.")
                    print(f"✗ Max retries ({max_retries}) reached. Giving up.")
                    raise
