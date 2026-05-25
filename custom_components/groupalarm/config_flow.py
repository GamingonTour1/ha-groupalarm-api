import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_ORG_ID,
    CONF_ORG_NAME,
)
from .api import GroupAlarmAPI


class GroupAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.api_token = None
        self.organizations = {}

    async def async_step_user(self, user_input=None):

        if self._async_current_entries():
            self.api_token = self._async_current_entries()[0].data[CONF_API_TOKEN]
            return await self.async_step_org()

        if user_input is not None:
            self.api_token = user_input[CONF_API_TOKEN]
            return await self.async_step_org()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_TOKEN): str,
            }),
        )

    async def async_step_org(self, user_input=None):

        if not self.api_token:
            return self.async_abort(reason="missing_token")

        session = async_get_clientsession(self.hass)

        api = GroupAlarmAPI(
            session=session,
            token=self.api_token,
            org_id=0,
        )

        try:
            orgs = await api.get_organizations()
        except Exception:
            return self.async_abort(reason="cannot_connect")

        used_org_ids = {
            entry.data[CONF_ORG_ID]
            for entry in self._async_current_entries()
        }

        available_orgs = {
            str(org["id"]): org["name"]
            for org in orgs
            if org["id"] not in used_org_ids
        }

        if not available_orgs:
            return self.async_abort(reason="no_organizations")

        if user_input is not None:

            org_id = int(user_input["org_id"])
            org_name = available_orgs[str(org_id)]

            return self.async_create_entry(
                title=org_name,
                data={
                    CONF_API_TOKEN: self.api_token,
                    CONF_ORG_ID: org_id,
                    CONF_ORG_NAME: org_name,
                },
            )

        return self.async_show_form(
            step_id="org",
            data_schema=vol.Schema({
                vol.Required("org_id"): vol.In(available_orgs)
            }),
        )