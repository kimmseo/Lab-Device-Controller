# Lab-Device-Controller CLI

A command-line interface (CLI) for monitoring, controlling and acquiring data from laboratory equipment. This tool provides a simple and efficient way to interact with hardware like oscilloscopes and lasers directly from the terminal.

It features an interactive shell, allowing the user to run multiple commands in a single session without relaunching the application.

## Features
- **Status Monitoring**: Get a quick overview of all connected lab equipment or a detailed status for a specific device.
- **Direct Hardware Connection**: Establish a live connection with devices to verify their identity and operational state.
- **Oscilloscope Control**:
    - **Screen Capture**: Save the current display of a Keysight oscilloscope as a PNG image to your PC.
    - **Triggered Acquisition**: Arm the oscilloscope to wait for an external trigger signal (e.g., from a pulse streamer) and automatically save the resulting screen capture.
- **Interactive Shell**: Run multiple commands in a persistent session for a smoother workflow.

## Prerequisites

Before installing, please ensure you have the following software installed and configured:

1. **Python**: Version 3.8 or higher
2. **NI-VISA Drivers**: This application communicates with hardware using the VISA protocol. You must install a VISA backend on your system. For most Windows systems, the [NI-VISA Driver](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html) is required.
3. **Hardware Connection**: Ensure your lab equipment (e.g., Keysight DSOX1204G/DSOX2024A) is connected to the same network as your PC.

## Installation

Follow these steps to install and set up the Lab Device Controller CLI.

1. **Clone the Repository**

        git clone https://github.com/kimmseo/Lab-Device-Controller.git
        cd Lab-Device-Controller

2. **(Recommended) Create a Virtual Environment**

        python -m venv .venv
        # On Windows
        .\.venv\Scripts\activate
        # On macOS/Linux
        source .venv/bin/activate

3. **Install Dependencies**

    Install all the required Python packages from the requirements.txt file.

        pip install -r requirements.txt

4. **Install the CLI Tool**

    Install the application in "editable" mode. This creates the `lab-cli` command in your terminal and ensures that any changes you make to the source code are immediately available.

        pip install -e .

## Configuration

Before using the tool, you must configure it to recognise your specific lab equipment.

1. Open the main configuration file: `lab_cli/main.py`.
2. Locate the `MOCK_EQUIPMENT_DATA` Python dictionary near the top of the file.
3. Modify the dictionary to match your equipment. Pay close attention to the `visa_address`. You can find this address using vendor-supplied software like Keysight Connection Expert.

**Example Configuration:**

    # In lab_cli/main.py
    MOCK_EQUIPMENT_DATA = {
        "laser-01" : {
            "type" : "Femtosecond Laser",
            # ... other details
        }
        "scope-01" : {
            "type" : "Digital Oscilloscope",
            "status" : "Idle",
            # Find this address using Keysight Connection Expert
            "visa_address" :"TCPIP0::192.168.1.10::inst0::INSTR",
            "details" : "Keysight DSOX1204G"
        }
    }


## Usage

The primary way to use the application is through its interactive shell.

### Starting the Shell

To begin, run the following command in your terminal:

    lab-cli shell

You will be gretted with the `lab-cli >` prompt. From here, you can run all the commands listed below. To exit the shell, type `exit` or `quit`.

### Command Reference

`list`

Displays a summary table of all configured equipment and their current status.

**Example:**

    lab-cli > list

    Lab Equipment Status Overview
    ┌────────────┬────────────────────────┬────────┬─────────────────────┐
    │ ID         │ Type                   │ Status │ Last Checked        │
    ├────────────┼────────────────────────┼────────┼─────────────────────┤
    │ laser-01   │ Toptica Laser          │ Active │ 2025-10-10 16:30:00 │
    │ scope-01   │ Digital Oscilloscope   │ Idle   │ N/A                 │
    └────────────┴────────────────────────┴────────┴─────────────────────┘

`status <EQUIPMENT_ID>`

Fetches and displays detailed information for a single piece of equipment.

**Example:**

    lab-cli > status scope-01

    Querying status for: scope-01
    ┌──────────┬────────────────────────────┐
    │ ID:      │ scope-01                   │
    │ Type:    │ Digital Oscilloscope       │
    │ Status:  │ Idle                       │
    │----------│----------------------------│
    │ Details: │ Keysight DSOX1204G         │
    │----------│----------------------------│
    │ Operator:│ N/A                        │
    │ Last...  │ N/A                        │
    └──────────┴────────────────────────────┘

