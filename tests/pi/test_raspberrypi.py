import pkg_resources

from pi_mqtt_gpio.modules import raspberrypi
from pi_mqtt_gpio.server import install_missing_requirements


def test_install_missing_requirements():
    pkgs_installed = pkg_resources.WorkingSet()
    req = pkg_resources.Requirement.parse("RPi.GPIO")
    assert pkgs_installed.find(req) is None
    install_missing_requirements(raspberrypi)
    pkgs_installed = pkg_resources.WorkingSet()
    assert pkgs_installed.find(req) is not None
