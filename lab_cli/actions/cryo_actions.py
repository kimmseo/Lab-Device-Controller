# lab_cli/actions/cryo_actions.py
from . import register_action
from ..connections.cryostat import set_magnet_field, set_temperature
from ..equipment_api import EQUIPMENT_CONFIG
from rich.console import Console

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
