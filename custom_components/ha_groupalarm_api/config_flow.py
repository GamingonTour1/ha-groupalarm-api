# Copyright (C) 2026 | GamingonTour1 | All Rights Reserved
# Unauthorized copying, distributing, and using of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Lennox Matzerath (GamingonTour1) <gamingontour2016@gmail.com>

import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, CONF_API_TOKEN, CONF_ORG_ID, CONF_ORG_NAME


class GroupAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:

            title = f"{user_input[CONF_ORG_NAME]} ({user_input[CONF_ORG_ID]})"

            return self.async_create_entry(
                title=title,
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(
                CONF_API_TOKEN,
                description={"suggested_value": "", "label": "API Token"}
            ): str,

            vol.Required(
                CONF_ORG_ID,
                description={"label": "Organisations ID (z.B. 10251)"}
            ): int,

            vol.Required(
                CONF_ORG_NAME,
                description={"label": "Organisations Name (z.B. Feuerwehr Musterstadt)"}
            ): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema
        )