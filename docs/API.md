# TGecomm API Documentation

## Overview

TGecomm is a Telegram client application built with Python and Telethon. This document describes the API for extending and integrating with TGecomm.

## Architecture

### Module Structure

```
TGecomm/
├── main.py           # Application entry point
├── client.py         # Telegram client wrapper
├── config.py         # Configuration management
├── ui.py             # User interface
├── validators.py     # Input validation
├── logger.py         # Logging configuration
├── media_handler.py  # Media processing utilities
└── metrics.py        # Metrics and monitoring
```

## Core API

### TGecommClient

Main client class for interacting with Telegram.

#### Initialization

```python
from client import TGecommClient

# Using context manager (recommended)
async with TGecommClient() as client:
    # Client is automatically started and connected
    await client.send_message("username", "Hello")
    # Client is automatically disconnected on exit
```

#### Methods

##### `send_message(recipient: str, message: str) -> bool`

Send a message to a recipient.

**Parameters:**
- `recipient` (str): Recipient identifier (username, phone, or chat_id)
- `message` (str): Message text to send (max 4096 characters)

**Returns:**
- `bool`: True if message was sent successfully

**Example:**
```python
success = await client.send_message("@username", "Hello, World!")
if success:
    print("Message sent!")
```

**Raises:**
- Handles `FloodWaitError`, `UserNotFoundError`, `ChatNotFoundError`, `ChannelPrivateError`, `MessageEmptyError`

##### `get_dialogs(limit: int = 10) -> List[Dialog]`

Get list of dialogs (chats).

**Parameters:**
- `limit` (int): Maximum number of dialogs to retrieve (max 10000, configurable via `Config.MAX_DIALOGS_LIMIT`)

**Returns:**
- `List[Dialog]`: List of Dialog objects

**Example:**
```python
dialogs = await client.get_dialogs(limit=20)
for dialog in dialogs:
    print(f"{dialog.name} (ID: {dialog.id})")
```

##### `get_messages(chat: str, limit: int = 10) -> List[Message]`

Get messages from a chat.

**Parameters:**
- `chat` (str): Chat identifier (username, phone, or chat_id)
- `limit` (int): Maximum number of messages to retrieve (max 10000, configurable via `Config.MAX_MESSAGES_LIMIT`)

**Returns:**
- `List[Message]`: List of Message objects

**Example:**
```python
messages = await client.get_messages("@channel", limit=50)
for msg in messages:
    if msg.text:
        print(f"{msg.date}: {msg.text}")
```

##### `run() -> None`

Run the client until disconnected. Listens for incoming messages.

**Example:**
```python
await client.run()  # Blocks until Ctrl+C or disconnect
```

##### `disconnect() -> None`

Manually disconnect the client.

**Example:**
```python
await client.disconnect()
```

#### Event Handlers

The client automatically sets up event handlers for incoming messages. You can extend this by modifying `_setup_handlers()`:

```python
def _setup_handlers(self) -> None:
    @self.client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event: events.NewMessage.Event) -> None:
        # Custom handler logic
        pass
```

## Configuration API

### Config Class

Configuration management class.

#### Class Variables

- `API_ID: Optional[int]` - Telegram API ID
- `API_HASH: Optional[str]` - Telegram API Hash
- `PHONE: Optional[str]` - Phone number
- `SESSION_NAME: str` - Session file name (default: 'tgecomm_session')
- `MAX_MESSAGE_LENGTH: int` - Maximum message length (default: 4096)
- `MAX_DIALOGS_LIMIT: int` - Maximum dialogs limit (default: 10000)
- `MAX_MESSAGES_LIMIT: int` - Maximum messages limit (default: 10000)

#### Methods

##### `load_env(env_file: str = '.env') -> None`

Load environment variables from file.

**Parameters:**
- `env_file` (str): Path to .env file

##### `validate() -> bool`

Validate required configuration.

**Returns:**
- `bool`: True if validation passes

**Raises:**
- `ValueError`: If validation fails

##### `get_masked_config() -> Dict[str, Optional[str]]`

Get configuration with masked sensitive data for logging.

**Returns:**
- `Dict[str, Optional[str]]`: Masked configuration values

## Validation API

### Validators Module

Input validation utilities.

#### Functions

##### `validate_phone_number(phone: str) -> bool`

Validate phone number format.

**Parameters:**
- `phone` (str): Phone number to validate

**Returns:**
- `bool`: True if valid

##### `validate_username(username: str) -> bool`

Validate Telegram username format.

**Parameters:**
- `username` (str): Username to validate (with or without @)

**Returns:**
- `bool`: True if valid

##### `validate_recipient(recipient: str) -> bool`

Validate recipient (can be username, phone, or chat ID).

**Parameters:**
- `recipient` (str): Recipient identifier

**Returns:**
- `bool`: True if valid format

##### `validate_api_id(api_id: Optional[str]) -> bool`

Validate API ID format.

**Parameters:**
- `api_id` (Optional[str]): API ID to validate

**Returns:**
- `bool`: True if valid

##### `validate_api_hash(api_hash: str) -> bool`

Validate API Hash format (should be 32 hex characters).

**Parameters:**
- `api_hash` (str): API Hash to validate

**Returns:**
- `bool`: True if valid

##### `validate_positive_integer(value: str, field_name: str = "value") -> int`

Validate that value is a positive integer.

**Parameters:**
- `value` (str): String to validate
- `field_name` (str): Name of the field for error messages

**Returns:**
- `int`: Validated integer value

