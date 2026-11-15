"""Numbers: setpoints and settings, checked against the documented range before writing."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SwegonConfigEntry, SwegonCoordinator
from .entity import SwegonRegEntity
from .registers import Reg


async def async_setup_entry(
    hass: HomeAssistant, entry: SwegonConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        SwegonNumber(coordinator, reg) for reg in coordinator.registers if reg.platform == "number"
    )


class SwegonNumber(SwegonRegEntity, NumberEntity):
    """A holding register with a range."""

    def __init__(self, coordinator: SwegonCoordinator, reg: Reg) -> None:
        super().__init__(coordinator, reg)
        self._attr_native_min_value = reg.minimum if reg.minimum is not None else 0
        self._attr_native_max_value = reg.maximum if reg.maximum is not None else 65535
        self._attr_native_step = reg.step
        self._attr_native_unit_of_measurement = reg.unit
        self._attr_mode = NumberMode.SLIDER if reg.key == "smart_control" else NumberMode.BOX
        if reg.device_class in ("temperature", "duration"):
            self._attr_device_class = NumberDeviceClass(reg.device_class)

    @property
    def native_value(self) -> float | None:
        return self.value

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write(self.reg, value)
