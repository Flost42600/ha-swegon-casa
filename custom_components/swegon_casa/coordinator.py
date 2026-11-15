"""Polling of the Swegon CASA unit and writes."""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SETTINGS_INTERVAL,
    DOMAIN,
    OPT_FEATURES,
    OPT_SCAN_INTERVAL,
    OPT_SETTINGS_INTERVAL,
)
from .modbus import SwegonModbus, SwegonModbusError, SwegonWriteError
from .registers import (
    ALARM_BITFIELD,
    FIRMWARE,
    GIO_AI,
    GIO_DI,
    GIO_FUNCTIONS,
    GIO_RELAYS,
    INFO_BITFIELD,
    MODEL_NAME,
    PARAMETERS,
    REGISTERS,
    SENSOR_FAILURES,
    SERIAL_NUMBER,
    Reg,
    applicable,
    to_raw,
)

_LOGGER = logging.getLogger(__name__)


def has_rotor(model: str | None) -> bool:
    """R-series CASA units (R3, R5, R15…) have a rotary heat exchanger, W-series a plate one."""
    return bool(model and re.search(r"\bR\d", model.upper()))

type SwegonConfigEntry = ConfigEntry["SwegonCoordinator"]


@dataclass
class DeviceInfo:
    firmware: tuple[int, int, int] = (3, 0, 0)
    parameters: tuple[int, int] | None = None
    model: str | None = None
    serial: str | None = None

    @property
    def sw(self) -> tuple[int, int]:
        return self.firmware[0], self.firmware[1]

    @property
    def firmware_text(self) -> str:
        return ".".join(str(v) for v in self.firmware)


@dataclass
class SwegonData:
    input: dict[int, int | None] = field(default_factory=dict)
    holding: dict[int, int | None] = field(default_factory=dict)

    def raw(self, reg: Reg) -> int | None:
        table = self.input if reg.table == "input" else self.holding
        return table.get(reg.number)


class SwegonCoordinator(DataUpdateCoordinator[SwegonData]):
    """Reads measurements every scan interval and settings less often."""

    config_entry: SwegonConfigEntry

    def __init__(self, hass: HomeAssistant, entry: SwegonConfigEntry, client: SwegonModbus) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {entry.title}",
            update_interval=timedelta(
                seconds=entry.options.get(OPT_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )
        self.client = client
        self.features: set[str] = set(entry.options.get(OPT_FEATURES, []))
        self._settings_interval = entry.options.get(OPT_SETTINGS_INTERVAL, DEFAULT_SETTINGS_INTERVAL)
        self._last_settings = 0.0
        self.device = DeviceInfo()
        self.registers: list[Reg] = []
        self.gio: dict[int, int] = {}  # GIO index (0-4) -> configured function
        self.last_error: str | None = None

    async def async_setup(self) -> None:
        """Read the device information once and choose the registers of this unit."""
        try:
            fw = await self.client.read("input", list(FIRMWARE))
            params = await self.client.read("input", list(PARAMETERS))
            model = await self.client.read_text(*MODEL_NAME)
            serial = await self.client.read_text(*SERIAL_NUMBER)
        except SwegonModbusError as err:
            raise UpdateFailed(str(err)) from err
        if fw[FIRMWARE[0]] is not None:
            self.device.firmware = tuple(fw[n] or 0 for n in FIRMWARE)  # type: ignore[assignment]
        if params[PARAMETERS[0]] is not None:
            self.device.parameters = tuple(params[n] or 0 for n in PARAMETERS)  # type: ignore[assignment]
        self.device.model = model
        self.device.serial = serial
        if has_rotor(model):
            self.features.add("rotor")
        self.registers = [r for r in REGISTERS if applicable(r, self.features, self.device.sw)]
        if "gio" in self.features:
            functions = await self.client.read("holding", list(GIO_FUNCTIONS))
            self.gio = {i: functions[n] or 0 for i, n in enumerate(GIO_FUNCTIONS)}
        _LOGGER.debug(
            "Swegon %s, firmware %s, %d registers", model, self.device.firmware_text, len(self.registers)
        )

    def _numbers(self, table: str) -> list[int]:
        numbers = [
            r.number for r in self.registers if r.table == table and not r.write_only
        ] + [r.state_number for r in self.registers if r.state_number and table == "input"]
        if table == "input":
            numbers += [ALARM_BITFIELD, INFO_BITFIELD, *SENSOR_FAILURES.values()]
            if self.gio:
                numbers += [*GIO_DI, *GIO_AI]
        elif self.gio:
            numbers += list(GIO_RELAYS)
        return numbers

    async def _async_update_data(self) -> SwegonData:
        data = SwegonData(
            input={} if self.data is None else dict(self.data.input),
            holding={} if self.data is None else dict(self.data.holding),
        )
        now = time.monotonic()
        try:
            data.input.update(await self.client.read("input", self._numbers("input")))
            if self.data is None or now - self._last_settings >= self._settings_interval:
                data.holding.update(await self.client.read("holding", self._numbers("holding")))
                self._last_settings = now
        except SwegonModbusError as err:
            self.last_error = str(err)
            raise UpdateFailed(str(err)) from err
        self.last_error = None
        return data

    async def async_write(self, reg: Reg, value: float, verify: bool | None = None) -> None:
        """Write a value (entity units), then refresh the data right away."""
        try:
            raw = to_raw(reg, value)
            await self.client.write(reg.number, raw, verify=not reg.write_only if verify is None else verify)
        except (SwegonModbusError, SwegonWriteError, ValueError) as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_failed",
                translation_placeholders={"name": reg.name_en, "reason": str(err)},
            ) from err
        if not reg.write_only and self.data is not None:
            self.data.holding[reg.number] = raw
        self._last_settings = 0.0  # re-read the settings on this refresh
        await self.async_refresh()

    async def async_write_number(self, number: int, raw: int) -> None:
        """Write a raw holding register that has no definition (GIO relays)."""
        try:
            await self.client.write(number, raw)
        except (SwegonModbusError, SwegonWriteError) as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_failed",
                translation_placeholders={"name": str(number), "reason": str(err)},
            ) from err
        if self.data is not None:
            self.data.holding[number] = raw
        await self.async_refresh()

    def diagnostics(self) -> dict[str, Any]:
        return {
            "firmware": self.device.firmware_text,
            "parameters": self.device.parameters,
            "model": self.device.model,
            "features": sorted(self.features),
            "slave": self.client.slave,
            "offset": self.client.offset,
            "registers": len(self.registers),
            "missing_registers": sorted(f"{t}:{n}" for t, n in self.client._missing),
            "gio": self.gio,
            "last_error": self.last_error,
        }
