# toptica laser
import sys
try:
    from toptica.lasersdk.dlcpro.v2_0_3 import DLCpro, NetworkConnection, DeviceNotFoundError
except ImportError:
    DLCpro = None
    print("Warning: 'toptica-lasersdk' not installed. Laser connection will be simulated.")

def get_laser_details(ip: str) -> dict:
    """
    Connects to Toptica DLC Pro and fetches live data.
    """
    if DLCpro is None:
        return {"status": "Error", "details": "SDK Missing"}

    try:
        with DLCpro(NetworkConnection(ip)) as dlc:
            # Fetch basic health
            health = dlc.system_health_txt.get()

            # Fetch emission state
            emission = dlc.laser1.emission.get()

            # Fetch current Wavelength (act) and Power (act)
            # Parameter names depend on specific laser head, these are standard for CTL/DL
            wavelength = dlc.laser1.ctl.wavelength.act.get()

            # Check for power stabilization input or direct output
            # Using input_channel_value_act
            try:
                power = dlc.laser1.power_stabilization.input_channel_value_act.get()
            except:
                # Fallback if stabilization not active/avail
                power = 0.0

            return {
                "status": "Active" if health == "OK" else "Warning",
                "emission_active": bool(emission),
                "wavelength_nm": float(wavelength),
                "power_mw": float(power),
                "details": f"Health: {health}"
            }

    except DeviceNotFoundError:
        return {"status": "Offline", "details": "Device not found"}
    except Exception as e:
        return {"status": "Connection Error", "details": str(e)}
