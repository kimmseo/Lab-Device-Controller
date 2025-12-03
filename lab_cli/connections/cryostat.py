import sys
import requests
import json
import time
from pathlib import Path

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

# Patching Requests
# Montana library creates a new session for every call, which can overwhelm the server
# We patch requests.get to use a persistent session, as per your working script.
_cryo_session = requests.Session()

def persistent_get(url, params=None, **kwargs):
    return _cryo_session.get(url=url, params=params, **kwargs)

requests.get = persistent_get

try:
    import scryostation
except ImportError:
    scryostation = None
    print(f"Warning: Could not import scryostation from {MONTANA_LIB_PATH}")

def get_cryostat_details(ip: str) -> dict:
    if not scryostation:
        return {"status": "Error", "details": "Library Import Failed"}

    try:
        # Connect
        cryo = scryostation.SCryostation(ip)

        # Fetch Data (with safety checks)
        temp = cryo.get_temperature() if hasattr(cryo, 'get_temperature') else 0.0
        pressure = cryo.get_pressure() if hasattr(cryo, 'get_pressure') else 0.0

        # Magnet info
        field = 0.0
        if hasattr(cryo, 'get_magnet_target_field'):
            field = cryo.get_magnet_target_field()
        elif hasattr(cryo, 'getMagnetTargetField'):
             field = cryo.getMagnetTargetField()

        return {
            "status": "Active",
            "temperature_k": float(temp),
            "pressure_torr": float(pressure),
            "magnet_field_tesla": float(field),
            "details": "Connected via Lib"
        }

    except Exception as e:
        return {
            "status": "Connection Error",
            "details": str(e)
        }
