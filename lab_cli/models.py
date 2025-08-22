# models.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Type

# --- Base Equipment Model ---

@dataclass
class Equipment:
    """
    A base dataclass representing a generic piece of lab equipment.

    Attributes:
        id (str): The unique identifier for the equipment.
        type (str): The general type of the equipment (e.g., 'Laser').
        status (str): The current operational status (e.g., 'Active', 'Idle').
        operator (Optional[str]): The person currently operating the device.
        last_check (Optional[str]): Timestamp of the last status check.
    """
    id: str
    type: str
    status: str
    operator: Optional[str] = None
    last_check: Optional[str] = None

# --- Specialized Equipment Models ---

@dataclass
class Laser(Equipment):
    """
    Represents a Laser, inheriting from the base Equipment class.

    Adds laser-specific attributes like power and wavelength.
    """
    power_mw: Optional[float] = None
    wavelength_nm: Optional[int] = None

@dataclass
class Oscilloscope(Equipment):
    """
    Represents an Oscilloscope.

    Adds oscilloscope-specific attributes.
    """
    channels_active: Optional[int] = None
    sample_rate_gs: Optional[float] = None # Giga-samples per second

@dataclass
class PowerSupply(Equipment):
    """
    Represents a DC Power Supply.
    """
    voltage_v: Optional[float] = None
    current_a: Optional[float] = None

@dataclass
class Spectrometer(Equipment):
    """
    Represents a Spectrometer.

    Adds fields for error conditions.
    """
    error_code: Optional[str] = None
    details: Optional[str] = None

@dataclass
class MaintenanceDevice(Equipment):
    """
    A model for devices currently in maintenance.
    """
    details: Optional[str] = None

# --- Factory Function ---

# A mapping from a string type (from the API) to the corresponding dataclass
EQUIPMENT_TYPE_MAP: Dict[str, Type[Equipment]] = {
    "femtosecond laser": Laser,
    "diode laser": Laser,
    "digital oscilloscope": Oscilloscope,
    "dc power supply": PowerSupply,
    "spectrometer": Spectrometer,
}

def create_equipment_model(equipment_id: str, data: Dict[str, Any]) -> Equipment:
    """
    Factory function to create the appropriate equipment model from a data dictionary.

    This function inspects the 'type' and 'status' fields of the input data
    to decide which dataclass to instantiate. This avoids having large if/elif/else
    blocks in your main application logic.

    Args:
        equipment_id (str): The ID of the equipment.
        data (Dict[str, Any]): A dictionary of properties for the equipment.

    Returns:
        Equipment: An instance of a specific Equipment subclass.
    """
    # Check for maintenance status first, as it's a special case
    if data.get("status", "").lower() == "maintenance":
        return MaintenanceDevice(id=equipment_id, **data)

    equipment_type_str = data.get("type", "unknown").lower()

    # Find the correct class from our map
    ModelClass = EQUIPMENT_TYPE_MAP.get(equipment_type_str, Equipment)

    # Filter the data dictionary to only include keys that the dataclass expects.
    # This prevents errors if the API returns extra, unexpected fields.
    expected_fields = ModelClass.__dataclass_fields__.keys()
    filtered_data = {k: v for k, v in data.items() if k in expected_fields}

    return ModelClass(id=equipment_id, **filtered_data)

