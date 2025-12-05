# Last updated 5 Dec 2025
import time
from rich.console import Console
from . import register_action

console = Console()

@register_action("delay")
def action_delay(seconds: float, context: dict = None):
    """Waits for a specified duration in seconds."""
    console.print(f"[yellow]Waiting {seconds}s...[/yellow]")
    time.sleep(float(seconds))
    return True

@register_action("log")
def action_log(message: str, context: dict = None):
    """Prints a message to the console (useful for experiment notes)."""
    # Replace variables like {field} in the message
    formatted_msg = message.format(**(context or {}))
    console.print(f"[bold cyan]LOG:[/bold cyan] {formatted_msg}")
    return True
