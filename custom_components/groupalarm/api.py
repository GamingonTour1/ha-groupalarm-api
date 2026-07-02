# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lennox Matzerath (GamingonTour1)

import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://app.groupalarm.com/api/v1"


class GroupAlarmAPI:

    def __init__(self, session: aiohttp.ClientSession, api_token: str):
        self.session = session
        self.api_token = api_token.strip()

    def _headers(self):
        return {
            "Accept": "application/json",
            "Personal-Access-Token": self.api_token,
            "API-TOKEN": self.api_token,
        }

    async def _get(self, url: str, params=None):

        async with self.session.get(
            url,
            headers=self._headers(),
            params=params,
        ) as resp:

            text = await resp.text()

            if resp.status == 401:
                raise Exception("Unauthorized - check API token")

            if resp.status != 200:
                _LOGGER.error("GroupAlarm API error %s: %s", resp.status, text)
                raise Exception(f"GroupAlarm API error {resp.status}: {text}")

            try:
                return await resp.json()
            except Exception:
                _LOGGER.error("Invalid JSON response: %s", text)
                return {}

    async def get_organizations(self):
        url = f"{BASE_URL}/organizations"
        data = await self._get(url)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get("organizations", [])

        return []

    async def get_alarms(self, org_id: int, limit: int = 10):
        url = f"{BASE_URL}/alarms"

        data = await self._get(
            url,
            params={"organization": org_id, "limit": limit},
        )

        if isinstance(data, list):
            return data

        return data.get("alarms", [])

    async def get_alarm(self, alarm_id: int):
        return await self._get(f"{BASE_URL}/alarm/{alarm_id}")

    async def get_user(self):
        return await self._get(f"{BASE_URL}/user")

    async def get_appointment(self, appointment_id: int):
        return await self._get(f"{BASE_URL}/appointment/{appointment_id}")

    async def get_appointments(self, start: str, end: str, org_id: int | None = None, type_: str = "organization"):

        params = {
            "start": start,
            "end": end,
            "type": type_,
        }

        if org_id:
            params["organization_id"] = org_id

        data = await self._get(f"{BASE_URL}/appointments/calendar", params=params)

        if isinstance(data, list):
            return data

        return data.get("appointments", [])