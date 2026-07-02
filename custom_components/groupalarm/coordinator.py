# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

from datetime import timedelta, datetime, timezone
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class GroupAlarmCoordinator(DataUpdateCoordinator):

    def __init__(
        self,
        hass,
        api,
        hub_name: str,
        orgs: list[int],
        enable_appointments: bool,
        scan_interval: int = 30,
        appointment_lookahead_days: int = 30,
    ):

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
        self.user_id = None

    def _build_self_feedback(self, alarm: dict):
        """Berechnet eigenes Feedback aus Alarmdaten"""

        if not alarm:
            return {
                "feedback": False,
                "state": "NO_ALARM",
                "responseTime": None,
                "duration": None,
                "comment": None,
            }

        feedback_list = alarm.get("feedback", [])
        user_id = self.user_id

        if not user_id or not isinstance(feedback_list, list):
            return {
                "feedback": False,
                "state": "UNKNOWN",
                "responseTime": None,
                "duration": None,
                "comment": None,
            }

        for entry in feedback_list:
            if entry.get("userID") == user_id:
                return {
                    "feedback": entry.get("feedback", False),
                    "state": entry.get("state", "UNKNOWN"),
                    "responseTime": entry.get("responseTime"),
                    "duration": entry.get("userDuration"),
                    "comment": entry.get("userComment"),
                }

        return {
            "feedback": False,
            "state": "NOT_ALARMED",
            "responseTime": None,
            "duration": None,
            "comment": None,
        }

    async def _async_update_data(self):

        try:
            organizations = await self.api.get_organizations()
            user = await self.api.get_user()
            self.user_id = user["id"]

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

                    latest_alarm["selfFeedback"] = self._build_self_feedback(latest_alarm)

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

                            participants = full.get("participants", [])

                            is_participant = False
                            feedback_value = None

                            for p in participants:
                                if p.get("userID") == self.user_id:
                                    is_participant = True
                                    feedback_value = p.get("feedback", 0)
                                    break

                            if not is_participant:
                                continue

                            if feedback_value == 2:
                                continue

                            name = a.get("name", "")

                            a["display_name"] = (
                                f"[?] {name}" if feedback_value == 0 else name
                            )

                            cleaned.append(a)

                        except Exception:
                            continue

                    result["appointments"][org_id] = cleaned

            self._active_orgs = active_org_ids

            return result

        except Exception as err:
            raise UpdateFailed(str(err)) from err