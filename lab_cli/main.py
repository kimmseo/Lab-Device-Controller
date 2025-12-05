import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live
import shlex
import time

# Imports
from .equipment_api import get_all_equipment, get_equipment_by_id, EQUIPMENT_CONFIG
# Import the new control functions
from .connections.cryostat import set_temperature, set_magnet_field

app = typer.Typer(
    help="CLI to monitor and control lab equipment.",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False
)

console = Console()

@app.command("status")
def status_monitor(refresh_rate: float = 2.0):
    """Continuously monitors equipment status."""
    console.print("[bold blue]Starting Equipment Monitor... (Press Ctrl+C to stop)[/bold blue]")
    try:
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                equipment_data = get_all_equipment()
                table = Table(title=f"Lab Equipment Status (Updated: {time.strftime('%H:%M:%S')})")
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Type", style="magenta")
                table.add_column("Status", justify="center")
                table.add_column("Key Readings", style="green")

                for eq_id, data in equipment_data.items():
                    status_style = "green" if data.get("status") == "Active" else "red"

                    # Format Readings
                    readings = []
                    if "temperature_k" in data: readings.append(f"{data['temperature_k']:.2f} K")
                    if "magnet_field_tesla" in data: readings.append(f"{data['magnet_field_tesla']:.4f} T")
                    if "wavelength_nm" in data: readings.append(f"{data['wavelength_nm']:.2f} nm")
                    if "power_mw" in data: readings.append(f"{data['power_mw']:.2f} mW")

                    table.add_row(
                        eq_id,
                        data.get("type", "Unknown"),
                        f"[{status_style}]{data.get('status', 'Unknown')}[/{status_style}]",
                        ", ".join(readings) if readings else "-"
                    )
                live.update(table)
                time.sleep(refresh_rate)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Monitor stopped.[/bold yellow]")

@app.command("inspect")
def inspect_device(device_id: str):
    """Get detailed info for a device."""
    data = get_equipment_by_id(device_id)
    if not data:
        console.print(f"[bold red]Device {device_id} not found.[/bold red]")
        return
    console.print(data)

@app.command("shell")
def interactive_shell():
    """Starts the interactive shell."""
    console.print("\n[bold green]Lab CLI Shell. Type 'exit' to quit.[/bold green]")
    while True:
        try:
            cmd = Prompt.ask("[bold magenta]lab-cli >[/bold magenta]")
            if cmd.lower() in ["exit", "quit"]: break
            if not cmd.strip(): continue
            app(shlex.split(cmd), standalone_mode=False)
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@app.command("set-temp")
def set_temp(target: float):
    """
    Sets the target temperature for the Cryostat (cryo-01).
    Usage: set-temp 10.5
    """
    # Get the IP for cryo-01
    config = EQUIPMENT_CONFIG.get("cryo-01")
    if not config:
        console.print("[red]Error: 'cryo-01' is not configured.[/red]")
        return

    console.print(f"[yellow]Setting Cryostat Temperature to {target} K...[/yellow]")

    # Call the function
    result = set_temperature(config["ip"], target)

    # Print Result
    if "Error" in result:
        console.print(f"[bold red]{result}[/bold red]")
    else:
        console.print(f"[bold green]{result}[/bold green]")


@app.command("set-field")
def set_field(target: float):
    """
    Sets the magnetic field (Tesla) for the Cryostat (cryo-01).
    Usage: set-field 0.5
    """
    config = EQUIPMENT_CONFIG.get("cryo-01")
    if not config:
        console.print("[red]Error: 'cryo-01' is not configured.[/red]")
        return

    console.print(f"[yellow]Setting Magnetic Field to {target} Tesla...[/yellow]")

    result = set_magnet_field(config["ip"], target)

    if "Error" in result:
        console.print(f"[bold red]{result}[/bold red]")
    else:
        console.print(f"[bold green]{result}[/bold green]")

if __name__ == "__main__":
    app()
