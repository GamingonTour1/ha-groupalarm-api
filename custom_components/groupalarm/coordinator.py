# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

from datetime import timedelta, datetime, timezone
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class GroupAlarmCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, api, hub_name: str, orgs: list[int], enable_appointments: bool,
                 scan_interval: int = 30,
                 appointment_lookahead_days: int = 30):

        super().__init__(
            hass,
            logger=_LOGGER,
            name=hub_name,
            update_interval=timedelta(seconds=scan_interval),
        )

        self.api = api
        self.hub_name = hub_name
        self.orgs = orgs
        self.enable_appointments = enable_appointments

        self.scan_interval = scan_interval
        self.lookahead_days = appointment_lookahead_days

        self.org_info = {}

    async def _async_update_data(self):

        try:
            organizations = await self.api.get_organizations()
            user = await self.api.get_user()
            user_id = user["id"]

            result = {
                "organizations": {},
                "appointments": {},
            }

            now = datetime.now(timezone.utc)

            active_org_ids = set()

            for org in organizations:

                org_id = org["id"]
                self.org_info[org_id] = org

                if org_id not in self.orgs:
                    continue

                active_org_ids.add(org_id)

                alarms = await self.api.get_alarms(org_id)

                latest_alarm = None
                if alarms:
                    latest_alarm = await self.api.get_alarm(alarms[0]["id"])

                result["organizations"][org_id] = {
                    "alarms": alarms,
                    "latest_alarm": latest_alarm,
                }

                if self.enable_appointments:

                    start = now.isoformat()
                    end = (now + timedelta(days=self.lookahead_days)).isoformat()

                    appointments = await self.api.get_appointments(
                        start=start,
                        end=end,
                        org_id=org_id,
                    )

                    cleaned = []

                    for a in appointments:

                        try:
                            full = await self.api.get_appointment(a["id"])

                            feedback = 0

                            for participant in full.get("participants", []):
                                if participant.get("userID") == user_id:
                                    feedback = participant.get("feedback", 0)
                                    break

                            if feedback == 2:
                                continue

                            name = a.get("name", "")

                            if feedback == 0:
                                display = f"[?] {name}"
                            else:
                                display = name

                            a["display_name"] = display
                            cleaned.append(a)

                        except Exception:
                            continue

                    result["appointments"][org_id] = cleaned

            self._active_orgs = active_org_ids

            return result

        except Exception as err:
            raise UpdateFailed(str(err)) from err