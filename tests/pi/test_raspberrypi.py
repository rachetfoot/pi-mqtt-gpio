import pkg_resources

from pi_mqtt_gpio.modules import PinDirection, PinPullup, dht22, raspberrypi
from pi_mqtt_gpio.server import install_missing_requirements

# There is a physical jumper between these two pins on the test Pi
JUMPER_PINS = (22, 27)


def test_digital_io():
    """
    Uses the module to set digital output and read it with a digital input.
    """
    gpio = raspberrypi.GPIO({})
    pin_in, pin_out = JUMPER_PINS

    gpio.setup_pin(pin_in, PinDirection.INPUT, PinPullup.DOWN, {})
    gpio.setup_pin(pin_out, PinDirection.OUTPUT, None, {})

    gpio.set_pin(pin_out, True)
    assert gpio.get_pin(pin_in) is True
    gpio.set_pin(pin_out, False)
    assert gpio.get_pin(pin_in) is False
    gpio.cleanup()


def test_temperature():
    """
    Gets the temperature from the DHT22 device.
    """
    dht = dht22.Sensor(dict(type="AM2302", pin=14))
    temp = dht.get_value(dict(type="temperature"))
    assert isinstance(temp, float)


def test_humidity():
    """
    Gets the temperature from the DHT22 device.
    """
    dht = dht22.Sensor(dict(type="AM2302", pin=14))
    humidity = dht.get_value(dict(type="humidity"))
    assert isinstance(humidity, float)

