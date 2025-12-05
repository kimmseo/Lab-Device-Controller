# Lab-Device-Controller CLI

A versatile, future-proof command-line interface (CLI) for automating laboratory equipment, running complex experiments, and monitoring hardware status.

This tool has evolved from a simple status monitor into a **modular automation framework**. It allows researchers to define experiment "recipes" interactively, loop over variables (like magnetic field or temperature), and acquire data without writing new Python code for every measurement.

## Supported Hardware

* **Toptica DLC Pro Lasers**: Full control via Toptica SDK (Emission, Power, Wide Scans).
* **Montana Instruments Cryostation**: Control via REST API/Library (Temperature, Magnetic Field, Pressure).
* **Keysight Oscilloscopes**: Screen capture and triggering via VISA.
* **Generic/Mock Devices**: Extensible support for any device driver.

## Key Features

### 1. Modular Action Registry

The core of the system is the **Action Registry**. Instead of hardcoding experiments, the CLI exposes atomic actions (e.g., `set-temp`, `sweep-laser`, `delay`).

* **Future-Proof:** Adding a new instrument is as simple as dropping a new python file into the `actions/` folder. The CLI automatically detects and registers the new commands.

### 2. "No-Code" Experiment Builder

* **Define:** Create custom experiment workflows interactively in the terminal.
* **Loop:** Execute these workflows while sweeping a variable (e.g., "Loop `my_scan` while varying `field` from 0T to 1T").
* **Save:** Recipes are saved to `user_experiments.json` and can be reused instantly.

### 3. Automated Data Acquisition

* Laser sweeps are automatically saved as **Excel (.xlsx)** files for analysis and **PNG** images for quick reference.
* Folders are organized by experiment type and timestamp.

## Installation & Setup

### 1. Prerequisites

Ensure you have Python 3.8+ installed. You also need the NI-VISA drivers installed if using Oscilloscopes via USB/TCP.

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install typer rich requests pyvisa toptica-lasersdk pandas numpy matplotlib scipy sshtunnel openpyxl
```

### 3. Folder Structure

Ensure your project folder is organized as follows:

```text
lab_cli/
├── main.py                 # Entry point
├── equipment_api.py        # Configuration (IP addresses)
├── experiment_registry.py  # JSON storage for user recipes
├── actions/                # <<< Place new action scripts here
│   ├── __init__.py
│   ├── cryo_actions.py
│   ├── laser_actions.py
│   └── general_actions.py
└── connections/            # Hardware drivers
    ├── laser.py
    ├── cryostat.py
    └── scryostation.py     # (Copy this from Montana Examples/libs)
```

### 4. Configuration

Edit `lab_cli/equipment_api.py` to set the IP addresses for your specific lab setup:

```python
EQUIPMENT_CONFIG = {
    "laser-01": {
        "type": "Toptica Laser",
        "ip": "192.168.0.39",
        "driver": "toptica_dlc"
    },
    "cryo-01": {
        "type": "Montana Cryostation",
        "ip": "192.168.0.178",
        "driver": "montana"
    }
}
```

## Usage Guide

You can run the CLI in **Interactive Mode** (recommended) or as single commands.

### 1. Interactive Shell

Start the persistent shell session:

```bash
python -m lab_cli.main interactive
```

You will see the prompt: `lab-cli >`

### 2. Monitoring Status

Check the live health, temperature, and field of all connected devices:

```bash
status
```

To see detailed properties of a specific device:

```bash
inspect laser-01
inspect cryo-01
```

### 3. Running Instant Actions

You can execute any registered action immediately. Arguments are passed as `key=value`.

**Set Temperature:**

```bash
run set-temp target=295
```

**Set Magnetic Field:**

```bash
run set-field target=0.5
```

**Run a Laser Sweep:**

```bash
run sweep-laser start_nm=1530 end_nm=1535 speed=5 power=0.7
```

### 4. Defining & Looping Experiments (The Automation Workflow)

**Step A: Define a Recipe**
Use the `define` command. You can use `{variable}` syntax to create placeholders.

```bash
define my_magnet_sweep
```

  * *Select Action:* `set-field` → Value: `{field}`
  * *Select Action:* `delay` → Value: `10`
  * *Select Action:* `sweep-laser` → Values: `1530`, `1535`, `5`, `0.7`
  * *Select Action:* `finish`

**Step B: Run the Loop**
Now, run that recipe while sweeping the `{field}` variable from 0 to 0.5 Tesla.

```bash
run-loop my_magnet_sweep --variable field --start 0 --end 0.5 --step 0.1
```

The system will automatically:

1. Set Field to 0.0 T
2. Wait 10s
3. Sweep Laser & Save Data
4. Set Field to 0.1 T
5. ...repeat until 0.5 T.

### 5. Comprehensive Command Reference

**Core CLI Commands**

| Command | Arguments | Description |
| :--- | :--- | :--- |
| **`status`** | `[refresh_rate]` | Shows a live dashboard of all connected equipment. |
| **`inspect`** | `device_id` | Shows detailed properties (health, raw values) for a specific device. |
| **`run`** | `action_name` `[key=value]...` | Executes a specific hardware action immediately. |
| **`define`** | `name` | Starts an interactive wizard to create a new experiment recipe. |
| **`run-loop`** | `name` `--variable` `--start` `--end` `--step` | Loops a defined experiment while varying a specific variable. |
| **`interactive`** | *(none)* | Enters the persistent shell mode. |
| **`exit`** | *(none)* | Exits the interactive shell. |

**Hardware Actions (Used with `run`)**

These are the modular actions registered in your `actions/` folder.

| Device | Action Name | Parameters | Description |
| :--- | :--- | :--- | :--- |
| **Cryostat** | **`set-temp`** | `target` | Sets platform temperature (Kelvin). |
|  | **`set-field`** | `target` | Sets magnetic field (Tesla). |
| **Laser** | **`sweep-laser`** | `start_nm`, `end_nm`, `speed`, `power` | Performs a wide scan sweep and saves Data/Image. |
| **General** | **`delay`** | `seconds` | Pauses execution (useful in loops). |
|  | **`log`** | `message` | Prints a message to the console. |

## Developer Guide: Adding New Actions

To support new hardware (e.g., a Spectrometer), you do **not** need to modify `main.py`.

1. Create a file `lab_cli/actions/spectrometer_actions.py`.
2. Use the `@register_action` decorator.

```python
from . import register_action

@register_action("measure-spectrum")
def action_measure(integration_time: int, context: dict = None):
    """Captures a spectrum."""
    print(f"Measuring for {integration_time} ms...")
    # Add driver code here
    return True
```

3. Restart the CLI. The command `run measure-spectrum` is now available!
