"""Modbus access to a Swegon CASA unit (RTU over serial, or TCP through a gateway).

* Register numbers are those of the Swegon document (1-based); the address sent
  is number + offset, the offset (normally -1) being detected at setup.
* Reads are grouped into blocks. A block the unit refuses ("illegal address")
  is retried register by register, and registers that do not exist are
  remembered and skipped afterwards.
* One transaction at a time: the RS-485 bus is half duplex.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from dataclasses import dataclass, replace
from typing import Any, Literal

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .registers import FIRMWARE

_LOGGER = logging.getLogger(__name__)

MAX_BLOCK = 32  # registers per read
MAX_GAP = 0  # read only wanted registers: a missing one in a gap would fail the block
ILLEGAL_ADDRESS = 2


class SwegonModbusError(Exception):
    """The unit did not answer (cable, port, settings)."""


class SwegonPortError(SwegonModbusError):
    """The serial port or gateway cannot be opened (wrong path, busy, unplugged)."""


class SwegonWriteError(Exception):
    """The unit refused or did not confirm a write."""


@dataclass
class Transport:
    kind: Literal["serial", "tcp"]
    port: str | None = None  # serial device
    baudrate: int = 38400
    parity: str = "N"
    stopbits: int = 1
    bytesize: int = 8
    host: str | None = None
    tcp_port: int = 502
    timeout: float = 2.0
    retries: int = 1


def plan_blocks(numbers: list[int]) -> list[tuple[int, int]]:
    """Contiguous (first, count) blocks covering the numbers, gaps <= MAX_GAP, length <= MAX_BLOCK."""
    blocks: list[tuple[int, int]] = []
    for number in sorted(set(numbers)):
        if blocks:
            first, count = blocks[-1]
            last = first + count - 1
            if number - last - 1 <= MAX_GAP and number - first + 1 <= MAX_BLOCK:
                blocks[-1] = (first, number - first + 1)
                continue
        blocks.append((number, 1))
    return blocks


class SwegonModbus:
    """Client for one unit."""

    def __init__(self, transport: Transport, slave: int = 1, offset: int = -1) -> None:
        self.transport = transport
        self.slave = slave
        self.offset = offset
        self._client: Any = None
        self._lock = asyncio.Lock()
        self._missing: set[tuple[str, int]] = set()  # registers the unit does not have
        self._split: set[tuple[str, int, int]] = set()  # blocks the unit refused: read one by one
        self._id_kw = "device_id"

    # ------------------------------------------------------------ connection

    def _make_client(self) -> Any:
        t = self.transport
        if t.kind == "serial":
            return AsyncModbusSerialClient(
                port=t.port,
                baudrate=t.baudrate,
                parity=t.parity,
                stopbits=t.stopbits,
                bytesize=t.bytesize,
                timeout=t.timeout,
                retries=t.retries,
            )
        return AsyncModbusTcpClient(host=t.host, port=t.tcp_port, timeout=t.timeout, retries=t.retries)

    async def connect(self) -> None:
        if self._client is not None and self._client.connected:
            return
        self._client = self._make_client()
        params = inspect.signature(self._client.read_input_registers).parameters
        self._id_kw = "device_id" if "device_id" in params else "slave"
        try:
            opened = await self._client.connect()
        except OSError as err:
            opened = False
            _LOGGER.debug("Opening %s failed: %s", self._where(), err)
        if not opened:
            self._client = None
            raise SwegonPortError(f"Cannot open {self._where()}")

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def _where(self) -> str:
        t = self.transport
        return t.port if t.kind == "serial" else f"{t.host}:{t.tcp_port}"

    # ------------------------------------------------------------------ reads

    async def _read_block(self, table: str, first: int, count: int) -> list[int] | int:
        """Raw values, or the Modbus exception code when the unit refuses."""
        await self.connect()
        func = (
            self._client.read_input_registers
            if table == "input"
            else self._client.read_holding_registers
        )
        try:
            result = await func(first + self.offset, count=count, **{self._id_kw: self.slave})
        except ModbusException as err:
            await self.close()
            raise SwegonModbusError(f"No answer from {self._where()}: {err}") from err
        if result.isError():
            return getattr(result, "exception_code", 0) or 0
        registers = list(result.registers)
        if len(registers) < count:
            raise SwegonModbusError(f"Short answer reading {table} {first}")
        return registers[:count]

    async def read(self, table: str, numbers: list[int]) -> dict[int, int | None]:
        """{number: raw value or None}. Missing registers read as None."""
        wanted = [n for n in numbers if (table, n) not in self._missing]
        values: dict[int, int | None] = {n: None for n in numbers}
        async with self._lock:
            for first, count in plan_blocks(wanted):
                if (table, first, count) not in self._split:
                    block = await self._read_block(table, first, count)
                    if isinstance(block, list):
                        for i, raw in enumerate(block):
                            if first + i in values:
                                values[first + i] = raw
                        continue
                    if count > 1:
                        self._split.add((table, first, count))
                # Refused: read the wanted registers of this block one by one.
                for number in [n for n in wanted if first <= n < first + count]:
                    single = await self._read_block(table, number, 1)
                    if isinstance(single, list):
                        values[number] = single[0]
                    elif single == ILLEGAL_ADDRESS:
                        _LOGGER.debug("Register %s %s does not exist on this unit", table, number)
                        self._missing.add((table, number))
                    else:
                        _LOGGER.debug("Register %s %s refused (code %s)", table, number, single)
        return values

    async def read_text(self, first: int, count: int) -> str | None:
        """ASCII text stored one character (or two) per input register."""
        values = await self.read("input", list(range(first, first + count)))
        chars: list[str] = []
        for number in range(first, first + count):
            raw = values.get(number)
            if not raw:
                continue
            pair = [raw] if raw < 256 else [raw >> 8, raw & 0xFF]
            chars.extend(chr(c) for c in pair if 32 <= c < 127)
        text = "".join(chars).strip()
        return text or None

    # ----------------------------------------------------------------- writes

    async def write(self, number: int, raw: int, verify: bool = True) -> None:
        """Write one holding register (function 6) and read it back."""
        async with self._lock:
            await self.connect()
            try:
                result = await self._client.write_register(
                    number + self.offset, raw, **{self._id_kw: self.slave}
                )
            except ModbusException as err:
                await self.close()
                raise SwegonModbusError(f"No answer from {self._where()}: {err}") from err
            if result.isError():
                raise SwegonWriteError(
                    f"The unit refused value {raw} for register {number} "
                    f"(code {getattr(result, 'exception_code', '?')})"
                )
        if verify:
            back = (await self.read("holding", [number]))[number]
            if back != raw:
                raise SwegonWriteError(f"Register {number} reads {back} after writing {raw}")


BAUDRATES = (38400, 19200, 9600, 57600, 115200)
PROBE_TIMEOUT = 0.8  # seconds per request while searching: an idle bus answers nothing


async def detect(
    transport: Transport,
    slaves: tuple[int, ...] = (1, 16),
    offsets: tuple[int, ...] = (-1, 0),
    baudrates: tuple[int, ...] | None = None,
) -> tuple[int, int, tuple[int, int, int], int]:
    """Find (slave, offset, firmware, baudrate) by reading the firmware version registers.

    Searching is quick: short timeout, no retry, and a slave that stays silent
    is not asked again with another offset. On a serial link the chosen speed
    is tried first, then the other usual speeds. A port that cannot be opened
    stops the search at once (SwegonPortError).
    """
    if baudrates is None:
        baudrates = (transport.baudrate,)
        if transport.kind == "serial":
            baudrates += tuple(b for b in BAUDRATES if b != transport.baudrate)
    for baudrate in baudrates:
        probe = replace(transport, baudrate=baudrate, timeout=min(transport.timeout, PROBE_TIMEOUT), retries=0)
        for slave in slaves:
            for offset in offsets:
                client = SwegonModbus(probe, slave, offset)
                try:
                    values = await client.read("input", list(FIRMWARE))
                except SwegonPortError:
                    raise
                except SwegonModbusError:
                    break  # silent: no use trying another offset for this slave
                finally:
                    await client.close()
                major, minor, build = (values.get(n) for n in FIRMWARE)
                if major is not None and 1 <= major <= 9 and minor is not None and minor <= 99 and (build or 0) <= 999:
                    _LOGGER.info("Swegon unit found at %s baud, slave %s, offset %s", baudrate, slave, offset)
                    return slave, offset, (major, minor, build or 0), baudrate
    raise SwegonModbusError(f"No Swegon unit answers on {SwegonModbus(transport)._where()}")
