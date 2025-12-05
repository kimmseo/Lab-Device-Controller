from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# Base Equipment Model

@dataclass
class Equipment:
    """Base dataclass for generic lab equipment."""
    id: str
    type: str
    status: str
    operator: Optional[str] = None
    last_check: Optional[str] = None

# Specialized Equipment Models

@dataclass
class Laser(Equipment):
    """Laser with power and wavelength."""
    power_mw: Optional[float] = None
    wavelength_nm: Optional[float] = None
    emission_active: Optional[bool] = None

@dataclass
class Oscilloscope(Equipment):
    """Oscilloscope with channel details."""
    channels_active: Optional[int] = None
    sample_rate_gs: Optional[float] = None
    details: Optional[str] = None

@dataclass
class Cryostat(Equipment):
    """
    Represents the Montana Cryostat.
    """
    temperature_k: Optional[float] = None
    pressure_torr: Optional[float] = None
    magnet_field_tesla: Optional[float] = None
    magnet_enabled: Optional[bool] = None

@dataclass
class PowerSupply(Equipment):
    """DC Power Supply."""
    voltage_v: Optional[float] = None
    current_a: Optional[float] = None

@dataclass
class Spectrometer(Equipment):
    """Spectrometer."""
    integration_time_ms: Optional[int] = None

@dataclass
class MaintenanceDevice(Equipment):
    """Device in maintenance."""
    issue_description: Optional[str] = None
    estimated_fix_date: Optional[str] = None

# Mapping
EQUIPMENT_TYPE_MAP = {
    "laser": Laser,
    "femtosecond laser": Laser,
    "digital oscilloscope": Oscilloscope,
    "cryostat": Cryostat,  # <--- Added
    "montana cryostation": Cryostat, # <--- Added
    "dc power supply": PowerSupply,
    "spectrometer": Spectrometer,
}

def create_equipment_model(equipment_id: str, data: Dict[str, Any]) -> Equipment:
    """Factory function to create equipment models."""
    if data.get("status", "").lower() == "maintenance":
        return MaintenanceDevice(id=equipment_id, **data)

    equipment_type_str = data.get("type", "unknown").lower()
    ModelClass = EQUIPMENT_TYPE_MAP.get(equipment_type_str, Equipment)

    expected_fields = ModelClass.__dataclass_fields__.keys()
    filtered_data = {k: v for k, v in data.items() if k in expected_fields}

    return ModelClass(id=equipment_id, **filtered_data)
