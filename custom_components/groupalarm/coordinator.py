# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class GroupAlarmCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, api, org_name: str):

        super().__init__(
            hass,
            logger=_LOGGER,
            name="groupalarm",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

        self.api = api
        self.org_name = org_name

    async def _async_update_data(self):

        alarms_response = await self.api.get_alarms(limit=10)
        alarms = alarms_response.get("alarms", [])

        data = {
            "alarms": alarms,
            "latest_alarm": None,
            "organization_id": self.api.org_id,
            "organization_name": self.org_name,
        }

        if alarms:
            latest_id = alarms[0].get("id")

            if latest_id:
                latest = await self.api.get_alarm(latest_id)
                data["latest_alarm"] = latest

        return data