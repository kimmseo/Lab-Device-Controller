import typer
import time
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live
import shlex

# Import from centralised API commands
from .equipment_api import get_all_equipment, get_equipment_by_id

app = typer.Typer(
    help="CLI to monitor the status of lab equipment.",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False
)

console = Console()

@app.command("status")
def status_monitor(refresh_rate: float = 2.0):
    """
    Continuously monitors and displays the status of all connected equipment.
    Press Ctrl+C to exit.
    """
    console.print("[bold blue]Starting Equipment Monitor... (Press Ctrl+C to stop)[/bold blue]")

    try:
        # Create a Live display that updates automatically
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                # 1. Fetch live data using our new API
                equipment_data = get_all_equipment()

                # 2. Build the table
                table = Table(title=f"Lab Equipment Status (Updated: {time.strftime('%H:%M:%S')})")
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Type", style="magenta")
                table.add_column("Status", justify="center")
                table.add_column("Key Readings", style="green")
                table.add_column("Details", style="white")

                # 3. Populate rows based on the Equipment Models
                for eq_id, data in equipment_data.items():

                    # Determine Status Color
                    status_style = "green" if data.get("status") == "Active" else "red"
                    if data.get("status") == "Idle": status_style = "yellow"

                    # Format Key Readings based on device type
                    readings = []
                    if "temperature_k" in data:
                        readings.append(f"{data['temperature_k']:.2f} K")
                    if "pressure_torr" in data:
                        readings.append(f"{data['pressure_torr']:.2e} Torr")
                    if "magnet_field_tesla" in data:
                        readings.append(f"{data['magnet_field_tesla']:.4f} T")
                    if "wavelength_nm" in data:
                        readings.append(f"{data['wavelength_nm']:.2f} nm")
                    if "power_mw" in data:
                        readings.append(f"{data['power_mw']:.2f} mW")

                    readings_str = ", ".join(readings) if readings else "-"

                    table.add_row(
                        eq_id,
                        data.get("type", "Unknown"),
                        f"[{status_style}]{data.get('status', 'Unknown')}[/{status_style}]",
                        readings_str,
                        str(data.get("details", ""))
                    )

                live.update(table)
                time.sleep(refresh_rate)

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Monitor stopped.[/bold yellow]")


@app.command("inspect")
def inspect_device(device_id: str):
    """
    Get detailed information for a specific device by ID.
    Example: inspect laser-01
    """
    console.print(f"[bold]Querying device: {device_id}...[/bold]")

    data = get_equipment_by_id(device_id)

    if not data:
        console.print(f"[bold red]Error:[/bold red] Device ID '{device_id}' not found.")
        return

    # specific formatting for the inspection view
    console.print(f"\n[bold underline]Device Report: {device_id}[/bold underline]")
    for key, value in data.items():
        console.print(f"[cyan]{key}:[/cyan] {value}")


@app.command("shell")
def interactive_shell():
    """
    Starts an interactive shell session.
    """
    console.print("\n[bold green]Entering interactive lab shell.[/bold green]")
    console.print("Type '[bold cyan]exit[/bold cyan]' to leave.")

    while True:
        try:
            command = Prompt.ask("[bold magenta]lab-cli >[/bold magenta]", default="")

            if command.lower() in ["exit", "quit"]:
                console.print("[bold yellow]Exiting shell.[/bold yellow]")
                break

            if not command.strip():
                continue

            # Process command
            args = shlex.split(command)

            # Run the typer command programmatically
            try:
                app(args, standalone_mode=False)
            except SystemExit:
                pass # Prevent the shell from closing on command exit
            except Exception as e:
                console.print(f"[bold red]Error running command:[/bold red] {e}")

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Exiting shell.[/bold yellow]")
            break

if __name__ == "__main__":
    app()
