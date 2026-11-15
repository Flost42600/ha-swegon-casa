"""Swegon CASA ventilation units over Modbus (SCB controller 3.0 and later)."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import UpdateFailed

from .config_flow import transport_from
from .const import CARD_URL, CONF_OFFSET, CONF_SLAVE, DOMAIN, VERSION
from .coordinator import SwegonConfigEntry, SwegonCoordinator
from .modbus import SwegonModbus

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS: list[Platform] = [
    Platform.FAN,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.BUTTON,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Serve the dashboard card shipped with the integration."""
    if hass.data.get(f"{DOMAIN}_card"):
        return True
    path = Path(__file__).parent / "frontend" / "swegon-casa-card.js"
    try:
        from homeassistant.components.frontend import add_extra_js_url
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths([StaticPathConfig(CARD_URL, str(path), cache_headers=False)])
        add_extra_js_url(hass, f"{CARD_URL}?v={VERSION}")
        hass.data[f"{DOMAIN}_card"] = True
    except Exception as err:  # noqa: BLE001 - the card is a bonus, never block the integration
        _LOGGER.warning("Could not register the dashboard card (%s); add %s as a resource", err, CARD_URL)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SwegonConfigEntry) -> bool:
    client = SwegonModbus(transport_from(dict(entry.data)), entry.data[CONF_SLAVE], entry.data[CONF_OFFSET])
    coordinator = SwegonCoordinator(hass, entry, client)
    try:
        await coordinator.async_setup()
    except UpdateFailed as err:
        await client.close()
        raise ConfigEntryNotReady(str(err)) from err
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: SwegonConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: SwegonConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.client.close()
    return unloaded
