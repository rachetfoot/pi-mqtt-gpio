import pkg_resources

from pi_mqtt_gpio.modules import raspberrypi, PinDirection, PinPullup
from pi_mqtt_gpio.server import install_missing_requirements


# There is a physical jumper between these two pins on the test Pi
JUMPER_PINS = (17, 27)


def test_digital_io():
    """
    Uses the module to set digital output and read it with a digital input.
    """
    gpio = raspberrypi.GPIO({})
    pin_in = JUMPER_PINS[0]
    pin_out = JUMPER_PINS[1]

    gpio.setup_pin(pin_in, PinDirection.INPUT, PinPullup.DOWN, {})
    gpio.setup_pin(pin_out, PinDirection.OUTPUT, None, {})

    assert gpio.get_pin(pin_in) is False
    gpio.set_pin(pin_out, True)
    assert gpio.get_pin(pin_in) is True
    gpio.set_pin(pin_out, False)
    assert gpio.get_pin(pin_in) is False
