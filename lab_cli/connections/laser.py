import sys

# Try importing the SDK
try:
    from toptica.lasersdk.dlcpro.v2_0_3 import DLCpro, NetworkConnection, DeviceNotFoundError
except ImportError:
    DLCpro = None
    print("Warning: 'toptica-lasersdk' not installed. Laser connections will fail.")

def get_laser_details(ip: str) -> dict:
    """
    Connects to Toptica DLC Pro via SDK and fetches live data.
    """
    if DLCpro is None:
        return {"status": "Error", "details": "SDK Missing"}

    try:
        # Connect to the laser
        with DLCpro(NetworkConnection(ip)) as dlc:
            # 1. Get Health Status
            # .strip() removes whitespace, .upper() ensures "ok" matches "OK"
            health_txt = dlc.system_health_txt.get().strip()
            is_healthy = health_txt.upper() == "OK"

            # 2. Get Emission State
            emission = dlc.laser1.emission.get()

            # 3. Get Wavelength (FIXED)
            # Debug output showed 'wavelength_act' is directly under 'ctl'
            try:
                if hasattr(dlc.laser1, 'ctl'):
                    wavelength = dlc.laser1.ctl.wavelength_act.get()
                elif hasattr(dlc.laser1, 'wide_scan'):
                    # Fallback for other models if CTL isn't present
                    wavelength = dlc.laser1.wide_scan.scan_begin.get()
                else:
                    wavelength = 0.0
            except Exception:
                wavelength = 0.0

            # 4. Get Power
            # We try the stabilization input first (most accurate for experiments)
            # If that fails, we check the 'power' attribute under ctl
            power = 0.0
            try:
                # Primary Method: Power Stabilization Input
                if hasattr(dlc.laser1, 'power_stabilization'):
                    power = dlc.laser1.power_stabilization.input_channel_value_act.get()
                # Secondary Method: CTL Power Reading
                elif hasattr(dlc.laser1, 'ctl') and hasattr(dlc.laser1.ctl, 'power'):
                     power = dlc.laser1.ctl.power.get()
            except Exception:
                power = 0.0

            return {
                "status": "Active" if is_healthy else "Warning",
                "emission_active": bool(emission),
                "wavelength_nm": float(wavelength),
                "power_mw": float(power),
                "details": f"Health: {health_txt}"
            }

    except DeviceNotFoundError:
        return {
            "status": "Offline",
            "details": "Device not found at IP"
        }
    except Exception as e:
        return {
            "status": "Connection Error",
            "details": str(e)
        }
