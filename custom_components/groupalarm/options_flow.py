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
    CONF_API_TOKEN,
    CONF_ORGANIZATIONS,
    CONF_ENABLE_APPOINTMENTS,
    CONF_SCAN_INTERVAL,
    CONF_APPOINTMENT_LOOKAHEAD_DAYS,
)

_LOGGER = logging.getLogger(__name__)


class GroupAlarmOptionsFlow(config_entries.OptionsFlowWithConfigEntry):

    async def async_step_init(self, user_input=None):

        errors = {}

        session = async_get_clientsession(self.hass)
        api_token = self.config_entry.data.get(CONF_API_TOKEN)

        try:
            api = GroupAlarmAPI(session=session, api_token=api_token)
            organizations = await api.get_organizations()
        except Exception as err:
            _LOGGER.exception("Failed loading organizations: %s", err)
            organizations = []
            errors["base"] = "cannot_connect"

        current_orgs = self.config_entry.options.get(CONF_ORGANIZATIONS, [])
        current_enabled = self.config_entry.options.get(CONF_ENABLE_APPOINTMENTS, False)
        current_scan = self.config_entry.options.get(CONF_SCAN_INTERVAL, 30)
        current_lookahead = self.config_entry.options.get(CONF_APPOINTMENT_LOOKAHEAD_DAYS, 30)

        options = [
            {"label": org["name"], "value": str(org["id"])}
            for org in organizations
        ]

        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_ORGANIZATIONS: [
                        int(x) for x in user_input[CONF_ORGANIZATIONS]
                    ],
                    CONF_ENABLE_APPOINTMENTS: user_input[CONF_ENABLE_APPOINTMENTS],
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    CONF_APPOINTMENT_LOOKAHEAD_DAYS: user_input[CONF_APPOINTMENT_LOOKAHEAD_DAYS],
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_ORGANIZATIONS,
                    default=[str(x) for x in current_orgs],
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=options,
                        multiple=True,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),

                vol.Required(
                    CONF_ENABLE_APPOINTMENTS,
                    default=current_enabled,
                ): bool,

                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_scan,
                ): int,

                vol.Required(
                    CONF_APPOINTMENT_LOOKAHEAD_DAYS,
                    default=current_lookahead,
                ): int,
            }),
            errors=errors,
        )