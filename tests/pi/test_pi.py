from pi_mqtt_gpio.modules import raspberrypi
from pi_mqtt_gpio.server import install_missing_requirements


def test_install_missing_requirements():
    install_missing_requirements(raspberrypi)
