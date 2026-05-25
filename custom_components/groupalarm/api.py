# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

import aiohttp


BASE_URL = "https://app.groupalarm.com/api/v1"


class GroupAlarmAPI:
    def __init__(self, session: aiohttp.ClientSession, token: str, org_id: int):
        self.session = session
        self.token = token
        self.org_id = org_id

    async def _get(self, url: str):
        headers = {
            "Personal-Access-Token": self.token,
            "Content-Type": "application/json",
        }

        async with self.session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"GroupAlarm API error {resp.status}: {await resp.text()}")
            return await resp.json()

    async def get_alarms(self, limit: int = 10):
        url = f"{BASE_URL}/alarms?organization={self.org_id}&limit={limit}"
        return await self._get(url)

    async def get_alarm(self, alarm_id: int):
        url = f"{BASE_URL}/alarm/{alarm_id}"
        return await self._get(url)

    async def get_organizations(self):
        url = f"{BASE_URL}/organizations"
        data = await self._get(url)

        if isinstance(data, list):
            return data

        return data.get("organizations", [])