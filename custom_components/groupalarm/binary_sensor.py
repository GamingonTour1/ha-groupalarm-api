# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

from datetime import datetime, timezone

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
            GroupAlarmActiveBinarySensor(
                coordinator,
                org_id,
                entry,
            )
        )

    async_add_entities(entities)


class GroupAlarmActiveBinarySensor(
    CoordinatorEntity,
    BinarySensorEntity,
):

    def __init__(
        self,
        coordinator,
        org_id,
        entry,
    ):
        super().__init__(coordinator)

        self.org_id = int(org_id)

        org = coordinator.org_info.get(
            self.org_id,
            {},
        )

        org_name = org.get(
            "name",
            f"Org {self.org_id}",
        )

        org_slug = slugify(org_name)

        self._attr_name = f"{org_name} Active"
        self._attr_unique_id = f"{org_slug}_active"

        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"org_{self.org_id}",
                )
            },
            name=org_name,
            manufacturer="GroupAlarm",
            model="Organization",
        )

    @property
    def is_on(self):

        org_data = self.coordinator.data["organizations"].get(
            self.org_id
        )

        if not org_data:
            return False

        latest = org_data.get("latest_alarm")

        if not latest:
            return False

        end_date = latest.get("endDate")

        if not end_date:
            return True

        try:
            end_dt = datetime.fromisoformat(
                end_date.replace(
                    "Z",
                    "+00:00",
                )
            )

            return (
                datetime.now(timezone.utc)
                < end_dt
            )

        except ValueError:
            return False