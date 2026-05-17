# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .utils import slugify


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        GroupAlarmLatestSensor(coordinator)
    ])


class GroupAlarmLatestSensor(CoordinatorEntity, Entity):

    def __init__(self, coordinator):

        super().__init__(coordinator)

        org = slugify(coordinator.org_name)

        self._attr_name = f"{coordinator.org_name} Latest Alarm"
        self._attr_unique_id = f"{org}_latest_alarm"

    @property
    def state(self):

        alarms = self.coordinator.data.get("alarms", [])

        return alarms[0].get("id") if alarms else "no_alarm"

    @property
    def extra_state_attributes(self):

        alarms = self.coordinator.data.get("alarms", [])
        latest = self.coordinator.data.get("latest_alarm") or {}

        if not alarms:
            return

        return {
            "message": latest.get("message"),
            "event": latest.get("event"),
            "creator": alarms[0].get("creatorName"),
            "startDate": alarms[0].get("startDate"),
            "endDate": alarms[0].get("endDate"),
            "alarmResources": latest.get("alarmResources"),
            "optionalContent": latest.get("optionalContent"),
            "feedback": latest.get("feedback"),
        }