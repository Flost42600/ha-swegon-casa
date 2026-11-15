"""Sensors: measurements, status, and the heat recovery efficiency."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import SwegonConfigEntry, SwegonCoordinator
from .entity import SwegonEntity, SwegonRegEntity
from .registers import GIO_AI, GIO_FUNCTION_MODBUS_AI, Reg, by_key, from_raw

EFFICIENCY_MIN_DELTA = 3.0  # °C between extract and fresh air, below which the ratio is meaningless


async def async_setup_entry(
    hass: HomeAssistant, entry: SwegonConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        SwegonSensor(coordinator, reg) for reg in coordinator.registers if reg.platform == "sensor"
    ]
    entities.append(EfficiencySensor(coordinator, "heat_recovery_efficiency"))
    for index, function in coordinator.gio.items():
        if function == GIO_FUNCTION_MODBUS_AI:
            entities.append(GioVoltageSensor(coordinator, index))
    async_add_entities(entities)


class SwegonSensor(SwegonRegEntity, SensorEntity):
    """One register shown as a sensor."""

    def __init__(self, coordinator: SwegonCoordinator, reg: Reg) -> None:
        super().__init__(coordinator, reg)
        if reg.options:
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = list(reg.options.values())
        elif reg.device_class:
            self._attr_device_class = SensorDeviceClass(reg.device_class)
        if reg.state_class:
            self._attr_state_class = SensorStateClass(reg.state_class)
        self._attr_native_unit_of_measurement = reg.unit
        if reg.precision is not None:
            self._attr_suggested_display_precision = reg.precision

    @property
    def native_value(self) -> Any:
        if self.reg.options:
            return self.reg.options.get(self.raw) if self.raw is not None else None
        return self.value

    @property
    def available(self) -> bool:
        return super().available and self.native_value is not None


class EfficiencySensor(SwegonEntity, SensorEntity):
    """Temperature efficiency of the heat exchanger: (supply - fresh) / (extract - fresh)."""

    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0
    _attr_icon = "mdi:heat-wave"

    def _temp(self, key: str) -> float | None:
        reg = by_key()[key]
        if self.coordinator.data is None:
            return None
        return from_raw(reg, self.coordinator.data.raw(reg))  # type: ignore[return-value]

    @property
    def native_value(self) -> float | None:
        fresh = self._temp("fresh_air_temperature")
        supply = self._temp("supply_air_temperature")
        extract = self._temp("extract_air_temperature")
        if None in (fresh, supply, extract) or abs(extract - fresh) < EFFICIENCY_MIN_DELTA:  # type: ignore[operator]
            return None
        ratio = (supply - fresh) / (extract - fresh) * 100  # type: ignore[operator]
        return round(max(0.0, min(100.0, ratio)), 1)

    @property
    def available(self) -> bool:
        return super().available and self.native_value is not None


class GioVoltageSensor(SwegonEntity, SensorEntity):
    """General purpose input configured as Modbus analog input (0-10 V)."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SwegonCoordinator, index: int) -> None:
        super().__init__(coordinator, f"gio{index + 1}_voltage")
        self._attr_translation_key = "gio_voltage"
        self._attr_translation_placeholders = {"index": str(index + 1)}
        self._number = GIO_AI[index]

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.data.input.get(self._number) if self.coordinator.data else None
        return None if raw is None else round(raw / 1000, 2)
