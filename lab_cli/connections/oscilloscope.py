import pyvisa
import platform
import datetime
import time

'''
Oscilloscope connection
Last changed: 9th Oct 2025
Changes: Made file path dynamic instead of static
'''

def find_visa_library():
    # ... (function content remains the same)
    if platform.system() == "Windows":
        return None
    else:
        return None

def connect_oscilloscope():
    """
    Connects to the oscilloscope by first finding the VISA resource manager
    and then opening the specific instrument.
    """
    scope = None
    try:
        rm_oscil = pyvisa.ResourceManager()
        scope = rm_oscil.open_resource("TCPIP0::192.168.0.92::inst0::INSTR")
        scope.write_termination = '\n'
        scope.read_termination = '\n'
        scope.timeout = 15000
        scope.clear()
        return scope
    except pyvisa.errors.VisaIOError as e:
        print(f"VISA connection failed: {e}")
        print("Please ensure the oscilloscope is connected and the VISA drivers are installed.")
        if scope:
            try:
                scope.close()
            except Exception as close_e:
                print(f"Error closing scope resource: {close_e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def capture_scope_screen(scope_address: str, save_path: str = "."):
    """
    Connects to an oscilloscope, captures its screen, and saves it as a PNG file.
    """
    scope = None
    try:
        rm = pyvisa.ResourceManager()
        scope = rm.open_resource(scope_address)
        scope.timeout = 15000

        print("Requesting screen data from oscilloscope...")
        image_data = scope.query_binary_values(
            ':DISPlay:DATA? PNG, COLor',
            datatype='B',
            container=bytes
        )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{save_path}/keysight_capture_{timestamp}.png"

        with open(filename, 'wb') as f:
            f.write(image_data)

        print(f"Screen captured successfully and saved to: {filename}")
        return True

    except pyvisa.errors.VisaIOError as e:
        print(f"VISA Error: Could not communicate with the scope. Details: {e}")
        return False
    finally:
        if scope:
            scope.close()
        print("Connection closed.")


def arm_and_capture(scope_address: str, save_path: str = "."):
    """
    Arms the oscilloscope to wait for an external trigger,
    and saves the screen once the acquisition is complete.
    """
    scope = None
    try:
        rm = pyvisa.ResourceManager()
        scope = rm.open_resource(scope_address)
        scope.timeout = 20000
        scope.clear()

        print("Configuring oscilloscope for single external trigger...")
        scope.write(':STOP')
        scope.write(':TRIGger:SWEep NORMal')
        scope.write(':TRIGger:EDGE:SOURce EXTernal')
        scope.write(':SINGle')

        print("Oscilloscope armed. Waiting for trigger signal...")
        scope.query('*OPC?')
        print("Trigger received and acquisition complete!")
        time.sleep(1)

        print("Requesting screen data...")
        image_data = scope.query_binary_values(
            ':DISPlay:DATA? PNG, COLor',
            datatype='B',
            container=bytes
        )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{save_path}/triggered_capture_{timestamp}.png"

        with open(filename, 'wb') as f:
            f.write(image_data)

        print(f"✅ Screen captured successfully and saved to: {filename}")
        return True

    except pyvisa.errors.VisaIOError as e:
        if "VI_ERROR_TMO" in str(e):
            print("\nOperation timed out. No trigger was received.")
        else:
            print(f"\nVISA Error: {e}")
        return False
    finally:
        if scope:
            scope.write(":RUN")
            scope.close()
        print("Connection closed.")

if __name__ == "__main__":
    print("Connecting to oscilloscope...")
    oscilloscope = connect_oscilloscope()

    if oscilloscope:
        try:
            idn_response = oscilloscope.query("*IDN?").strip()
            print(f"Oscilloscope connected. ID: {idn_response}\n")
            oscilloscope.close()    # Close connection!!
        except pyvisa.errors.VisaIOError as e:
            print(f"Failed to query oscilloscope ID: {e}")
            oscilloscope.close()
    else:
        print("Failed to connect to the oscilloscope.")
