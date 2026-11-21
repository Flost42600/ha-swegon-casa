"""Modbus layer and register conversions."""

from __future__ import annotations

import pytest

from custom_components.swegon_casa.modbus import (
    SwegonModbus,
    SwegonModbusError,
    SwegonPortError,
    SwegonWriteError,
    Transport,
    detect,
    plan_blocks,
)
from custom_components.swegon_casa.registers import REGISTERS, by_key, from_raw, to_raw

SERIAL = Transport(kind="serial", port="/dev/ttyUSB0")


def test_plan_blocks_contiguous_only():
    assert plan_blocks([6203, 6201, 6202, 6205]) == [(6201, 3), (6205, 1)]
    assert plan_blocks(list(range(6001, 6050))) == [(6001, 32), (6033, 17)]


def test_signed_and_scaled_conversions():
    temp = by_key()["fresh_air_temperature"]
    assert from_raw(temp, 55) == 5.5
    assert from_raw(temp, (-123) & 0xFFFF) == -12.3
    assert from_raw(temp, (-550) & 0xFFFF) is None  # no sensor
    smart = by_key()["smart_control"]
    assert to_raw(smart, -10) == 65526
    assert from_raw(smart, 65526) == -10
    with pytest.raises(ValueError):
        to_raw(by_key()["operating_mode"], 70000)


def test_every_register_is_consistent():
    for reg in REGISTERS:
        assert reg.table in ("input", "holding")
        if reg.platform in ("number", "select", "switch", "button"):
            assert reg.table == "holding", reg.key
        if reg.platform == "number":
            assert reg.minimum is not None and reg.maximum is not None, reg.key
        if reg.options:
            assert set(reg.options.values()) == set(reg.options_fr) == set(reg.options_en), reg.key


async def test_detect_finds_slave_and_offset(fake_bus, unit):
    unit.slave = 16
    assert await detect(SERIAL) == (16, -1, (3, 1, 12), 38400)


async def test_detect_fails_cleanly_when_nothing_answers(fake_bus, unit):
    unit.slave = 99
    with pytest.raises(SwegonModbusError):
        await detect(SERIAL)


async def test_read_uses_the_offset_and_blocks(fake_bus, unit):
    client = SwegonModbus(SERIAL, 1, -1)
    values = await client.read("input", [6201, 6202, 6203, 6204, 6205])
    assert values == {6201: 55, 6202: 180, 6203: 185, 6204: 215, 6205: 80}
    assert fake_bus[-1].requests == 1  # one block


async def test_missing_register_is_remembered(fake_bus, unit):
    client = SwegonModbus(SERIAL, 1, -1)
    values = await client.read("input", [6209, 6210, 6203])  # no water radiator / preheater
    assert values == {6209: None, 6210: None, 6203: 185}
    before = fake_bus[-1].requests
    await client.read("input", [6209, 6210, 6203])
    assert fake_bus[-1].requests - before == 1  # only 6203 is asked again


async def test_text_registers(fake_bus, unit):
    client = SwegonModbus(SERIAL, 1, -1)
    assert await client.read_text(6008, 15) == "CASA W3"


async def test_write_is_read_back(fake_bus, unit):
    client = SwegonModbus(SERIAL, 1, -1)
    await client.write(5001, 3)
    assert unit.holding[5001] == 3


async def test_write_not_confirmed_raises(fake_bus, unit):
    client = SwegonModbus(SERIAL, 1, -1)
    original = unit.on_write
    unit.on_write = lambda number, value: unit.writes.append((number, value))  # ignores the value
    with pytest.raises(SwegonWriteError):
        await client.write(5001, 3)
    unit.on_write = original


async def test_write_refused_raises(fake_bus, unit):
    client = SwegonModbus(SERIAL, 1, -1)
    with pytest.raises(SwegonWriteError):
        await client.write(5999, 1)


async def test_detect_finds_another_speed(fake_bus, unit):
    unit.baudrate = 9600
    assert await detect(SERIAL) == (1, -1, (3, 1, 12), 9600)


async def test_detect_skips_offsets_of_a_silent_slave(fake_bus, unit):
    unit.slave = 99
    with pytest.raises(SwegonModbusError):
        await detect(SERIAL)
    # 5 speeds x 2 slaves, one request each: the second offset is never tried
    assert sum(c.requests for c in fake_bus) == 10


async def test_detect_stops_when_the_port_cannot_be_opened(fake_bus, unit):
    unit.port_ok = False
    with pytest.raises(SwegonPortError):
        await detect(SERIAL)
    assert len(fake_bus) == 1
