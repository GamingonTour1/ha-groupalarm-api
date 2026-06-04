# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import async_get as async_get_dev_registry

from .api import GroupAlarmAPI
from .coordinator import GroupAlarmCoordinator
from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_HUB_NAME,
    CONF_ORGANIZATIONS,
    CONF_ENABLE_APPOINTMENTS,
    CONF_SCAN_INTERVAL,
    CONF_APPOINTMENT_LOOKAHEAD_DAYS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_APPOINTMENT_LOOKAHEAD_DAYS
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "calendar"]


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    session = async_get_clientsession(hass)

    api = GroupAlarmAPI(
        session=session,
        api_token=entry.data[CONF_API_TOKEN],
    )

    coordinator = GroupAlarmCoordinator(
        hass=hass,
        api=api,
        hub_name=entry.data[CONF_HUB_NAME],
        orgs=entry.options.get(
            CONF_ORGANIZATIONS,
            entry.data.get(CONF_ORGANIZATIONS, []),
        ),
        enable_appointments=entry.options.get(
            CONF_ENABLE_APPOINTMENTS,
            False,
        ),
        scan_interval=entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        ),
        appointment_lookahead_days=entry.options.get(
            CONF_APPOINTMENT_LOOKAHEAD_DAYS,
            DEFAULT_APPOINTMENT_LOOKAHEAD_DAYS,
        ),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:

        dev_reg = async_get_dev_registry(hass)
        coordinator = hass.data[DOMAIN].get(entry.entry_id)

        if coordinator:
            for org_id in coordinator.orgs:
                device_id = (DOMAIN, f"org_{org_id}")

                device = dev_reg.async_get_device(identifiers={device_id})

                if device:
                    dev_reg.async_remove_device(device.id)

        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok