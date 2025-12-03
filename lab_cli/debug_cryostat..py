import sys
import requests
import json
from rich.console import Console

console = Console()


# --- 2. CRYOSTAT DEBUG ---
CRY_IP = "192.168.0.178"
LIB_PATH = r"C:\Users\qmqin\VSCode-v2\read_only\Python Montana examples\libs"

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
