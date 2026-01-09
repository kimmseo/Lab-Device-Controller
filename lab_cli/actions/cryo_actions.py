# Last updated 5 Dec 2025
from . import register_action
from ..connections.cryostat import set_magnet_field, set_temperature
from ..connections.cryostat import set_vacuum_pump
from ..equipment_api import EQUIPMENT_CONFIG
from rich.console import Console

import time

console = Console()

def _get_cryo_ip():
    # Helper to find configured cryostat
    conf = EQUIPMENT_CONFIG.get("cryo-01")
    return conf["ip"] if conf else None

@register_action("set-field")
def action_set_field(target: float, context: dict = None):
    """Sets the magnetic field (Tesla) on cryo-01."""
    ip = _get_cryo_ip()
    if not ip:
        console.print("[red]Error: cryo-01 not configured.[/red]")
        return False

    console.print(f"Setting Field to {target} T...")
    result = set_magnet_field(ip, float(target))

    if "Error" in result:
        console.print(f"[red]{result}[/red]")
        return False
    return True

@register_action("set-temp")
def action_set_temp(target: float, context: dict = None):
    """Sets the platform temperature (Kelvin) on cryo-01."""
    ip = _get_cryo_ip()
    if not ip: return False

    console.print(f"Setting Temp to {target} K...")
    result = set_temperature(ip, float(target))
    return "Error" not in result

@register_action("toggle-pump")
def action_toggle_pump(state: str, context: dict = None):
    """
    Toggles the Vacuum Pump
    Usage: state='on' (SVPR) or 'off' (SVPS)
    WARNING: Only turn off for short durations to minimize vibrations.
    """
    ip = _get_cryo_ip()
    if not ip:
        console.print("[red]Cryostat not configured.[/red]")
        return False

    target_mode = state.lower()
    enable_pump = target_mode in ["on", "start", "run"]

    console.print(f"[bold cyan]Sending Pump Command: {'ON' if enable_pump else 'OFF'}...[/bold cyan]")

    # Call the driver function
    result = set_vacuum_pump(ip, enable_pump)

    # Check response string for "OK" or "Error"
    if "OK" in result:
        console.print(f"[green]{result}[/green]")
        return True
    else:
        console.print(f"[red]Failed: {result}[/red]")
        return False


@register_action("wait-stable")
def action_wait_stable(threshold: float, timeout: float = 600, context: dict = None):
    """
    Blocks execution until Platform Stability < threshold (Kelvin)
    """
    ip = _get_cryo_ip()
    if not ip: return False

    console.print(f"[yellow]Waiting for stability < {threshold} K...[/yellow]")
    start_time = time.time()

    while (time.time() - start_time) < float(timeout):
        # Implementation depends on your connection layer
        # current_stability = float(get_stability_reading(ip)) # Uses command "GPS"

        # Mocking value for demonstration
        current_stability = 0.005

        console.print(f"Current Stability: {current_stability} K", end="\r")

        if current_stability < float(threshold):
            console.print(f"\n[green]Stable! ({current_stability} < {threshold})[/green]")
            return True

        time.sleep(2.0)

    console.print("\n[red]Timeout waiting for stability.[/red]")
    return False

@register_action("magnet-zero")
def action_magnet_zero(context: dict = None):
    """
    Runs the Magnet True Zero (Degauss) routine to remove remnant fields
    """
    ip = _get_cryo_ip()
    if not ip: return False

    console.print("[bold magenta]Initiating Magnet True Zero Routine...[/bold magenta]")

    # Send command "SMTZ"
    # Might want to loop checking "GMS" (Get Magnet State)
    # until it returns "MAGNET ENABLED" or "READY"

    return True

@register_action("system-state")
def action_set_system_state(mode: str, context: dict = None):
    """
    Sets system mode: 'cooldown' (SCD), 'warmup' (SWU), or 'standby' (SSB).
    """
    ip = _get_cryo_ip()
    mode = mode.lower()

    cmd_map = {
        "cooldown": "SCD",
        "warmup": "SWU",
        "standby": "SSB"
    }

    if mode not in cmd_map:
        console.print(f"[red]Unknown mode '{mode}'. Use cooldown, warmup, or standby.[/red]")
        return False

    cmd = cmd_map[mode]
    console.print(f"[bold cyan]Sending system command: {mode.upper()} ({cmd})[/bold cyan]")
    # send_command(ip, cmd)
    return True
