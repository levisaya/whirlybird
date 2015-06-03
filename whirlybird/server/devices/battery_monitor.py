import time
import RPi.GPIO as GPIO


class BatteryMonitor(object):
    """
    Device to read the voltage off an ADC.
    Specifically used to monitor the lipo voltage.
    """
    def __init__(self,
                 vin_max,
                 vin_min,
                 r1,
                 r2,
                 chip_select_pin=25,
                 clock_pin=8,
                 mosi_pin=24,
                 miso_pin=23):
        """
        :param vin_max: The maximum input voltage. This voltage will be interpreted as 100%.
        :param vin_min: The minimum input voltage. This voltage will be interpreted as 0%.
        :param r1: The value of the vin to vout resistor, in ohms.
        :param r2: The value of the vout to ground resistor, in ohms.
        :param chip_select_pin: Chip enable pin number on the Pi (25 or 26)
        :param clock_pin: Spi clock pin number on the Pi.
        :param mosi_pin: MOSI pin number on the Pi.
        :param miso_pin: MISO pin number on the Pi.
        :return:
        """
        self.chip_select_pin = chip_select_pin
        self.clock_pin = clock_pin
        self.mosi_pin = mosi_pin
        self.miso_pin = miso_pin
        self.r1 = r1
        self.r2 = r2

        # Setup the SPI GPIO pins.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(mosi_pin, GPIO.OUT)
        GPIO.setup(miso_pin, GPIO.IN)
        GPIO.setup(clock_pin, GPIO.OUT)
        GPIO.setup(chip_select_pin, GPIO.OUT)

        # Calculate the max and min voltages we should be seeing over the voltage drop.
        # These values become 100% charge and 0% charge.
        self.vout_max = (vin_max * r1) / (r1 + r2)
        self.vout_min = (vin_min * r1) / (r1 + r2)

    def _read_adc_bits(self, num_bits=12):
        """
        Generator to pulse the clock and read a bit.
        :param num_bits: The number of bits to read.
        :return: Generator over the bits read.
        """
        for _ in range(num_bits):
            GPIO.output(self.clock_pin, True)
            GPIO.output(self.clock_pin, False)
            yield GPIO.input(self.miso_pin)

    def read_adc(self, percentage=True):
        """
        :param percentage: If true, the battery percentage is also returned.
        :return: If percentage was False, a float representing the voltage in volts. If True, a tuple containing the
        voltage and the percentage.
        """

        # Initialize the clock to low, set the chip select low to select the ADC.
        GPIO.output(self.chip_select_pin, True)
        GPIO.output(self.clock_pin, False)
        GPIO.output(self.chip_select_pin, False)

        adc_command = ([1, 1, 0] if self.chip_select_pin == 25 else [1, 1, 1])
        for bit in adc_command:
            GPIO.output(self.mosi_pin, bit)
            GPIO.output(self.clock_pin, True)
            GPIO.output(self.clock_pin, False)

        # Read 12 bits off the ADC.
        adc_bits = [bit for bit in self._read_adc_bits()]

        # Sum the bit values to get the read voltage.
        # Note that we iterate up until the last bit, which is the null bit that isn't included in the value.
        # The exponent is adjusted to match.
        adc_voltage = sum([2**(len(adc_bits) - i - 2) * bit for i, bit in enumerate(adc_bits[:-1])])

        # All done reading, flip chip select back high.
        GPIO.output(self.chip_select_pin, True)

        # Right now we adc_voltage is a integer ranging from 0 to 1023, mapping to the 0 to 3.3V output of the
        # voltage divider. Convert back to a voltage.
        read_voltage = adc_voltage * (3.3 / 1024.0)

        # Reverse the voltage drop to determine vin from vout.
        real_voltage = read_voltage * (self.r1 + self.r2) / self.r1

        if percentage:
            # Calculate the percentage with respect to the range vout_min to vout_max.
            percentage = (read_voltage - self.vout_min) / (self.vout_max - self.vout_min) * 100

            # Trim the percentage to 100 if we were over slightly.
            if percentage > 100:
                percentage = 100.0
            return real_voltage, percentage
        else:
            return real_voltage

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Battery monitoring loop')
    parser.add_argument('--vin-max', dest='vin_max', type=float, help='Maximum input voltage in volts.', required=True)
    parser.add_argument('--vin-min', dest='vin_min', type=float, help='Minimum input voltage in volts.', required=True)
    parser.add_argument('--r1', dest='r1', type=int, help='Resistor R1 value in ohms.', required=True)
    parser.add_argument('--r2', dest='r2', type=int, help='Resistor R2 value in ohms.', required=True)
    parser.add_argument('--chip-select-pin', dest='chip_select_pin', type=int,
                        help='Pi chip select pin.', required=True, choices=[25, 26])
    parser.add_argument('--polling-period', dest='polling_period', type=float,
                        help='Time between readings, in seconds.', default=2.0)

    args = parser.parse_args()

    monitor = BatteryMonitor(args.vin_max,
                             args.vin_min,
                             args.r1,
                             args.r2,
                             args.chip_select_pin)

    try:
        while True:
            # read the analog pin
            read_adc = monitor.read_adc()

            print(read_adc)
            time.sleep(args.polling_period)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
