#!/usr/bin/env python3
#

import sys
import os
import instrument
import time
import datetime

class Pegasus(instrument.Instrument):
    def __init__(self, ip, version='v1', verbose=False, tunnel=False):
        super().__init__(ip=ip,
                         port=instrument.Rest_Ports.pegasus_hlm,
                         version=version,
                         verbose=verbose,
                         tunnel=tunnel)

    def start_cryocooler(self):
        '''Start running the cryocooler'''
        self.call_method('cooler/cryocooler/methods/startCryocooler()')
        return

    def stop_cryocooler(self):
        '''Stop running the cryocooler'''
        self.call_method('cooler/cryocooler/methods/stopCryocooler()')
        return

    def get_compressor_speed(self):
        """Get the current compressor speed (Hz)"""
        r = self.get_prop('/cooler/cryocooler/properties/compressorSpeed')
        return r['compressorSpeed']

    def get_cryocooler_running(self):
        """Get the cryocooler running status"""
        r = self.get_prop('/cooler/cryocooler/properties/cryocoolerRunning')
        return r['cryocoolerRunning']

    def get_device_connected(self):
        """Get the device connected status"""
        r = self.get_prop('/cooler/cryocooler/properties/deviceConnected')
        return r['deviceConnected']

    def get_max_allowed_compressor_speed(self):
        """Get the maximum allowed compressor speed (Hz)"""
        r = self.get_prop('/cooler/cryocooler/properties/maxAllowedCompressorSpeed')
        return r['maxAllowedCompressorSpeed']

    def get_min_allowed_compressor_speed(self):
        """Get the minimum allowed compressor speed (Hz)"""
        r = self.get_prop('/cooler/cryocooler/properties/minAllowedCompressorSpeed')
        return r['minAllowedCompressorSpeed']

    def get_power_consumption(self):
        """Get the power consumption (W)"""
        r = self.get_prop('/cooler/cryocooler/properties/powerConsumption')
        return r['powerConsumption']

    def get_return_pressure(self):
        """Get the return pressure (Pa)"""
        r = self.get_prop('/cooler/cryocooler/properties/returnPressure')
        return r['returnPressure']

    def get_supply_pressure(self):
        """Get the supply pressure (Pa)"""
        r = self.get_prop('/cooler/cryocooler/properties/supplyPressure')
        return r['supplyPressure']

    def get_target_compressor_speed(self):
        """Get the target compressor speed (Hz)"""
        r = self.get_prop('/cooler/cryocooler/properties/targetCompressorSpeed')
        return r['targetCompressorSpeed']

    def set_target_compressor_speed(self, target):
        """Set the target compressor speed (Hz)"""
        self.set_prop('/cooler/cryocooler/properties/targetCompressorSpeed', target)
        return

    def get_water_inlet_temperature(self):
        """Get the water inlet temperature (K)"""
        r = self.get_prop('/cooler/cryocooler/properties/waterInletTemperature')
        return r['waterInletTemperature']

    def get_water_outlet_temperature(self):
        """Get the water outlet temperature (K)"""
        r = self.get_prop('/cooler/cryocooler/properties/waterOutletTemperature')
        return r['waterOutletTemperature']

    def print_status(self):
        """Print the current status of the cryocooler"""
        try:
            compressor_speed = self.get_compressor_speed()
            cryocooler_running = self.get_cryocooler_running()
            max_speed = self.get_max_allowed_compressor_speed()
            min_speed = self.get_min_allowed_compressor_speed()
            power_consumption = self.get_power_consumption()
            return_pressure = _pa_to_psig(self.get_return_pressure())
            supply_pressure = _pa_to_psig(self.get_supply_pressure())
            target_speed = self.get_target_compressor_speed()
            water_inlet_temp = _kelvin_to_celsius(self.get_water_inlet_temperature())
            water_outlet_temp = _kelvin_to_celsius(self.get_water_outlet_temperature())

            print(f"\n--- Status Update ({datetime.datetime.now()}) ---")
            print(f"Compressor Running: {cryocooler_running}")
            print(f"Compressor Speed: {compressor_speed} Hz")
            print(f"Target Compressor Speed: {target_speed} Hz")
            print(f"Supply Pressure: {supply_pressure:.2f} psig")
            print(f"Return Pressure: {return_pressure:.2f} psig")
            print(f"Differential Pressure: {return_pressure - supply_pressure:.2f} psig")
            print(f"Water Inlet Temperature: {water_inlet_temp:.2f} °C")
            print(f"Water Outlet Temperature: {water_outlet_temp:.2f} °C")
            print(f"Power Consumption: {power_consumption} W")
            print(f"Max Allowed Compressor Speed: {max_speed} Hz")
            print(f"Min Allowed Compressor Speed: {min_speed} Hz")
        except Exception as e:
            print(f"Error retrieving status: {e}")

            
def _pa_to_psig(pa):
    """Convert Pascals to pounds per square inch gauge (psig)"""
    return pa * 0.0001450377 


def _kelvin_to_celsius(kelvin):
    """Convert Kelvin to Celsius"""
    return kelvin - 273.15


if __name__ == "__main__":
    # Example to demonstrate basic usage:
    #  1. set target compressor speed to 78 Hz
    #  2. start the cryocooler
    #  3. loop for 15 minutes, printing status every 10 seconds
    #  4. stop the cryocooler
    try:
        pegasus = Pegasus('192.168.1.50')  # Replace with your system's IP address
        print("Pegasus instrument initialized")

        # Set target compressor speed to 78 Hz
        pegasus.set_target_compressor_speed(78)
        print("Target compressor speed set to 78 Hz")

        # Start the cryocooler
        pegasus.start_cryocooler()
        print("Cryocooler started")

        # Loop every 30 seconds for 15 minutes (30 * 30 = 900 seconds)
        start_time = time.time()
        while time.time() - start_time < 900:
            pegasus.print_status()
            time.sleep(10)

        # Stop the cryocooler
        pegasus.stop_cryocooler()
        print("Cryocooler stopped")

    except Exception as e:
        print(f"An error occurred: {e}")
