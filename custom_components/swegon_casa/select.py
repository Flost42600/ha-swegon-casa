"""Selects: operating mode and the multi-level automatic functions."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SwegonConfigEntry, SwegonCoordinator
from .entity import SwegonRegEntity
from .registers import Reg


async def async_setup_entry(
    hass: HomeAssistant, entry: SwegonConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        SwegonSelect(coordinator, reg) for reg in coordinator.registers if reg.platform == "select"
    )


class SwegonSelect(SwegonRegEntity, SelectEntity):
    """A holding register with named values."""

    def __init__(self, coordinator: SwegonCoordinator, reg: Reg) -> None:
        super().__init__(coordinator, reg)
        self._attr_options = list(reg.options.values())
        self._to_raw = {key: raw for raw, key in reg.options.items()}

    @property
    def current_option(self) -> str | None:
        return None if self.raw is None else self.reg.options.get(self.raw)

    async def async_select_option(self, option: str) -> None:
        if option not in self._to_raw:
            raise HomeAssistantError(f"Unknown option {option}")
        await self.coordinator.async_write(self.reg, self._to_raw[option])
