# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GroupAlarmAPI
from .coordinator import GroupAlarmCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):

    session = async_get_clientsession(hass)

    org_name = entry.data["org_name"]

    api = GroupAlarmAPI(
        session=session,
        token=entry.data["api_token"],
        org_id=entry.data["org_id"],
    )

    coordinator = GroupAlarmCoordinator(
        hass,
        api,
        org_name=org_name
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["sensor", "binary_sensor"]
    )

    return True


async def async_unload_entry(hass, entry):

    hass.data[DOMAIN].pop(entry.entry_id)

    return True