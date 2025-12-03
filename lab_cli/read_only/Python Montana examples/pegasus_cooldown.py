#!/usr/bin/env python3

import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pythonlibs"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
import pegasus


def main():
    # Set instrument IP
    ip = '192.168.1.50'  # Replace with your system's IP address

    # Create object used to communicate with the instrument
    peg = pegasus.Pegasus(ip)
    print("Pegasus instrument initialized")

    # Set target compressor speed to 78 Hz
    peg.set_target_compressor_speed(78)
    print("Target compressor speed set to 78 Hz")

    # Start the cryocooler
    peg.start_cryocooler()
    print("Cryocooler started")

    # Loop every 10 seconds for 15 minutes (10 * 90 = 900 seconds)
    start_time = time.time()
    while time.time() - start_time < 900:
        peg.print_status()
        time.sleep(10)

    # Stop the cryocooler
    peg.stop_cryocooler()
    print("Cryocooler stopped")

    
if __name__ == "__main__":
    main()
