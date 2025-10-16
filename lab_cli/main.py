import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import shlex # for safe argument splitting
import time
import random

# Connections
from .connections.oscilloscope import connect_oscilloscope
from .connections.laser import connect_laser_via_server

# Data models
from .models import create_equipment_model, Laser, Oscilloscope, PowerSupply, Spectrometer, MaintenanceDevice # <-- ADD THIS

# Create a Typer application instance
app = typer.Typer(
    help="CLI to monitor the status of lab equipment.",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False
)

# Initialize Rich console
console = Console()

# Mock data for placeholder
MOCK_EQUIPMENT_DATA = {
    "laser-01": {
        "type": "Femtosecond Laser",
        "status": "Active",
        "power_mw": 10.00,
        "wavelength_nm": 1550,
        "last_check": "2025-08-22 12:30:15",
        "operator": "Dr. Evelyn Reed",
    },
    # Placeholder for oscilloscope
    "scope-01": { # <-- ADD THIS BLOCK
        "type": "Digital Oscilloscope",
        "status": "Idle",
        "details": "Awaiting connection...",
        "last_check": "N/A",
        "operator": "N/A"
    }
}

# Helper functions
def get_status_color(status: str) -> str:
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

# CLI Commands
@app.command(name="list", help="List all available lab equipment and their current status.")
def list_equipment():
    console.print("\n[bold blue]Lab Equipment Status Overview[/bold blue]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=15)
    table.add_column("Type")
    table.add_column("Status", justify="center")
    table.add_column("Last Checked")
    with console.status("[bold green]Fetching latest equipment data...[/bold green]"):
        time.sleep(0.5)
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
    console.print("Use '[bold]status <ID>[/bold]' or '[bold]connect <ID>[/bold]' for more actions.\n")


@app.command(name="status", help="Get the detailed status of a specific piece of equipment.")
def get_status(
    equipment_id: str = typer.Argument(
        ...,
        help="The unique identifier for the equipment (e.g., 'laser-01').",
        metavar="EQUIPMENT_ID"
    )
):
    """
    Fetches and displays detailed information for a single piece of equipment.
    Refactored to use the dataclass factory from models.py.
    """
    console.print(f"\n[bold blue]Querying status for:[/] [bold yellow]{equipment_id}[/bold yellow]")
    with console.status(f"[bold green]Fetching data for {equipment_id}...[/bold green]"):
        time.sleep(0.5)
        data = MOCK_EQUIPMENT_DATA.get(equipment_id.lower())

    if not data:
        console.print(f"[bold red]Error:[/] Equipment ID '{equipment_id}' not found.")
        raise typer.Exit(code=1)

    # Create structed object using factory
    equipment = create_equipment_model(equipment_id, data)

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan")
    table.add_column()

    status_color = get_status_color(equipment.status)
    table.add_row("ID:", equipment.id)
    table.add_row("Type:", equipment.type)
    table.add_row("Status:", f"[{status_color}]{equipment.status}[/{status_color}]")
    table.add_row("-" * 10, "-" * 30)

    # Display details based on object types
    if isinstance(equipment, Oscilloscope):
        table.add_row("Active Channels:", str(equipment.channels_active or "N/A"))
        table.add_row("Sample Rate:", f"{equipment.sample_rate_gs or 'N/A'} Gs/S")
        if equipment.details:
            table.add_row("Details:", equipment.details)
    elif isinstance(equipment, Laser):
        table.add_row("Power:", f"{equipment.power_mw} mW")
        table.add_row("Wavelength:", f"{equipment.wavelength_nm} nm")
    # for other objects
    elif isinstance(equipment, (Spectrometer, MaintenanceDevice)):
         table.add_row("Details:", equipment.details or 'N/A')

    table.add_row("-" * 10, "-" * 30)
    table.add_row("Operator:", equipment.operator or "N/A")
    table.add_row("Last Check:", equipment.last_check or "N/A")
    console.print(table)

# Command to connect to hardware
@app.command(name="connect", help="Connect to a piece of equipment to get live data.")
def connect_to_device(
    equipment_id: str = typer.Argument(
        ...,
        help="The ID of the equipment to connect to (e.g., 'scope-01').",
        metavar="EQUIPMENT_ID"
    )
):
    """
    Connects to physical hardware and updates its status.
    """
    equipment_id = equipment_id.lower()
    if "scope" not in equipment_id:
        console.print(f"[bold red]Error:[/] Connection logic for '{equipment_id}' is not implemented.")
        raise typer.Exit(code=1)

    with console.status(f"[bold green]Connecting to {equipment_id} via VISA...[/bold green]"):
        scope = connect_oscilloscope()



    if not scope:
        console.print(f"[bold red]Failed to connect to {equipment_id}.[/bold red] Check network and VISA drivers.")
        MOCK_EQUIPMENT_DATA[equipment_id]['status'] = 'Error'
        MOCK_EQUIPMENT_DATA[equipment_id]['details'] = 'Connection via VISA failed.'
        raise typer.Exit(code=1)

    # If connection success get live data
    try:
        idn = scope.query("*IDN?").strip()
        console.print(f"[bold green]Successfully connected![/bold green]")
        console.print(f"[bold]Device ID:[/bold] {idn}")

        # Update db with live data
        MOCK_EQUIPMENT_DATA[equipment_id]['status'] = 'Active'
        MOCK_EQUIPMENT_DATA[equipment_id]['details'] = idn # Store the ID string
        MOCK_EQUIPMENT_DATA[equipment_id]['last_check'] = time.strftime("%Y-%m-%d %H:%M:%S")
        MOCK_EQUIPMENT_DATA[equipment_id]['operator'] = "CLI User"

    except Exception as e:
        console.print(f"[bold red]Error during communication: {e}[/bold red]")
    finally:
        scope.close()   # IMPORTANT: Always close the connection
        console.print("   Connection closed.")

@app.command(name="shell", help="Enter an interactive shell to run multiple commands.")
def shell():
    """
    Starts an interactive session to run multiple commands without exiting.
    """
    console.print("\n[bold green]Entering interactive lab shell.[/bold green]")
    console.print("Type '[bold cyan]exit[/bold cyan]' or '[bold cyan]quit[/bold cyan]' to leave.")

    while True:
        try:
            command = Prompt.ask("[bold magenta]lab-cli >[/bold magenta]", default="")

            if command.lower() in ["exit", "quit"]:
                console.print("[bold yellow]Exiting shell.[/bold yellow]")
                break

            if not command.strip():
                continue

            args = shlex.split(command)

            # Programmatically invoke the Typer app with the parsed arguments
            # We wrap this in a try/except block to catch sys.exit()
            try:
                app(args, standalone_mode=False)
            except SystemExit as e:
                # A non-zero exit code from Typer usually means an error occurred
                # (e.g., command not found, bad argument). We can ignore code 0.
                if e.code != 0:
                     console.print(f"[bold red]Command finished with error code: {e.code}[/bold red]")

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print("\n[bold yellow]Exiting shell.[/bold yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")

if __name__ == "__main__":
    app()