**Raises:**
- `ValidationError`: If validation fails

##### `mask_sensitive_data(data: Optional[str], visible_chars: int = 4) -> str`

Mask sensitive data for logging.

**Parameters:**
- `data` (Optional[str]): Data to mask
- `visible_chars` (int): Number of characters to show at the end

**Returns:**
- `str`: Masked string

## Metrics API

### MetricsCollector Class

Collects and stores application metrics.

#### Methods

##### `increment(name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None`

Increment a counter metric.

**Parameters:**
- `name` (str): Metric name
- `value` (int): Increment value (default: 1)
- `tags` (Optional[Dict[str, str]]): Optional tags for the metric

##### `record_timing(name: str, duration: float, tags: Optional[Dict[str, str]] = None) -> None`

Record a timing metric.

**Parameters:**
- `name` (str): Metric name
- `duration` (float): Duration in seconds
- `tags` (Optional[Dict[str, str]]): Optional tags

##### `record_error(error_type: str, error_message: str, context: Optional[Dict[str, any]] = None) -> None`

Record an error.

**Parameters:**
- `error_type` (str): Type of error
- `error_message` (str): Error message
- `context` (Optional[Dict[str, any]]): Optional context information

##### `get_counter(name: str) -> int`

Get counter value.

**Parameters:**
- `name` (str): Counter name

**Returns:**
- `int`: Counter value

##### `get_timing_stats(name: str) -> Dict[str, float]`

Get timing statistics.

**Parameters:**
- `name` (str): Timer name

**Returns:**
- `Dict[str, float]`: Dictionary with min, max, avg, count

##### `get_summary() -> Dict[str, any]`

Get metrics summary.

**Returns:**
- `Dict[str, any]`: Dictionary with metrics summary

#### Global Functions

##### `get_metrics() -> MetricsCollector`

Get global metrics collector instance.

**Returns:**
- `MetricsCollector`: MetricsCollector instance

##### `reset_metrics() -> None`

Reset global metrics.

#### TimingContext

Context manager for timing operations.

**Example:**
```python
from metrics import TimingContext

with TimingContext("operation_name"):
    # Your code here
    pass
# Automatically records timing
```

## Media Handler API

### Media Handler Module

Media processing utilities.

#### Functions

##### `get_media_type(media: Any) -> str`

Get human-readable media type name.

**Parameters:**
- `media` (Any): Telegram media object

**Returns:**
- `str`: Media type name

##### `format_media_info(media: Any) -> str`

Format media information for display.

**Parameters:**
- `media` (Any): Telegram media object

**Returns:**
- `str`: Formatted media information string

## UI API

### ConsoleUI Class

Console-based user interface.

#### Methods

All methods are static and can be called directly:

- `print_header() -> None` - Print application header
- `print_menu() -> None` - Print interactive menu
- `get_choice() -> str` - Get user menu choice
- `get_send_message_input() -> Tuple[Optional[str], Optional[str]]` - Get input for sending a message
- `get_view_messages_input() -> Tuple[Optional[str], Optional[int]]` - Get input for viewing messages
- `get_list_dialogs_input() -> Optional[int]` - Get input for listing dialogs
- `print_success(message: str) -> None` - Print success message
- `print_error(message: str) -> None` - Print error message
- `print_info(message: str) -> None` - Print info message
- `print_warning(message: str) -> None` - Print warning message
- `print_table(data: List[Dict[str, str]], title: Optional[str] = None) -> None` - Print data as a table
- `print_metrics(metrics_summary: Dict[str, any]) -> None` - Print metrics summary

## Logging API

### Logger Module

Logging configuration.

#### Functions

##### `setup_logger(name: str, level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger`

Setup and configure logger.

**Parameters:**
- `name` (str): Logger name
- `level` (int): Logging level (default: INFO)
- `log_file` (Optional[str]): Optional path to log file

**Returns:**
- `logging.Logger`: Configured logger instance

## Extension Examples

### Custom Event Handler

```python
from client import TGecommClient
from telethon import events

class CustomClient(TGecommClient):
    def _setup_handlers(self) -> None:
        super()._setup_handlers()
        
        @self.client.on(events.NewMessage(outgoing=True))
        async def handle_outgoing_message(event):
            print(f"Sent: {event.message.text}")
```

### Custom Metrics

```python
from metrics import get_metrics, TimingContext

metrics = get_metrics()

# Record custom metric
metrics.increment("custom_action", tags={"type": "example"})

# Time an operation
with TimingContext("custom_operation"):
    # Your code
    pass
```

### Custom Validator

```python
from validators import ValidationError

def validate_custom_field(value: str) -> bool:
    """Custom validation logic"""
    if not value or len(value) < 5:
        return False
    return True
```

## Error Handling

All methods handle errors gracefully and return appropriate values:

- `send_message()` returns `False` on error
- `get_dialogs()` returns empty list on error
- `get_messages()` returns empty list on error

Errors are logged and recorded in metrics automatically.

## Thread Safety

- The client is designed for single-threaded async usage
- Metrics collector is thread-safe for basic operations
- Configuration is read-only after initialization

## Best Practices

1. **Always use context manager** for client initialization
2. **Handle errors** - check return values
3. **Use metrics** to monitor performance
4. **Validate input** before sending messages
5. **Respect rate limits** - handle FloodWaitError appropriately
6. **Log important operations** for debugging

## Version Compatibility

- Python 3.12+
- Telethon >= 1.34.0
- Rich >= 13.0.0 (optional, for enhanced UI)

## License

See LICENSE file for details.

