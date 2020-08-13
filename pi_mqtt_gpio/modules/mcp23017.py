from __future__ import absolute_import

from pi_mqtt_gpio.modules import GenericGPIO, PinDirection, PinPullup


REQUIREMENTS = ("https://github.com/sensorberg/MCP23017-python#37c27f2",)
CONFIG_SCHEMA = {
    "i2c_bus_num": {"type": "integer", "required": True, "empty": False},
    "chip_addr": {"type": "integer", "required": True, "empty": False},
}

PULLUPS = None


class GPIO(GenericGPIO):
    """
    Implementation of GPIO class for the MCP23017 IO expander chip.
    """

    def __init__(self, config):
        global PULLUPS
        PULLUPS = {PinPullup.UP: True, PinPullup.DOWN: False}
        from mcp23017 import MCP23017

        from i2c import I2C
        import smbus

        i2c = I2C(smbus.SMBus(config["i2c_bus_num"]))
        self.io = MCP23017(config["chip_addr"], i2c)

    def setup_pin(self, pin, direction, pullup, pin_config):
        self.io.pin_mode(pin, 0xFF if direction == PinDirection.INPUT else 0x00)

        if direction == PinDirection.INPUT and pullup is not None:
            pair = self.get_offset_gpio_tuple([0x0C, 0x0D], pin)
            self.set_bit_enabled(pair[0], pair[1], PULLUPS[pullup])

        initial = pin_config.get("initial")
        if initial is not None:
            if initial == "high":
                self.digital_write(pin, 0xFF)
            elif initial == "low":
                self.digital_write(pin, 0x00)

    def set_pin(self, pin, value):
        self.io.digital_write[pin] = 0xFF if value else 0x00

    def get_pin(self, pin):
        return self.io.digital_read(pin) == 0xFF
