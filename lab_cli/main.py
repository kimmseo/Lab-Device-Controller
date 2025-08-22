import typer
from rich.console import Console
from rich.table import Table
import time
import random

# Create a Typer application instance
app = typer.Typer(
    help="CLI to monitor the status of lab equipment.",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False
)

# Initialize Rich console
console = Console()

# --- Mock Data ---
# In a real application, this data would come from a database, API,
# or direct communication with the equipment <- preferred
MOCK_EQUIPMENT_DATA = {
    "laser-01": {
        "type": "Laser_1",
        "status": "Active",
        "power_mw": 10.00,
        "wavelength_nm": 1550.00,
        "last_check": "2025-08-22 12:30:15",    # Datetime format
        "operator": "Dr. Evelyn Reed",
    },
}

# --- Helper Functions ---

def get_status_color(status: str) -> str:
    """Returns a color string for Rich based on the equipment status."""
    status = status.lower()
    if status == "active":
        return "green"
    elif status == "idle":
        return "yellow"
    elif status == "error":
        return "bold red"
    elif status == "maintenance":
        return "cyan"
    return "white"


# --- CLI Commands ---

@app.command(name="list", help="List all available lab equipment and their current status.")
def list_equipment():
    """
    Displays a summary table of all equipment.
    This function simulates fetching the status for all devices and
    presents it in a clean, readable table.
    """
    console.print("\n[bold blue]Lab Equipment Status Overview[/bold blue]")

    # Create a table using Rich
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=15)
    table.add_column("Type")
    table.add_column("Status", justify="center")
    table.add_column("Last Checked")

    with console.status("[bold green]Fetching latest equipment data...[/bold green]"):
        time.sleep(0.5) # Simulate network delay

        # Populate the table with mock data
        for eq_id, data in MOCK_EQUIPMENT_DATA.items():
            status = data.get("status", "Unknown")
            status_color = get_status_color(status)
            table.add_row(
                eq_id,
                data.get("type", "N/A"),
                f"[{status_color}]{status}[/{status_color}]",
                data.get("last_check", "N/A"),
            )

    console.print(table)
    console.print("Use '[bold]status <ID>[/bold]' to see more details for a specific device.\n")


@app.command(name="status", help="Get the detailed status of a specific piece of equipment.")
def get_status(
    equipment_id: str = typer.Argument(
        ...,    # requires arguments
        help="The unique identifier for the equipment (e.g., 'laser_1').",
        metavar="EQUIPMENT_ID"
    )
):
    """
    Fetches and displays detailed information for a single piece of equipment.
    Queries the specific device.
    """
    console.print(f"\n[bold blue]Querying status for:[/] [bold yellow]{equipment_id}[/bold yellow]")

    with console.status(f"[bold green]Contacting {equipment_id}...[/bold green]"):
        time.sleep(0.5) # Delay for device connection
        data = MOCK_EQUIPMENT_DATA.get(equipment_id.lower())

    if not data:
        console.print(f"[bold red]Error:[/] Equipment ID '{equipment_id}' not found.")
        raise typer.Exit(code=1)

    status = data.get("status", "Unknown")
    status_color = get_status_color(status)

    # Display details in a formatted table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan")
    table.add_column()

    table.add_row("ID:", equipment_id)
    table.add_row("Type:", data.get("type", "N/A"))
    table.add_row("Status:", f"[{status_color}]{status}[/{status_color}]")
    table.add_row("-" * 10, "-" * 30)   # Separator

    # Add specific details based on equipment status and type
    if status == "Active":
        if "power_mw" in data:
            table.add_row("Power:", f"{data['power_mw']} mW")
        if "wavelength_nm" in data:
            table.add_row("Wavelength:", f"{data['wavelength_nm']} nm")
        if "voltage_v" in data:
            table.add_row("Voltage:", f"{data['voltage_v']} V")
        if "current_a" in data:
            table.add_row("Current:", f"{data['current_a']} A")
    elif status == "Idle":
        if "channels_active" in data:
             table.add_row("Active Channels:", str(data['channels_active']))
    elif status == "Error":
         table.add_row("Error Code:", f"[bold red]{data.get('error_code', 'N/A')}[/bold red]")
         table.add_row("Details:", data.get('details', ''))
    elif status == "Maintenance":
         table.add_row("Details:", data.get('details', ''))

    table.add_row("-" * 10, "-" * 30)
    table.add_row("Operator:", data.get("operator", "N/A"))
    table.add_row("Last Check:", data.get("last_check", "N/A"))

    console.print(table)
    console.print()


if __name__ == "__main__":

    app()
