import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_ARMING,
    STATE_ALARM_TRIGGERED,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED, CONF_DEVICE_ID,
)

DOMAIN = "olarm_sensors"
CONF_UPDATE_INTERVAL = 5
DEFAULT_UPDATE_INTERVAL = 5
MIN_UPDATE_INTERVAL = 5
AuthenticationError = "invalid_credentials"
DeviceIDError = "invalid_device_id"
ZONE = 0
LOGGER = logging.getLogger(__package__)
CONF_ALARM_CODE = "alarm_code"
CONF_DEVICE_NAME = "olarm_device_name"
CONF_DEVICE_MAKE = "olarm_device_make"
CONF_DEVICE_MODEL = "olarm_device_model"

ALARM_STATE_TO_HA = {
    "disarm": STATE_ALARM_DISARMED,
    "notready": STATE_ALARM_DISARMED,
    "countdown": STATE_ALARM_ARMING,
    "sleep": STATE_ALARM_ARMED_NIGHT,
    "stay": STATE_ALARM_ARMED_HOME,
    "arm": STATE_ALARM_ARMED_AWAY,
    "alarm": STATE_ALARM_TRIGGERED,
    "fire": STATE_ALARM_TRIGGERED,
    "emergency": STATE_ALARM_TRIGGERED,
}

OLARM_CHANGE_TO_HA = {
    "area-disarm": STATE_ALARM_DISARMED,
    "area-stay": STATE_ALARM_ARMED_HOME,
    "area-sleep": STATE_ALARM_ARMED_NIGHT,
    "area-arm": STATE_ALARM_ARMED_AWAY,
    None: None,
}

VERSION = "1.1.2"

def get_domain(config_entry: ConfigEntry) -> str:
    """Return a unique domain for the given config entry."""
    instance_id = config_entry.data[CONF_DEVICE_ID].split("-")[0]
    return f"{DOMAIN}_{instance_id}"


class AlarmPanelArea:
    """
    DOCSTRING: Representation of the area number
    """

    area: int = 0

    def __init__(self, area: int) -> None:
        self.area = area
        return None

    @property
    def data(self):
        """
        DOCSTRING: Returns the area number for the api.
        """
        return {"area": self.area}
