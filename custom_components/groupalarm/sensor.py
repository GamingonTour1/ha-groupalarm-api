# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .utils import slugify


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for org_id in coordinator.orgs:
        entities.append(
            GroupAlarmLatestSensor(
                coordinator,
                org_id,
                entry,
            )
        )

    async_add_entities(entities)


class GroupAlarmLatestSensor(CoordinatorEntity, Entity):

    def __init__(self, coordinator, org_id, entry):
        super().__init__(coordinator)

        self.org_id = int(org_id)

        org = coordinator.org_info.get(self.org_id, {})

        org_name = org.get("name", f"Org {self.org_id}")
        org_slug = slugify(org_name)

        self._attr_name = f"{org_name} Latest Alarm"
        self._attr_unique_id = f"{org_slug}_latest_alarm"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"org_{self.org_id}")},
            name=org_name,
            manufacturer="GroupAlarm",
            model="Organization",
        )

    @property
    def state(self):
        org_data = self.coordinator.data["organizations"].get(self.org_id)

        if not org_data:
            return "no_alarm"

        alarms = org_data.get("alarms", [])

        if not alarms:
            return "no_alarm"

        return alarms[0].get("id")

    @property
    def extra_state_attributes(self):

        org_data = self.coordinator.data["organizations"].get(self.org_id)

        if not org_data:
            return {}

        alarms = org_data.get("alarms", [])
        latest = org_data.get("latest_alarm") or {}

        if not alarms:
            return {}

        return {
            "message": latest.get("message"),
            "event": latest.get("event"),
            "creator": alarms[0].get("creatorName"),
            "startDate": alarms[0].get("startDate"),
            "endDate": alarms[0].get("endDate"),
            "alarmResources": latest.get("alarmResources"),
            "optionalContent": latest.get("optionalContent"),
            "feedback": latest.get("feedback"),
            "selfFeedback": latest.get("selfFeedback"),
        }