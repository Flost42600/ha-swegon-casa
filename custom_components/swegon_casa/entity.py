"""Base entities: one device per unit, entities described by the register table."""

from __future__ import annotations

from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import SwegonCoordinator
from .registers import Reg, from_raw

_CATEGORY = {"config": EntityCategory.CONFIG, "diagnostic": EntityCategory.DIAGNOSTIC}


class SwegonEntity(CoordinatorEntity[SwegonCoordinator]):
    """An entity of the unit."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SwegonCoordinator, key: str) -> None:
        super().__init__(coordinator)
        uid = coordinator.config_entry.unique_id or coordinator.config_entry.entry_id
        self._attr_unique_id = f"{uid}_{key}"
        self._attr_translation_key = key
        device = coordinator.device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, uid)},
            name=coordinator.config_entry.title,
            manufacturer=MANUFACTURER,
            model=device.model or "CASA",
            sw_version=device.firmware_text,
            hw_version=".".join(str(v) for v in device.parameters) if device.parameters else None,
            serial_number=device.serial,
        )


class SwegonRegEntity(SwegonEntity):
    """An entity backed by one register of the table."""

    def __init__(self, coordinator: SwegonCoordinator, reg: Reg) -> None:
        super().__init__(coordinator, reg.key)
        self.reg = reg
        if reg.category:
            self._attr_entity_category = _CATEGORY[reg.category]
        self._attr_entity_registry_enabled_default = reg.enabled
        if reg.icon:
            self._attr_icon = reg.icon

    @property
    def raw(self) -> int | None:
        if self.coordinator.data is None:
            return None
        if self.reg.state_number is not None:
            return self.coordinator.data.input.get(self.reg.state_number)
        return self.coordinator.data.raw(self.reg)

    @property
    def value(self) -> float | int | None:
        return from_raw(self.reg, self.raw)

    @property
    def available(self) -> bool:
        return super().available and (self.reg.write_only and self.reg.state_number is None or self.raw is not None)
