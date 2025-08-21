import typer
import pyvisa

# Local Imports
# Import the shared resource manager instance
from visa_manager import rm
# Import the specific instrument controller
from instruments.laser import LaserController

# Create a Typer application instance. This is the main entry point for commands.
app = typer.Typer(
    help="A CLI application to monitor and control lab devices using PyVISA."
)

@app.command(name="list")
def list_devices():
    """
    Finds and lists all connected VISA-compatible devices.
    """
    typer.echo("\nSearching for connected devices...")
    try:
        devices = rm.list_resources()
        if not devices:
            typer.secho("  -> No devices found. Please check connections.", fg=typer.colors.YELLOW)
        else:
            typer.secho(f"  -> Found {len(devices)} device(s):", fg=typer.colors.GREEN)
            for i, device in enumerate(devices):
                typer.echo(f"    {i+1}: {device}")
    except Exception as e:
        typer.secho(f"An error occurred while searching for devices: {e}", fg=typer.colors.RED)
    typer.echo("-" * 30)


@app.command()
def connect(
    address: str = typer.Argument(..., help="The full VISA resource address of the device."),
):
    """
    Connects to a device and prints its identification string (*IDN?).
    """
    typer.echo(f"\nAttempting to connect to: {address}")
    try:
        # Use a 'with' statement to ensure the connection is automatically closed
        with rm.open_resource(address) as instrument:
            instrument.timeout = 5000
            idn = instrument.query("*IDN?")
            typer.secho("Successfully connected and disconnected!", fg=typer.colors.GREEN)
            typer.echo(f"  -> ID: {idn.strip()}")
    except pyvisa.errors.VisaIOError as e:
        typer.secho(f"Connection Error: Could not connect to the device.", fg=typer.colors.RED)
        typer.secho(f"  -> Details: {e}", fg=typer.colors.YELLOW)
    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)
    typer.echo("-" * 30)


@app.command()
def laser(
    address: str = typer.Argument(..., help="The VISA resource address of the laser."),
    power: float = typer.Option(None, "--power", "-p", help="Set the laser power in mW."),
    on: bool = typer.Option(False, "--on", help="Turn the laser on."),
    off: bool = typer.Option(False, "--off", help="Turn the laser off."),
):
    """
    Connects to and controls a laser.
    """
    typer.echo(f"\n--- Laser Control for {address} ---")
    try:
        with rm.open_resource(address) as instr:
            # Create an instance of our laser controller
            laser_controller = LaserController(instr)

            # Execute actions based on flags
            if power is not None:
                laser_controller.set_power(power)
            if on:
                laser_controller.turn_on()
            if off:
                laser_controller.turn_off()

            if not any([power, on, off]):
                typer.secho("No action specified. Use --power, --on, or --off.", fg=typer.colors.YELLOW)

    except pyvisa.errors.VisaIOError as e:
        typer.secho(f"Connection Error: Could not connect to the laser.", fg=typer.colors.RED)
        typer.secho(f"  -> Details: {e}", fg=typer.colors.YELLOW)
    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)
    typer.echo("-" * 30)


if __name__ == "__main__":
    app()
