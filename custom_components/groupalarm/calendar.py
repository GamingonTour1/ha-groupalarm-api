# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

from datetime import datetime

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEvent,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    if not coordinator.enable_appointments:
        return

    async_add_entities(
        [
            GroupAlarmCalendar(
                coordinator,
            )
        ]
    )


class GroupAlarmCalendar(
    CoordinatorEntity,
    CalendarEntity,
):

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(coordinator)

        self._attr_name = (
            f"GroupAlarm {coordinator.hub_name}"
        )

        self._attr_unique_id = (
            f"groupalarm_{coordinator.hub_name}_calendar"
        )

    @property
    def event(self):

        appointments = []

        for org_events in self.coordinator.data.get(
            "appointments",
            {},
        ).values():

            appointments.extend(org_events)

        if not appointments:
            return None

        appointments.sort(
            key=lambda x: x.get(
                "startDate",
                "",
            )
        )

        e = appointments[0]

        start = datetime.fromisoformat(
            e["startDate"].replace(
                "Z",
                "+00:00",
            )
        )

        end = datetime.fromisoformat(
            e["endDate"].replace(
                "Z",
                "+00:00",
            )
        )

        return CalendarEvent(
            summary=e.get(
                "display_name",
                e.get("name", ""),
            ),
            start=start,
            end=end,
            description=e.get(
                "description",
                "",
            ),
            location=e.get(
                "location",
                "",
            ),
        )

    async def async_get_events(
        self,
        hass,
        start_date,
        end_date,
    ):

        events = []

        for org_events in self.coordinator.data.get(
            "appointments",
            {},
        ).values():

            for e in org_events:

                try:

                    start = datetime.fromisoformat(
                        e["startDate"].replace(
                            "Z",
                            "+00:00",
                        )
                    )

                    end = datetime.fromisoformat(
                        e["endDate"].replace(
                            "Z",
                            "+00:00",
                        )
                    )

                    if (
                        end < start_date
                        or start > end_date
                    ):
                        continue

                    events.append(
                        CalendarEvent(
                            summary=e.get(
                                "display_name",
                                e.get("name", ""),
                            ),
                            start=start,
                            end=end,
                            description=e.get(
                                "description",
                                "",
                            ),
                            location=e.get(
                                "location",
                                "",
                            ),
                        )
                    )

                except Exception:
                    continue

        return events