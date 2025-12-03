# debug_devices.py
import sys
import requests
import json
from rich.console import Console

console = Console()

# --- LASER DEBUG ---
try:
    from toptica.lasersdk.dlcpro.v2_0_3 import DLCpro, NetworkConnection
    LASER_IP = "192.168.0.39"

    console.print(f"\n[bold blue]--- Inspecting Laser at {LASER_IP} ---[/bold blue]")
    try:
        with DLCpro(NetworkConnection(LASER_IP)) as dlc:
            console.print("[green]Connected![/green]")
            console.print(f"Health: {dlc.system_health_txt.get()}")

            # Check what is inside laser1
            console.print("\n[bold]Attributes of 'dlc.laser1':[/bold]")
            keys = dir(dlc.laser1)
            clean_keys = [k for k in keys if not k.startswith('_')]
            console.print(clean_keys)

            # Check for CTL or DL specific attributes
            if hasattr(dlc.laser1, 'ctl'):
                console.print("\n[bold]Attributes of 'dlc.laser1.ctl':[/bold]")
                print([k for k in dir(dlc.laser1.ctl) if not k.startswith('_')])

            if hasattr(dlc.laser1, 'dl'):
                console.print("\n[bold]Attributes of 'dlc.laser1.dl':[/bold]")
                print([k for k in dir(dlc.laser1.dl) if not k.startswith('_')])

    except Exception as e:
        console.print(f"[red]Laser Connection Failed: {e}[/red]")

except ImportError:
    console.print("[red]Toptica SDK not installed.[/red]")
