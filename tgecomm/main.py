"""
TGecomm - Main entry point
"""
import asyncio
import sys
import argparse
import logging
from .config import Config
from .client import TGecommClient
from .ui import ConsoleUI
from .logger import setup_logger
from .metrics import get_metrics

logger = setup_logger(__name__)
metrics = get_metrics()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='TGecomm - Telegram Client Application',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--env',
        type=str,
        default='.env',
        help='Path to .env file (default: .env)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    return parser.parse_args()


async def main() -> None:
    """Main application entry point"""
    args = parse_args()
    
    # Load environment from specified file before initializing client
    Config.load_env(args.env)
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    ui = ConsoleUI()
    ui.print_header()
    
    try:
        async with TGecommClient() as client:
            # Interactive menu loop
            while True:
                ui.print_menu()
                choice = ui.get_choice()
                
                if choice == "0":
                    print("Exiting...")
                    break
                
                elif choice == "1":
                    recipient, message = ui.get_send_message_input()
                    if recipient and message:
                        await client.send_message(recipient, message)
                
                elif choice == "2":
                    chat, limit = ui.get_view_messages_input()
                    if chat and limit:
                        await client.get_messages(chat, limit=limit)
                
                elif choice == "3":
                    limit = ui.get_list_dialogs_input()
                    if limit:
                        await client.get_dialogs(limit=limit)
                
                elif choice == "4":
                    await client.run()
                    break
                
                elif choice == "5":
                    # Show metrics
                    metrics_summary = metrics.get_summary()
                    ui.print_metrics(metrics_summary)
                
                else:
                    ui.print_error("Invalid option. Please choose 0-5.")
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n\nInterrupted by user")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n✗ Configuration error: {e}")
        print("\nPlease check your .env file and ensure all values are correct.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
