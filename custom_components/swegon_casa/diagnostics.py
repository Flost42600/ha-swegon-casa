"""Diagnostics: settings, detected unit and every raw register (serial number masked)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .coordinator import SwegonConfigEntry

TO_REDACT = {"unique_id", "serial_number", "host"}


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: SwegonConfigEntry) -> dict[str, Any]:
    coordinator = entry.runtime_data
    data = coordinator.data
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "unit": coordinator.diagnostics(),
        "input": {str(k): v for k, v in sorted(data.input.items())} if data else None,
        "holding": {str(k): v for k, v in sorted(data.holding.items())} if data else None,
    }
