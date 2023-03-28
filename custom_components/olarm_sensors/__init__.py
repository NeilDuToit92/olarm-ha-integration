import logging
from homeassistant.components.alarm_control_panel import (
    DOMAIN as ALARM_CONTROL_PANEL_DOMAIN,
)
from homeassistant.components.binary_sensor import (
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import OlarmCoordinator
from .olarm_api import OlarmApi
import asyncio
import voluptuous as vol
from .const import DOMAIN, get_domain, ZONE
from homeassistant.const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [ALARM_CONTROL_PANEL_DOMAIN, BINARY_SENSOR_DOMAIN, BUTTON_DOMAIN]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """
    This function handles the setup of the Olarm integration. It creates a coordinator instance, registers services for each zone, and forwards the setup for binary sensors.
    """
    coordinator = OlarmCoordinator(hass, entry=config_entry)
    instance_id = config_entry.data.get(CONF_DEVICE_ID)

    hass.data.setdefault(get_domain(config_entry), {})
    hass.data[get_domain(config_entry)][config_entry.entry_id] = {
        "coordinator": coordinator,
        "instance_id": instance_id,
    }

    # Creating an instance of the Olarm API class to call the requests to arm, disarm, sleep, or stay the zones.
    OLARM_API = OlarmApi(
        device_id=config_entry.data[CONF_DEVICE_ID],
        api_key=config_entry.data[CONF_API_KEY],
    )

    # Forwarding the setup for the binary sensors.
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    max_zones = await OLARM_API.get_devices_json()

    max_areas = max_zones["deviceProfile"]["areasLimit"]

    # Registering services for each zone.
    for area in range(1, max_areas + 1):
        hass.services.async_register(
            get_domain(config_entry),
            f"arm_{area}_{instance_id}",
            OLARM_API.arm_area,
            schema=vol.Schema({vol.Optional("area", default=area): int}),
        )
        hass.services.async_register(
            get_domain(config_entry),
            f"disarm_{area}_{instance_id}",
            OLARM_API.disarm_area,
            schema=vol.Schema({vol.Optional("area", default=area): int}),
        )
        hass.services.async_register(
            get_domain(config_entry),
            f"sleep_{area}_{instance_id}",
            OLARM_API.sleep_area,
            schema=vol.Schema({vol.Optional("area", default=area): int}),
        )
        hass.services.async_register(
            get_domain(config_entry),
            f"stay_{area}_{instance_id}",
            OLARM_API.stay_area,
            schema=vol.Schema({vol.Optional("area", default=area): int}),
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    coordinator = hass.data[get_domain(entry)][entry.entry_id]
    instance_id = entry.unique_id

    # Unregister all services for this instance
    for zone_id in range(1, coordinator.max_zones + 1):
        for service_name in ZONE:
            service_unload = f"{service_name}_{instance_id}_zone_{zone_id}"
            await hass.services.async_remove(DOMAIN, service_unload)

    # Unload all platforms for this instance
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unloaded:
        del hass.data[get_domain(entry)][entry.entry_id]

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
