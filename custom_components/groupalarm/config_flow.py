# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import GroupAlarmAPI
from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_HUB_NAME,
    CONF_ORGANIZATIONS,
    CONF_ENABLE_APPOINTMENTS,
)

_LOGGER = logging.getLogger(__name__)


class GroupAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            self._api_token = user_input[CONF_API_TOKEN].strip()
            self._hub_name = user_input[CONF_HUB_NAME].strip()
            self._enable_appointments = user_input.get(CONF_ENABLE_APPOINTMENTS, False)

            session = async_get_clientsession(self.hass)

            api = GroupAlarmAPI(session=session, api_token=self._api_token)

            try:
                self._organizations = await api.get_organizations()

                if not self._organizations:
                    return self.async_abort(reason="no_organizations")

                return await self.async_step_orgs()

            except Exception as err:
                _LOGGER.exception("Failed to fetch organizations: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HUB_NAME): str,
                vol.Required(CONF_API_TOKEN): str,
                vol.Optional(CONF_ENABLE_APPOINTMENTS, default=False): bool,
            }),
            errors=errors,
        )

    async def async_step_orgs(self, user_input=None):
        used_orgs = set()

        for entry in self._async_current_entries():
            used_orgs.update(entry.options.get(CONF_ORGANIZATIONS, []))

        if user_input is not None:
            return self.async_create_entry(
                title=self._hub_name,
                data={
                    CONF_API_TOKEN: self._api_token,
                    CONF_HUB_NAME: self._hub_name,
                },
                options={
                    CONF_ORGANIZATIONS: [
                        int(x) for x in user_input[CONF_ORGANIZATIONS]
                    ],
                    CONF_ENABLE_APPOINTMENTS: self._enable_appointments,
                }
            )

        options = [
            {"label": org["name"], "value": str(org["id"])}
            for org in self._organizations
            if org["id"] not in used_orgs
        ]

        return self.async_show_form(
            step_id="orgs",
            data_schema=vol.Schema({
                vol.Required(CONF_ORGANIZATIONS): SelectSelector(
                    SelectSelectorConfig(
                        options=options,
                        multiple=True,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        from .options_flow import GroupAlarmOptionsFlow
        return GroupAlarmOptionsFlow(config_entry)