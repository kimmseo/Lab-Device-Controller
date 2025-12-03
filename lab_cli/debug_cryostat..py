import sys
import requests
import json
from rich.console import Console
from pathlib import Path


console = Console()


# Configuration
# Import Montana Python libraries (scryostation.py)
current_dir = Path(__file__).resolve().parent
libs_path = current_dir.parent / "read_only" / "Python Montana examples" / "libs"

# Check if the path exists before adding it (good for debugging)
if not libs_path.exists():
    print(f"Warning: Could not find Montana libs at: {libs_path}")
else:
    # Convert to string and add to system path if not already there
    libs_path_str = str(libs_path)
    if libs_path_str not in sys.path:
        sys.path.append(libs_path_str)

# Import scryostation here
try:
    import scryostation
except ImportError as e:
    scryostation = None
    print(f"Error: Failed to import scryostation from {libs_path}. Details: {e}")

console.print(f"\n[bold blue]--- Inspecting Cryostat at {CRY_IP} ---[/bold blue]")

# Patch requests
_cryo_session = requests.Session()
requests.get = lambda url, **kwargs: _cryo_session.get(url, **kwargs)

# Import library
if LIB_PATH not in sys.path:
    sys.path.append(LIB_PATH)

try:
    import scryostation
    console.print(f"[green]Library loaded from {LIB_PATH}[/green]")

    try:
        cryo = scryostation.SCryostation(CRY_IP)
        console.print("[green]Connected![/green]")

        # Print all available methods to find the correct magnet commands
        methods = [method for method in dir(cryo) if "magnet" in method.lower() or "temp" in method.lower()]
        console.print("\n[bold]Available Methods (Temp/Magnet):[/bold]")
        console.print(methods)

    except Exception as e:
        console.print(f"[red]Cryostat Connection Failed: {e}[/red]")

except ImportError as e:
    console.print(f"[red]Could not import scryostation: {e}[/red]")
