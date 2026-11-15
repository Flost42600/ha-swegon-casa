"""Config flow: serial (USB RS-485) or TCP gateway, automatic detection, optional equipment."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_BAUDRATE,
    CONF_KIND,
    CONF_OFFSET,
    CONF_PARITY,
    CONF_SERIAL_PORT,
    CONF_SLAVE,
    CONF_STOPBITS,
    CONF_TCP_PORT,
    DEFAULT_BAUDRATE,
    DEFAULT_PARITY,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SETTINGS_INTERVAL,
    DEFAULT_STOPBITS,
    DEFAULT_TCP_PORT,
    DOMAIN,
    OPT_FEATURES,
    OPT_SCAN_INTERVAL,
    OPT_SETTINGS_INTERVAL,
)
from .modbus import SwegonModbus, SwegonModbusError, Transport, detect
from .registers import FEATURES, MODEL_NAME, SERIAL_NUMBER, by_key, from_raw

_LOGGER = logging.getLogger(__name__)

AUTO = 0  # slave id 0 in the form = detect


def transport_from(data: dict[str, Any]) -> Transport:
    if data[CONF_KIND] == "serial":
        return Transport(
            kind="serial",
            port=data[CONF_SERIAL_PORT],
            baudrate=int(data.get(CONF_BAUDRATE, DEFAULT_BAUDRATE)),
            parity=data.get(CONF_PARITY, DEFAULT_PARITY),
            stopbits=int(data.get(CONF_STOPBITS, DEFAULT_STOPBITS)),
        )
    return Transport(kind="tcp", host=data[CONF_HOST], tcp_port=int(data.get(CONF_TCP_PORT, DEFAULT_TCP_PORT)))


def _list_serial_ports() -> list[SelectOptionDict]:
    """Serial ports, by-id paths first since they survive reboots."""
    from serial.tools import list_ports

    options: list[SelectOptionDict] = []
    for port in list_ports.comports():
        path = port.device
        try:
            import os

            by_id = "/dev/serial/by-id"
            if os.path.isdir(by_id):
                for name in os.listdir(by_id):
                    if os.path.realpath(os.path.join(by_id, name)) == os.path.realpath(path):
                        path = os.path.join(by_id, name)
                        break
        except OSError:
            pass
        label = f"{path} — {port.description}" if port.description and port.description != "n/a" else path
        options.append(SelectOptionDict(value=path, label=label))
    return options


class SwegonConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swegon CASA."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._title = "Swegon CASA"
        self._serial: str | None = None
        self._suggested: list[str] = []

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return SwegonOptionsFlow()

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="user", menu_options=["serial", "tcp"])

    async def async_step_serial(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {CONF_KIND: "serial", **user_input}
            errors = await self._async_test(data)
            if not errors:
                return await self.async_step_features()
        ports = await self.hass.async_add_executor_job(_list_serial_ports)
        schema = vol.Schema(
            {
                vol.Required(CONF_SERIAL_PORT): SelectSelector(
                    SelectSelectorConfig(options=ports, custom_value=True, mode=SelectSelectorMode.DROPDOWN)
                ),
                vol.Required(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): vol.In([9600, 19200, 38400, 57600, 115200]),
                vol.Required(CONF_PARITY, default=DEFAULT_PARITY): vol.In({"N": "None", "E": "Even", "O": "Odd"}),
                vol.Required(CONF_STOPBITS, default=DEFAULT_STOPBITS): vol.In([1, 2]),
                vol.Required(CONF_SLAVE, default=AUTO): NumberSelector(
                    NumberSelectorConfig(min=0, max=247, mode=NumberSelectorMode.BOX)
                ),
            }
        )
        return self.async_show_form(
            step_id="serial", data_schema=self.add_suggested_values_to_schema(schema, user_input), errors=errors
        )

    async def async_step_tcp(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {CONF_KIND: "tcp", **user_input}
            errors = await self._async_test(data)
            if not errors:
                return await self.async_step_features()
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_TCP_PORT, default=DEFAULT_TCP_PORT): NumberSelector(
                    NumberSelectorConfig(min=1, max=65535, mode=NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_SLAVE, default=AUTO): NumberSelector(
                    NumberSelectorConfig(min=0, max=247, mode=NumberSelectorMode.BOX)
                ),
            }
        )
        return self.async_show_form(
            step_id="tcp", data_schema=self.add_suggested_values_to_schema(schema, user_input), errors=errors
        )

    async def _async_test(self, data: dict[str, Any]) -> dict[str, str]:
        """Find the unit, read its name and serial number, guess the equipment."""
        transport = transport_from(data)
        wanted = int(data.get(CONF_SLAVE, AUTO))
        slaves = (wanted,) if wanted else (1, 16)
        try:
            slave, offset, firmware = await detect(transport, slaves=slaves)
        except SwegonModbusError as err:
            _LOGGER.info("Swegon CASA not found: %s", err)
            return {"base": "cannot_connect"}
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Unexpected error while looking for the unit")
            return {"base": "unknown"}
        client = SwegonModbus(transport, slave, offset)
        try:
            model = await client.read_text(*MODEL_NAME)
            self._serial = await client.read_text(*SERIAL_NUMBER)
            self._suggested = await self._guess_features(client)
        except SwegonModbusError:
            model = None
        finally:
            await client.close()
        self._data = {**data, CONF_SLAVE: slave, CONF_OFFSET: offset}
        self._title = f"Swegon {model}" if model else "Swegon CASA"
        _LOGGER.info("Found %s (firmware %s) at slave %s, offset %s", self._title, firmware, slave, offset)
        return {}

    @staticmethod
    async def _guess_features(client: SwegonModbus) -> list[str]:
        regs = by_key()
        values = await client.read("input", [regs["co2"].number, regs["humidity"].number, regs["panel1_temperature"].number])
        guess = []
        if values.get(regs["co2"].number) or values.get(regs["humidity"].number):
            guess.append("air_quality")
        if from_raw(regs["panel1_temperature"], values.get(regs["panel1_temperature"].number)) not in (None, 0):
            guess.append("user_panel")
        return guess

    async def async_step_features(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            await self.async_set_unique_id(self._serial or self._data.get(CONF_SERIAL_PORT) or self._data.get(CONF_HOST))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._title,
                data=self._data,
                options={
                    OPT_FEATURES: user_input[OPT_FEATURES],
                    OPT_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                    OPT_SETTINGS_INTERVAL: DEFAULT_SETTINGS_INTERVAL,
                },
            )
        return self.async_show_form(
            step_id="features",
            data_schema=vol.Schema({vol.Required(OPT_FEATURES, default=self._suggested): _features_selector()}),
            description_placeholders={"model": self._title},
        )


def _features_selector() -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(options=list(FEATURES), multiple=True, translation_key="features")
    )


class SwegonOptionsFlow(OptionsFlow):
    """Equipment and polling intervals."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(OPT_FEATURES, default=options.get(OPT_FEATURES, [])): _features_selector(),
                vol.Required(OPT_SCAN_INTERVAL, default=options.get(OPT_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=300)
                ),
                vol.Required(
                    OPT_SETTINGS_INTERVAL, default=options.get(OPT_SETTINGS_INTERVAL, DEFAULT_SETTINGS_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=15, max=3600)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
