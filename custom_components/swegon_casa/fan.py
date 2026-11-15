"""Fan entity: the ventilation with its modes as presets (Away, Home, Boost, Travelling)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SwegonConfigEntry, SwegonCoordinator
from .entity import SwegonEntity
from .registers import by_key

PRESETS = {"away": 1, "home": 2, "boost": 3, "travelling": 4}
STOPPED = 0


async def async_setup_entry(
    hass: HomeAssistant, entry: SwegonConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([SwegonFan(entry.runtime_data)])


class SwegonFan(SwegonEntity, FanEntity):
    """Ventilation on/off and mode."""

    _attr_name = None  # the device name
    _attr_preset_modes = list(PRESETS)
    _attr_supported_features = (
        FanEntityFeature.PRESET_MODE | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: SwegonCoordinator) -> None:
        super().__init__(coordinator, "ventilation")
        self._reg = by_key()["operating_mode"]

    @property
    def _mode(self) -> int | None:
        return self.coordinator.data.raw(self._reg) if self.coordinator.data else None

    @property
    def available(self) -> bool:
        return super().available and self._mode is not None

    @property
    def is_on(self) -> bool | None:
        mode = self._mode
        return None if mode is None else mode != STOPPED

    @property
    def preset_mode(self) -> str | None:
        mode = self._mode
        return next((name for name, value in PRESETS.items() if value == mode), None)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self.coordinator.async_write(self._reg, PRESETS[preset_mode])

    async def async_turn_on(
        self, percentage: int | None = None, preset_mode: str | None = None, **kwargs: Any
    ) -> None:
        await self.coordinator.async_write(self._reg, PRESETS[preset_mode or "home"])

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_write(self._reg, STOPPED)
