"""Integration constants."""

from homeassistant.const import Platform

DOMAIN = "eureka_robot"
PLATFORMS = [
    Platform.VACUUM,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
]
VERSION = "0.5.1"
