"""
User Interface module for TGecomm
"""
from typing import Optional, Tuple, List, Dict, Any
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.prompt import Prompt
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback to colorama if rich is not available
    try:
        from colorama import init, Fore, Style
        init(autoreset=True)
        COLORAMA_AVAILABLE = True
    except ImportError:
        COLORAMA_AVAILABLE = False
        Fore = Style = type('obj', (object,), {'__getattr__': lambda *args: ''})()

from .validators import validate_positive_integer, validate_recipient, ValidationError
from .logger import setup_logger

logger = setup_logger(__name__)

# Initialize Rich console if available
if RICH_AVAILABLE:
    console = Console()


class ConsoleUI:
    """Console-based user interface"""
    
    @staticmethod
    def print_header() -> None:
        """Print application header"""
        if RICH_AVAILABLE:
            header = Panel.fit(
                "[bold cyan]TGecomm[/bold cyan] - Telegram Client",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(header)
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.CYAN}{'='*50}")
            print(f"{Fore.CYAN}TGecomm - Telegram Client{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        else:
            print("="*50)
            print("TGecomm - Telegram Client")
            print("="*50)
    
    @staticmethod
    def print_menu() -> None:
        """Print interactive menu"""
        if RICH_AVAILABLE:
            table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
            table.add_row("[bold]Options:[/bold]")
            table.add_row("1. Send a message")
            table.add_row("2. View messages from a chat")
            table.add_row("3. List dialogs")
            table.add_row("4. Keep running and listen for messages")
            table.add_row("5. Show metrics")
            table.add_row("0. Exit")
            console.print("\n")
            console.print(table)
        else:
            print("\n" + "="*50)
            print("Options:")
            print("1. Send a message")
            print("2. View messages from a chat")
            print("3. List dialogs")
            print("4. Keep running and listen for messages")
            print("5. Show metrics")
            print("0. Exit")
            print("="*50)
    
    @staticmethod
    def get_choice() -> str:
        """Get user menu choice"""
        if RICH_AVAILABLE:
            return Prompt.ask("\n[cyan]Choose an option[/cyan]", choices=["0", "1", "2", "3", "4", "5"], default="0")
        else:
            return input("\nChoose an option (0-5): ").strip()
    
    @staticmethod
    def get_send_message_input() -> Tuple[Optional[str], Optional[str]]:
        """Get input for sending a message
        
        Returns:
            Tuple of (recipient, message) or (None, None) if invalid
        """
        if RICH_AVAILABLE:
            recipient = Prompt.ask("[cyan]Enter recipient[/cyan] (username/phone/chat_id)")
        else:
            recipient = input("Enter recipient (username/phone/chat_id): ").strip()
        
        recipient = recipient.strip()
        
        if not validate_recipient(recipient):
            logger.warning(f"Invalid recipient format: {recipient}")
            ConsoleUI.print_error("Invalid recipient format. Use @username, +phone, or numeric ID")
            return None, None
        
        if RICH_AVAILABLE:
            message = Prompt.ask("[cyan]Enter message[/cyan]")
        else:
            message = input("Enter message: ")
        
        if not message.strip():
            ConsoleUI.print_error("Message cannot be empty")
            return None, None
        
        return recipient, message
    
    @staticmethod
    def get_view_messages_input() -> Tuple[Optional[str], Optional[int]]:
        """Get input for viewing messages
        
        Returns:
            Tuple of (chat, limit) or (None, None) if invalid
        """
        if RICH_AVAILABLE:
            chat = Prompt.ask("[cyan]Enter chat[/cyan] (username/phone/chat_id)")
        else:
            chat = input("Enter chat (username/phone/chat_id): ").strip()
        
        chat = chat.strip()
        
        if not validate_recipient(chat):
            logger.warning(f"Invalid chat format: {chat}")
            ConsoleUI.print_error("Invalid chat format. Use @username, +phone, or numeric ID")
            return None, None
        
        if RICH_AVAILABLE:
            limit_str = Prompt.ask("[cyan]Number of messages[/cyan]", default="10")
        else:
            limit_str = input("Number of messages (default 10): ").strip()
        
        try:
            limit = validate_positive_integer(limit_str, "Number of messages") if limit_str else 10
            return chat, limit
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            ConsoleUI.print_error(str(e))
            return None, None
    
    @staticmethod
    def get_list_dialogs_input() -> Optional[int]:
        """Get input for listing dialogs
        
        Returns:
            Limit value or None if invalid
        """
        if RICH_AVAILABLE:
            limit_str = Prompt.ask("[cyan]Number of dialogs[/cyan]", default="10")
        else:
            limit_str = input("Number of dialogs (default 10): ").strip()
        
        try:
            limit = validate_positive_integer(limit_str, "Number of dialogs") if limit_str else 10
            return limit
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            ConsoleUI.print_error(str(e))
            return None
    
    @staticmethod
    def print_success(message: str) -> None:
        """Print success message"""
        if RICH_AVAILABLE:
            console.print(f"[bold green]✓[/bold green] {message}")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        else:
            print(f"✓ {message}")
    
    @staticmethod
    def print_error(message: str) -> None:
        """Print error message"""
        if RICH_AVAILABLE:
            console.print(f"[bold red]✗[/bold red] {message}")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
        else:
            print(f"✗ {message}")
    
    @staticmethod
    def print_info(message: str) -> None:
        """Print info message"""
        if RICH_AVAILABLE:
            console.print(f"[cyan]ℹ[/cyan] {message}")
        else:
            print(message)
    
    @staticmethod
    def print_warning(message: str) -> None:
        """Print warning message"""
        if RICH_AVAILABLE:
            console.print(f"[bold yellow]⚠[/bold yellow] {message}")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
        else:
            print(f"⚠ {message}")
    
    @staticmethod
    def print_table(data: List[Dict[str, str]], title: Optional[str] = None) -> None:
        """Print data as a table
        
        Args:
            data: List of dictionaries with data
            title: Optional table title
        """
        if RICH_AVAILABLE and data:
            table = Table(title=title, box=box.ROUNDED, show_header=True)
            
            # Get headers from first row
            headers = list(data[0].keys())
            for header in headers:
                table.add_column(header, style="cyan")
            
            # Add rows
            for row in data:
                table.add_row(*[str(row.get(header, "")) for header in headers])
            
            console.print(table)
        else:
            # Fallback to simple print
            if title:
                print(f"\n{title}")
            if data:
                headers = list(data[0].keys())
                print(" | ".join(headers))
                print("-" * (sum(len(h) for h in headers) + len(headers) * 3))
                for row in data:
                    print(" | ".join(str(row.get(header, "")) for header in headers))
    
    @staticmethod
    def print_metrics(metrics_summary: Dict[str, Any]) -> None:
        """Print metrics summary
        
        Args:
            metrics_summary: Dictionary with metrics data
        """
        if RICH_AVAILABLE:
            table = Table(title="Metrics Summary", box=box.ROUNDED, show_header=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Uptime", metrics_summary.get('uptime_formatted', 'N/A'))
            table.add_row("Total Metrics", str(metrics_summary.get('total_metrics', 0)))
            table.add_row("Errors", str(metrics_summary.get('error_count', 0)))
            
            # Add counters
            counters = metrics_summary.get('counters', {})
            for name, value in counters.items():
                table.add_row(f"Counter: {name}", str(value))
            
            console.print("\n")
            console.print(table)
        else:
            print("\n=== Metrics Summary ===")
            print(f"Uptime: {metrics_summary.get('uptime_formatted', 'N/A')}")
            print(f"Total Metrics: {metrics_summary.get('total_metrics', 0)}")
            print(f"Errors: {metrics_summary.get('error_count', 0)}")
            counters = metrics_summary.get('counters', {})
            for name, value in counters.items():
                print(f"{name}: {value}")
