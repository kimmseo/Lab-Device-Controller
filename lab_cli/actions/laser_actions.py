# Last updated 5 Dec 2025
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from rich.console import Console
from . import register_action
from ..equipment_api import EQUIPMENT_CONFIG

# Toptica Import logic
try:
    from toptica.lasersdk.dlcpro.v2_0_3 import DLCpro, NetworkConnection
    from toptica.lasersdk.utils.dlcpro import extract_float_arrays
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

console = Console()

@register_action("sweep-laser")
def action_sweep(start_nm: float, end_nm: float, speed: float, power: float, context: dict = None):
    """Performs a wide scan sweep and saves data."""
    if not HAS_SDK:
        console.print("[red]Toptica SDK missing.[/red]")
        return False

    conf = EQUIPMENT_CONFIG.get("laser-01")
    if not conf: return False

    ip = conf["ip"]

    # Generate filename based on context (e.g., current field)
    suffix = ""
    if context:
        for k, v in context.items():
            suffix += f"_{k}_{v}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = "Data_Sweeps"
    if not os.path.exists(folder): os.makedirs(folder)

    filename_base = os.path.join(folder, f"Sweep_{timestamp}{suffix}")

    try:
        with DLCpro(NetworkConnection(ip)) as dlc:
            # Setup
            console.print(f"Sweeping {start_nm}-{end_nm} nm @ {speed} nm/s...")
            dlc.laser1.wide_scan.scan_begin.set(float(start_nm))
            dlc.laser1.wide_scan.scan_end.set(float(end_nm))
            dlc.laser1.wide_scan.speed.set(float(speed))

            # Recoder Setup
            scan_range = abs(float(end_nm) - float(start_nm))
            duration = scan_range / float(speed)
            sample_count = int(duration * 100) # 100 Hz
            dlc.laser1.recorder.recording_time.set(duration + 1.0)
            dlc.laser1.recorder.sample_count_set.set(sample_count)

            # Start
            dlc.laser1.wide_scan.start()
            while dlc.laser1.wide_scan.state.get() != 0:
                time.sleep(0.5)

            # Save
            raw = dlc.laser1.recorder.data.get_data()
            xy = extract_float_arrays('xy', raw)
            if 'x' in xy and 'y' in xy:
                df = pd.DataFrame({"Wavelength": xy['x'], "Intensity": xy['y']})
                df.to_excel(f"{filename_base}.xlsx", index=False)

                plt.figure()
                plt.plot(df["Wavelength"], df["Intensity"])
                plt.title(os.path.basename(filename_base))
                plt.savefig(f"{filename_base}.png")
                plt.close()
                console.print(f"[green]Saved: {os.path.basename(filename_base)}[/green]")
                return True
            return False

    except Exception as e:
        console.print(f"[red]Sweep Failed: {e}[/red]")
        return False
