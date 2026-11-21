"""Config flow, setup and entities against the simulated unit."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.swegon_casa.const import (
    CONF_BAUDRATE,
    CONF_KIND,
    CONF_OFFSET,
    CONF_PARITY,
    CONF_SERIAL_PORT,
    CONF_SLAVE,
    CONF_STOPBITS,
    DOMAIN,
    OPT_FEATURES,
)

PORT = "/dev/serial/by-id/usb-FTDI_RS485-if00-port0"
P = "swegon_casa_w3"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def serial_ports():
    with patch(
        "custom_components.swegon_casa.config_flow._list_serial_ports",
        return_value=[{"value": PORT, "label": PORT}],
    ):
        yield


def make_entry(features: list[str]) -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        title="Swegon CASA W3",
        unique_id="SW1234567",
        data={
            CONF_KIND: "serial", CONF_SERIAL_PORT: PORT, CONF_BAUDRATE: 38400,
            CONF_PARITY: "N", CONF_STOPBITS: 1, CONF_SLAVE: 1, CONF_OFFSET: -1,
        },
        options={OPT_FEATURES: features, "scan_interval": 15, "settings_interval": 60},
    )


async def setup(hass: HomeAssistant, features=("air_quality", "user_panel")) -> MockConfigEntry:
    entry = make_entry(list(features))
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def state(hass: HomeAssistant, entity_id: str) -> str:
    s = hass.states.get(entity_id)
    assert s is not None, f"{entity_id} missing"
    return s.state


# ------------------------------------------------------------------ config flow


async def test_flow_serial_detects_unit_and_equipment(hass: HomeAssistant, fake_bus, unit):
    unit.slave = 16
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.MENU
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"next_step_id": "serial"})
    assert result["step_id"] == "serial"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_SERIAL_PORT: PORT, CONF_BAUDRATE: 38400, CONF_PARITY: "N", CONF_STOPBITS: 1, CONF_SLAVE: 0},
    )
    assert result["step_id"] == "features"
    assert result["description_placeholders"]["model"] == "Swegon CASA W3"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {OPT_FEATURES: ["air_quality", "user_panel"]}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Swegon CASA W3"
    assert result["data"][CONF_SLAVE] == 16 and result["data"][CONF_OFFSET] == -1
    assert result["result"].unique_id == "SW1234567"
    await hass.async_block_till_done()


async def test_flow_reports_no_answer(hass: HomeAssistant, fake_bus, unit):
    unit.slave = 99
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"next_step_id": "serial"})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_SERIAL_PORT: PORT, CONF_BAUDRATE: 38400, CONF_PARITY: "N", CONF_STOPBITS: 1, CONF_SLAVE: 0},
    )
    assert result["errors"] == {"base": "cannot_connect"}


# --------------------------------------------------------------------- entities


async def test_measurements_and_status(hass: HomeAssistant, fake_bus):
    await setup(hass)
    assert state(hass, f"sensor.{P}_fresh_air_temperature") == "5.5"
    assert state(hass, f"sensor.{P}_supply_air_temperature") == "18.5"
    assert state(hass, f"sensor.{P}_co2") == "650"
    assert state(hass, f"sensor.{P}_relative_humidity") == "45"
    assert state(hass, f"sensor.{P}_unit_state") == "normal"
    assert state(hass, f"sensor.{P}_ventilation_level") == "home"
    # (18.5 - 5.5) / (21.5 - 5.5) = 81.25 %
    assert state(hass, f"sensor.{P}_heat_recovery_efficiency") == "81.2"
    assert hass.states.get(f"binary_sensor.{P}_rotor_active") is None  # W3: plate exchanger, no rotor
    assert state(hass, f"sensor.{P}_bypass_position") == "0"
    assert state(hass, f"fan.{P}") == "on"
    assert hass.states.get(f"fan.{P}").attributes["preset_mode"] == "home"


async def test_alarm_attributes_and_confirmation(hass: HomeAssistant, fake_bus, unit):
    await setup(hass)
    alarm = hass.states.get(f"binary_sensor.{P}_active_alarm")
    assert alarm.state == "on" and alarm.attributes["alarms"] == ["filter_guard"]
    assert state(hass, f"binary_sensor.{P}_filter_guard_info") == "on"
    assert state(hass, f"binary_sensor.{P}_temperature_sensor_failure") == "off"
    await hass.services.async_call(
        "button", "press", {"entity_id": f"button.{P}_confirm_filter_guard"}, blocking=True
    )
    assert (5404, 1) in unit.writes
    assert state(hass, f"binary_sensor.{P}_filter_guard_info") == "off"


async def test_operating_mode_from_select_and_fan(hass: HomeAssistant, fake_bus, unit):
    await setup(hass)
    await hass.services.async_call(
        "select", "select_option", {"entity_id": f"select.{P}_operating_mode", "option": "boost"}, blocking=True
    )
    assert unit.holding[5001] == 3
    assert state(hass, f"select.{P}_operating_mode") == "boost"
    await hass.services.async_call(
        "fan", "set_preset_mode", {"entity_id": f"fan.{P}", "preset_mode": "away"}, blocking=True
    )
    assert unit.holding[5001] == 1
    await hass.services.async_call("fan", "turn_off", {"entity_id": f"fan.{P}"}, blocking=True)
    assert unit.holding[5001] == 0
    assert state(hass, f"fan.{P}") == "off"


async def test_numbers_signed_and_ranges(hass: HomeAssistant, fake_bus, unit):
    await setup(hass)
    await hass.services.async_call(
        "number", "set_value", {"entity_id": f"number.{P}_smart_control", "value": -20}, blocking=True
    )
    assert unit.holding[5019] == (-20) & 0xFFFF
    assert state(hass, f"number.{P}_smart_control") == "-20"
    with pytest.raises(HomeAssistantError):  # outside the documented 0-60 min
        await hass.services.async_call(
            "number", "set_value", {"entity_id": f"number.{P}_fireplace_run_time", "value": 90}, blocking=True
        )
    assert unit.holding[5104] == 15


async def test_fireplace_switch_follows_status_register(hass: HomeAssistant, fake_bus, unit):
    await setup(hass)
    assert state(hass, f"switch.{P}_fireplace_function") == "off"
    await hass.services.async_call("switch", "turn_on", {"entity_id": f"switch.{P}_fireplace_function"}, blocking=True)
    assert (5002, 1) in unit.writes
    assert state(hass, f"switch.{P}_fireplace_function") == "on"


async def test_equipment_gates_entities(hass: HomeAssistant, fake_bus):
    await setup(hass, features=())
    assert hass.states.get(f"sensor.{P}_co2") is None
    assert hass.states.get(f"sensor.{P}_user_panel_1_temperature") is None
    assert hass.states.get(f"number.{P}_temperature_setpoint") is None  # no heater
    assert hass.states.get(f"sensor.{P}_fresh_air_temperature") is not None


async def test_software_version_gates_entities(hass: HomeAssistant, fake_bus, unit):
    unit.input[6002] = 0  # firmware 3.0: humidity control is a simple on/off
    unit.holding[5010] = 1
    await setup(hass)
    assert hass.states.get(f"select.{P}_auto_humidity_control") is None
    assert state(hass, f"switch.{P}_auto_humidity_control") == "on"


async def test_write_failure_is_reported(hass: HomeAssistant, fake_bus, unit):
    await setup(hass)
    unit.on_write = lambda number, value: None  # the unit ignores writes
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "select", "select_option", {"entity_id": f"select.{P}_summer_night_cooling", "option": "high"}, blocking=True
        )


async def test_unreachable_unit_marks_entities_unavailable(hass: HomeAssistant, fake_bus, unit):
    entry = await setup(hass)
    unit.slave = 99
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert state(hass, f"sensor.{P}_fresh_air_temperature") == "unavailable"
    unit.slave = 1
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert state(hass, f"sensor.{P}_fresh_air_temperature") == "5.5"


async def test_diagnostics_masks_serial(hass: HomeAssistant, fake_bus):
    from custom_components.swegon_casa.diagnostics import (
        async_get_config_entry_diagnostics,
    )

    entry = await setup(hass)
    diag = await async_get_config_entry_diagnostics(hass, entry)
    assert diag["entry"]["unique_id"] == "**REDACTED**"
    assert diag["unit"]["firmware"] == "3.1.12"
    assert diag["input"]["6201"] == 55


async def test_rotor_entities_only_on_r_series(hass: HomeAssistant, fake_bus, unit):
    from .simulator import ascii_registers

    unit.input.update(ascii_registers(6008, "CASA R5", 15))
    await setup(hass)
    assert state(hass, "binary_sensor.swegon_casa_w3_rotor_active") == "on"


async def _serial_flow(hass: HomeAssistant, port: str, baudrate: int = 38400):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"next_step_id": "serial"})
    return await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_SERIAL_PORT: port, CONF_BAUDRATE: baudrate, CONF_PARITY: "N", CONF_STOPBITS: 1, CONF_SLAVE: 0},
    )


async def test_flow_builtin_port_gets_a_clear_message(hass: HomeAssistant, fake_bus, unit):
    unit.slave = 99  # nothing on the built-in port
    result = await _serial_flow(hass, "/dev/ttyS0")
    assert result["errors"] == {"base": "no_answer_builtin_port"}


async def test_flow_port_that_cannot_open(hass: HomeAssistant, fake_bus, unit):
    unit.port_ok = False
    result = await _serial_flow(hass, "/dev/ttyUSB7")
    assert result["errors"] == {"base": "port_unavailable"}


async def test_flow_saves_the_detected_speed(hass: HomeAssistant, fake_bus, unit):
    unit.baudrate = 19200
    result = await _serial_flow(hass, PORT)
    assert result["step_id"] == "features"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {OPT_FEATURES: []})
    assert result["data"][CONF_BAUDRATE] == 19200
    await hass.async_block_till_done()
