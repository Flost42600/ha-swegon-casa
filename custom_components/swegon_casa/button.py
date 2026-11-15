"""Buttons: alarm and reminder confirmations (write-only registers)."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SwegonConfigEntry
from .entity import SwegonRegEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: SwegonConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        SwegonButton(coordinator, reg) for reg in coordinator.registers if reg.platform == "button"
    )


class SwegonButton(SwegonRegEntity, ButtonEntity):
    """Writes 1; the unit clears the register once processed."""

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_press(self) -> None:
        await self.coordinator.async_write(self.reg, self.reg.press_value, verify=False)
