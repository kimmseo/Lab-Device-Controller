import typer
import pyvisa
import sys

try:
    # Initialize the VISA resource manager
    rm = pyvisa.ResourceManager()
except Exception:
    # Use typer.echo for consistent output styling and better testing
    typer.secho(
        "Error: Could not initialize VISA resource manager.", fg=typer.colors.RED
    )
    typer.secho(
        "Please ensure NI-VISA or a compatible backend is installed.", fg=typer.colors.YELLOW
    )
    # Exit the script cleanly if the backend is missing
    sys.exit(1)
