"""Binary sensors: functions active, alarms (with the list of active alarms), sensor failures."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SwegonConfigEntry, SwegonCoordinator
from .entity import SwegonEntity, SwegonRegEntity
from .registers import (
    ALARM_BITFIELD,
    ALARM_BITS,
    GIO_DI,
    GIO_FUNCTION_MODBUS_DI,
    INFO_BITFIELD,
    SENSOR_FAILURES,
    Reg,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: SwegonConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    entities: list[BinarySensorEntity] = [
        SwegonBinarySensor(coordinator, reg)
        for reg in coordinator.registers
        if reg.platform == "binary_sensor"
    ]
    entities.append(SensorFailureSensor(coordinator, "temperature_sensor_failure"))
    for index, function in coordinator.gio.items():
        if function == GIO_FUNCTION_MODBUS_DI:
            entities.append(GioInputSensor(coordinator, index))
    async_add_entities(entities)


def _bits(raw: int | None) -> list[str]:
    if raw is None:
        return []
    return [name for bit, name in ALARM_BITS.items() if raw & (1 << bit)]


class SwegonBinarySensor(SwegonRegEntity, BinarySensorEntity):
    """On when the register is non-zero."""

    def __init__(self, coordinator: SwegonCoordinator, reg: Reg) -> None:
        super().__init__(coordinator, reg)
        if reg.device_class:
            self._attr_device_class = BinarySensorDeviceClass(reg.device_class)

    @property
    def is_on(self) -> bool | None:
        return None if self.raw is None else self.raw != 0

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self.coordinator.data
        if data is None:
            return None
        if self.reg.key == "alarm":
            return {"alarms": _bits(data.input.get(ALARM_BITFIELD))}
        if self.reg.key == "info":
            return {"infos": _bits(data.input.get(INFO_BITFIELD))}
        if self.reg.key == "defrost" and self.raw:
            return {"stage": self.raw}
        return None


class SensorFailureSensor(SwegonEntity, BinarySensorEntity):
    """Any of the temperature sensors T1..T9 failed; the list is in the attributes."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def _failed(self) -> list[str] | None:
        data = self.coordinator.data
        if data is None:
            return None
        values = {name: data.input.get(number) for name, number in SENSOR_FAILURES.items()}
        if all(v is None for v in values.values()):
            return None
        return [name for name, v in values.items() if v]

    @property
    def available(self) -> bool:
        return super().available and self._failed() is not None

    @property
    def is_on(self) -> bool | None:
        failed = self._failed()
        return None if failed is None else bool(failed)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"sensors": self._failed() or []}


class GioInputSensor(SwegonEntity, BinarySensorEntity):
    """General purpose input configured as Modbus digital input."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SwegonCoordinator, index: int) -> None:
        super().__init__(coordinator, f"gio{index + 1}_input")
        self._attr_translation_key = "gio_input"
        self._attr_translation_placeholders = {"index": str(index + 1)}
        self._number = GIO_DI[index]

    @property
    def is_on(self) -> bool | None:
        raw = self.coordinator.data.input.get(self._number) if self.coordinator.data else None
        return None if raw is None else raw != 0
