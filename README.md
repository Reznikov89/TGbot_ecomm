# TGecomm

Telegram client application built with Telethon library.

## Description
TGecomm is a Python-based Telegram client that allows you to:
- Send and receive messages
- View chat history
- List your dialogs
- Monitor incoming messages in real-time

## Requirements
- Python 3.12+
- Telegram API credentials (API ID and API Hash)

## Setup

### 1. Get Telegram API Credentials
1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Copy your `api_id` and `api_hash`

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Configuration
1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

2. Edit `.env` and add your credentials:
```
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=+1234567890
```

## Usage
```bash
# Activate virtual environment first
.\venv\Scripts\Activate.ps1  # PowerShell
# or
venv\Scripts\activate.bat     # CMD

# Run the application
python main.py
```

On first run, you'll need to:
1. Enter the verification code sent to your Telegram account
2. If you have 2FA enabled, enter your password

## Features
- **Send Messages**: Send messages to any user or chat
- **View Messages**: Read message history from any chat
- **List Dialogs**: See your recent conversations
- **Real-time Monitoring**: Listen for incoming messages

## Project Structure
```
TGecomm/
├── main.py              # Application entry point
├── tgecomm/             # Main package
│   ├── __init__.py      # Package initialization
│   ├── main.py          # Main application logic
│   ├── client.py        # Telegram client wrapper
│   ├── config.py        # Configuration management
│   ├── ui.py            # User interface
│   ├── validators.py    # Input validation
│   ├── logger.py        # Logging configuration
│   ├── media_handler.py # Media processing utilities
│   └── metrics.py       # Metrics and monitoring
├── tests/               # Test suite
│   ├── test_client.py
│   ├── test_config.py
│   ├── test_ui.py
│   ├── test_validators.py
│   └── test_logger.py
├── docs/                # Documentation
│   └── API.md           # API documentation
├── requirements.txt      # Python dependencies
├── pytest.ini           # Pytest configuration
├── README.md            # This file
├── .env                 # Environment variables (create from .env.example)
└── .env.example         # Example environment configuration
```

## Security Notes
- Never commit your `.env` file or session files
- Keep your API credentials secure
- Session files contain authentication tokens
