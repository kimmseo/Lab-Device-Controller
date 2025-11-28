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
            health_txt = dlc.system_health_txt.get()

            # Robust check: 'OK' might have spaces or case differences
            is_healthy = health_txt.strip().upper() == "OK"

            # 2. Get Emission State
            emission = dlc.laser1.emission.get()

            # 3. Get Wavelength and Power
            # Note: Using .act (actual value)
            wavelength = dlc.laser1.ctl.wavelength.act.get()

            # Try getting power from stabilization input (common setup)
            try:
                power = dlc.laser1.power_stabilization.input_channel_value_act.get()
            except:
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
        # Return the specific error to help debugging
        return {
            "status": "Connection Error",
            "details": str(e)
        }
