import sys
import requests
import json
import time

# Configuration
# Path to the Montana Python libraries (scryostation.py)
MONTANA_LIB_PATH = r"C:\Users\qmqin\VSCode-v2\read_only\Python Montana examples\libs"

# Patching Requests
# Montana library creates a new session for every call, which can overwhelm the server
# We patch requests.get to use a persistent session, as per your working script.
_cryo_session = requests.Session()

def persistent_get(url, params=None, **kwargs):
    return _cryo_session.get(url=url, params=params, **kwargs)

# Apply patch
requests.get = persistent_get

# Import Montana Library
if MONTANA_LIB_PATH not in sys.path:
    sys.path.append(MONTANA_LIB_PATH)

try:
    import scryostation
except ImportError:
    scryostation = None
    print(f"Warning: Could not import scryostation from {MONTANA_LIB_PATH}")

def get_cryostat_details(ip: str) -> dict:
    """
    Connects to the Montana Cryostat and fetches current status.
    Returns a dictionary suitable for the Cryostat model.
    """
    if not scryostation:
        return {"status": "Error", "details": "Library not found"}

    try:
        # Connect
        cryo = scryostation.SCryostation(ip)

        # Fetch Data
        # Use the REST methods exposed by the object or direct attributes
        # sample method, depends on specific lib version
        temp = cryo.get_temperature()
        pressure = cryo.get_pressure()

        # Magnet info
        mag_applied = False
        field = 0.0

        # Attempt to get magnet info if available
        if hasattr(cryo, 'get_magnet_target_field'):
             field = cryo.get_magnet_target_field()
        elif hasattr(cryo, 'getMagnetTargetField'):
             field = cryo.getMagnetTargetField()

        # If the library fails, we could use the direct REST fallback you found,
        # but the library should work if the path is correct

        return {
            "status": "Active",
            "temperature_k": float(temp) if temp is not None else 0.0,
            "pressure_torr": float(pressure) if pressure is not None else 0.0,
            "magnet_field_tesla": float(field) if field is not None else 0.0,
            "magnet_enabled": True
        }

    except Exception as e:
        return {
            "status": "Connection Error",
            "details": str(e)
        }