`capture <EQUIPMENT_ID>`

Connects to the specified oscilloscope and saves a PNG image of its current screen display.

**Options:**
- `-p`, `--save-path <PATH>`: Specify a directory to save the image in. Defaults to the current directory.

**Example:**

    lab-cli > capture scope-01 -p "C:\Data\Screenshots"

    Starting screen capture for scope-01...
    Requesting screen data from oscilloscope...
    Screen captured successfully and saved to: C:\Data\Screenshots\keysight_capture_2025-10-10_16-45-30.png
    Connection closed.

`arm <EQUIPMENT_ID>`

Arms the oscilloscope to wait for a single external trigger. Once the trigger is received, it automatically captures the screen and saves it as a PNG.

**Options:**
- `-p`, `--save-path <PATH>`: Specify a directory to save the image in.

**Example:**

    lab-cli > arm scope-01

    Arming scope-01 for external trigger...
    Configuring oscilloscope for single external trigger...
    Oscilloscope armed. Waiting for trigger signal...
    Trigger received and acquisition complete!
    Requesting screen data...
    Screen captured successfully and saved to: .\triggered_capture_2025-10-10_16-48-15.png
    Connection closed.

### Project Structure

    Lab-Device-Controller/
    ├── lab_cli/
    │   ├── connections/
    │   │   ├── __init__.py
    │   │   └── oscilloscope.py  # Hardware control logic
    │   ├── __init__.py
    │   ├── main.py              # Main CLI commands and app definition
    │   └── models.py            # Data models (dataclasses)
    ├── .gitignore
    ├── pyproject.toml           # Package configuration
    ├── README.md                # This file
    └── requirement.txt          # Python dependencies


### For debugging:

    Attributes of 'dlc.laser1':
    [
        'amp',
        'config',
        'ctl',
        'diagnosis',
        'dl',
        'dpss',
        'emission',
        'health',
        'health_txt',
        'load',
        'load_head',
        'nlo',
        'pd_ext',
        'power_stabilization',
        'product_name',
        'recorder',
        'save',
        'scan',
        'scope',
        'type',
        'uv',
        'wide_scan'
    ]

    Attributes of 'dlc.laser1.ctl':
    ['factory_settings', 'fpga_fw_ver', 'head_temperature', 'mode_control', 'motor', 'optimization', 'power', 'remote_control', 'state', 'state_txt', 'tuning_current_min', 'tuning_power_min', 'wavelength_act', 'wavelength_max', 'wavelength_min', 'wavelength_set']

    Attributes of 'dlc.laser1.dl':
    ['cc', 'factory_settings', 'fru_serial_number', 'legacy', 'lock', 'model', 'ontime', 'ontime_txt', 'pc', 'pd', 'pressure_compensation', 'restore', 'serial_number', 'store', 'tc', 'type', 'version']

    Available Methods (Temp/Magnet):
    [
        'get_cryooptic_temperature',
        'get_cryooptic_temperature_sample',
        'get_cryooptic_temperature_stability',
        'get_cryooptic_temperature_stable',
        'get_platform_target_temperature',
        'get_platform_temperature',
        'get_platform_temperature_sample',
        'get_platform_temperature_stability',
        'get_platform_temperature_stable',
        'get_stage1_temperature',
        'get_stage1_temperature_sample',
        'get_stage2_temperature',
        'get_stage2_temperature_sample',
        'get_user1_target_temperature',
        'get_user1_temperature',
        'get_user1_temperature_sample',
        'get_user1_temperature_stability',
        'get_user1_temperature_stable',
        'get_user2_target_temperature',
        'get_user2_temperature',
        'get_user2_temperature_sample',
        'get_user2_temperature_stability',
        'get_user2_temperature_stable',
        'set_cryooptic_target_temperature',
        'set_cryooptic_temperature_controller_enabled',
        'set_platform_bakeout_temperature',
        'set_platform_target_temperature',
        'set_user1_target_temperature',
        'set_user1_temperature_controller_enabled',
        'set_user2_target_temperature',
        'set_user2_temperature_controller_enabled'
    ]
