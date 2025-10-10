import pyvisa
import platform

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
