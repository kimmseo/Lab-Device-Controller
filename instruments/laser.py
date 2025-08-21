import pyvisa
import typer

class LaserController:
    """
    A class to encapsulate the control logic for a laser.
    """
    def __init__(self, instrument: pyvisa.resources.Resource):
        """
        Initializes the controller with a connected PyVISA instrument object.

        Args:
            instrument: An active and connected PyVISA resource instance.
        """
        self.instrument = instrument
        # You can add instrument-specific setup here, like setting a timeout.
        self.instrument.timeout = 5000
        typer.echo(f"  -> Laser controller initialized for device: {self.get_id().strip()}")

    def get_id(self) -> str:
        """Queries the instrument for its identification string."""
        return self.instrument.query("*IDN?")

    def set_power(self, power_mw: float):
        """
        (Placeholder) Sends the command to set the laser's power.

        Args:
            power_mw: The desired power in milliwatts.
        """
        typer.echo(f"  -> Pretending to send command: POWER {power_mw}mW")
        # In a real scenario, you would use:
        # self.instrument.write(f"POW {power_mw}")

    def turn_on(self):
        """(Placeholder) Sends the command to turn the laser on."""
        typer.echo("  -> Pretending to send command: OUTPUT ON")
        # In a real scenario, you would use:
        # self.instrument.write("OUTP 1")

    def turn_off(self):
        """(Placeholder) Sends the command to turn the laser off."""
        typer.echo("  -> Pretending to send command: OUTPUT OFF")
        # In a real scenario, you would use:
        # self.instrument.write("OUTP 0")

