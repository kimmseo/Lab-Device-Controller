# Import libraries
import pyvisa
import platform
import datetime
import time
import socket

'''
Laser connection
Last changed: 16th Oct 2025
Changes: Created file
'''

def find_visa_library():
    if platform.system() == "Windows":
        return None
    else:
        return None

def connect_laser():
    '''
    Connect to laser
    '''
    scope = None
    try:
        rm_laser = pyvisa.ResourceManager()
        scope = rm_laser.open_resource("TCPIP0::192.168.0.92::inst0::INSTR")
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

def connect_laser_via_server():

    class LaserProxy:
        '''
        self.sock.recv will receive stuff from the server
        self.sock.sendall will send stuff to the server
        Use only write and query functions
        '''
        def __init__(self, host = "localhost", port = 9999):
            self.host = host
            self.port = port    # Connects to 9999 port by default

        def write(self, command):
            # General purpose command, most commonly used
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.sendall(command.encode())

        def query(self, command):
            if not command.endswith("?"):
                raise NameError("Queries m ust end with ?")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.sendall(command.encode())
                # Data from laser is at most 1024 bytes long
                # Adjust as needed if other laser models use different values
                return s.recv(1024).decode().strip()

        def read(self, command):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                s.sendall(f"_r_{command}".encode())
                return s.recv(1024).decode().strip()

        def close(self):
            pass

    return LaserProxy()

if __name__ == "__main__":
    print("Connecting to laser server via proxy...")
    laser = connect_laser_via_server()

    if laser:
        try:
            idn_response = laser.query("*IDN").strip()
            print("Laser proxy client ready, Laser ID: ", idn_response)
            laser.close()
        except pyvisa.errors.VisaIOError as e:
            print(f"Failed to query laser ID: {e}")
            laser.close()
    else:
        print("Failed to connec to laser.")
