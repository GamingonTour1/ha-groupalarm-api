# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

from datetime import datetime, timezone

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .utils import slugify


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        GroupAlarmActiveBinarySensor(coordinator)
    ])


class GroupAlarmActiveBinarySensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)

        org = slugify(coordinator.org_name)

        self._attr_name = f"{coordinator.org_name} Active"
        self._attr_unique_id = f"{org}_active"

    @property
    def is_on(self):

        alarms = self.coordinator.data.get("alarms", [])
        latest = self.coordinator.data.get("latest_alarm")

        if not alarms or not latest:
            return False

        end_date = latest.get("endDate")

        if not end_date:
            return True

        try:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            return datetime.now(timezone.utc) < end_dt

        except ValueError:
            return False