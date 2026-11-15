"""Switches: on/off settings and functions, plus GIO relays set to Modbus."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SwegonConfigEntry, SwegonCoordinator
from .entity import SwegonEntity, SwegonRegEntity
from .registers import GIO_FUNCTION_MODBUS_DO, GIO_RELAYS


async def async_setup_entry(
    hass: HomeAssistant, entry: SwegonConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    entities: list[SwitchEntity] = [
        SwegonSwitch(coordinator, reg) for reg in coordinator.registers if reg.platform == "switch"
    ]
    for index, function in coordinator.gio.items():
        if function == GIO_FUNCTION_MODBUS_DO:
            entities.append(GioRelaySwitch(coordinator, index))
    async_add_entities(entities)


class SwegonSwitch(SwegonRegEntity, SwitchEntity):
    """1 = on, 0 = off. Write-only functions (fireplace) take their state from a status register."""

    @property
    def is_on(self) -> bool | None:
        return None if self.raw is None else self.raw != 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_write(self.reg, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_write(self.reg, 0)


class GioRelaySwitch(SwegonEntity, SwitchEntity):
    """General purpose output configured as Modbus relay."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: SwegonCoordinator, index: int) -> None:
        super().__init__(coordinator, f"gio{index + 1}_relay")
        self._attr_translation_key = "gio_relay"
        self._attr_translation_placeholders = {"index": str(index + 1)}
        self._number = GIO_RELAYS[index]

    @property
    def is_on(self) -> bool | None:
        raw = self.coordinator.data.holding.get(self._number) if self.coordinator.data else None
        return None if raw is None else raw != 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_write_number(self._number, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_write_number(self._number, 0)
