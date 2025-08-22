# equipment_api.py
import time
import random
from typing import Dict, Optional, Any

# --- Mock Database ---
# This dictionary simulates a persistent data source or the last known state
# of the equipment. In a real application, this would be replaced by calls
# to a database or direct queries to the equipment.
EQUIPMENT_DATABASE = {
    "laser-01": {
        "type": "Femtosecond Laser",
        "status": "Active",
        "power_mw": 85.3,
        "wavelength_nm": 1030,
        "last_check": "2025-08-22 12:30:15",
        "operator": "Dr. Evelyn Reed",
    },
    "osc-01": {
        "type": "Digital Oscilloscope",
        "status": "Idle",
        "channels_active": 2,
        "sample_rate_gs": 5.0,
        "last_check": "2025-08-22 12:35:02",
        "operator": "N/A",
    },
    "spec-01": {
        "type": "Spectrometer",
        "status": "Error",
        "error_code": "E-CAL-003",
        "details": "Calibration failed. Needs reset.",
        "last_check": "2025-08-22 12:25:45",
        "operator": "John Carter",
    },
    "pwr-supply-01": {
        "type": "DC Power Supply",
        "status": "Active",
        "voltage_v": 5.01,
        "current_a": 1.25,
        "last_check": "2025-08-22 12:36:10",
        "operator": "Dr. Evelyn Reed",
    },
    "laser-02": {
        "type": "Diode Laser",
        "status": "Maintenance",
        "details": "Scheduled alignment check.",
        "last_check": "2025-08-21 09:00:00",
        "operator": "Tech Team",
    },
}

# --- API Functions ---

def get_all_equipment() -> Dict[str, Any]:
    """
    Simulates fetching a summary of all equipment.

    In a real implementation, this might involve:
    - Querying a central management server.
    - Iterating through a list of known IP addresses and pinging each device.
    - Reading from a configuration file or database.
    """
    print("API: Fetching all equipment data...")
    # Simulate a network delay
    time.sleep(0.5)

    # Here, we just return a copy of our mock database.
    return EQUIPMENT_DATABASE.copy()


def get_equipment_by_id(equipment_id: str) -> Optional[Dict[str, Any]]:
    """
    Simulates fetching detailed data for a single piece of equipment.

    In a real implementation, this would be the place to put device-specific
    communication logic, for example:
    - Sending a SCPI command over a VISA connection.
    - Making an HTTP GET request to the device's REST API.
    - Communicating over a serial (RS-232) port.
    """
    print(f"API: Querying details for {equipment_id}...")
    # Simulate a device-specific delay
    time.sleep(0.5)

    device_data = EQUIPMENT_DATABASE.get(equipment_id.lower())

    if not device_data:
        return None

    # Simulate dynamic data by slightly randomizing some values if the device is active
    if device_data.get("status") == "Active":
        if "power_mw" in device_data:
            # Fluctuate power by +/- 2%
            fluctuation = device_data["power_mw"] * random.uniform(-0.02, 0.02)
            device_data["power_mw"] = round(device_data["power_mw"] + fluctuation, 2)
        if "current_a" in device_data:
            # Fluctuate current by +/- 1%
            fluctuation = device_data["current_a"] * random.uniform(-0.01, 0.01)
            device_data["current_a"] = round(device_data["current_a"] + fluctuation, 3)

    return device_data.copy()

