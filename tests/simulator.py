"""A simulated Swegon CASA W3 behaving like the real Modbus slave.

Registers are keyed by their document number; the bus address is number - 1.
Unknown registers answer "illegal data address" (exception code 2), and a
wrong slave address gets no answer at all, as on a real RS-485 bus.
"""

from __future__ import annotations

from pymodbus.exceptions import ModbusIOException


def ascii_registers(first: int, text: str, length: int) -> dict[int, int]:
    return {first + i: (ord(text[i]) if i < len(text) else 0) for i in range(length)}


class Unit:
    def __init__(self, firmware=(3, 1, 12), slave: int = 1) -> None:
        self.slave = slave
        self.writes: list[tuple[int, int]] = []
        self.input: dict[int, int] = {
            6001: firmware[0], 6002: firmware[1], 6003: firmware[2], 6004: 1, 6005: 2,
            **ascii_registers(6008, "CASA W3", 15),
            **ascii_registers(6024, "SW1234567", 24),
            # alarms
            6101: 0, 6102: 0, 6103: 0, 6104: 0, 6105: 0, 6106: 0, 6107: 0, 6108: 0, 6134: 0,
            6123: 0, 6125: 0, 6127: 0, 6129: 0, 6130: 1, 6131: 0, 6132: 1, 6133: 1,
            6136: 1 << 8, 6137: 1 << 8, 6143: 0, 6145: 0, 6147: 0, 6149: 0,
            # measurements
            6201: 55, 6202: 180, 6203: 185, 6204: 215, 6205: 80, 6206: 210, 6207: 212, 6208: (-550) & 0xFFFF,
            6212: 655, 6213: 650, 6214: 45, 6215: 72, 6216: 80, 6217: 120,
            6218: 60, 6219: 58, 6220: 40, 6221: 42, 6234: 12,
            # status
            6301: 3, 6302: 2, 6303: 45, 6304: 47, 6305: 1450, 6306: 1500, 6307: 0, 6308: 0, 6309: 1,
            6310: (-5) & 0xFFFF, 6311: 0, 6312: 0, 6314: 0, 6315: 0, 6328: 0, 6332: 1, 6334: 0, 6335: 0,
            6338: 0, 6339: 0, 6342: 0, 6343: 2100, 6346: 0, 6347: 0, 6348: 0,
        }
        self.holding: dict[int, int] = {
            5001: 2, 5002: 0, 5004: 0, 5009: 1, 5010: 3, 5011: 3, 5018: 0, 5019: 0,
            5104: 15, 5105: 10, 5106: 10, 5114: 800, 5115: 500, 5117: 10, 5118: 20, 5119: 5, 5120: 10,
            5121: 1000, 5122: 1500, 5125: 30, 5141: 1, 5142: 12,
            5164: 2, 5165: 12, 5166: 15, 5167: 0, 5168: 15, 5169: 0, 5170: 24,
            5201: 1, 5202: 1, 5205: 1, 5207: 1, 5208: 1,
            5404: 0, 5405: 0, 5406: 0, 5407: 0, 5408: 0,
        }

    def on_write(self, number: int, value: int) -> None:
        self.writes.append((number, value))
        if number == 5002:  # fireplace: the status register follows
            self.input[6335] = value
        elif 5401 <= number <= 5408:  # confirmations are cleared once processed
            self.holding[number] = 0
            if number == 5404:
                self.input[6130] = 0
                self.input[6136] &= ~(1 << 8)
            return
        if number == 5001:
            self.input[6302] = value
        self.holding[number] = value


class Result:
    def __init__(self, registers=None, code: int | None = None) -> None:
        self.registers = registers or []
        self.exception_code = code

    def isError(self) -> bool:  # noqa: N802 - pymodbus API
        return self.exception_code is not None


class FakeClient:
    """Stands in for AsyncModbusSerialClient / AsyncModbusTcpClient."""

    def __init__(self, unit: Unit) -> None:
        self.unit = unit
        self.connected = False
        self.requests = 0

    async def connect(self) -> bool:
        self.connected = True
        return True

    def close(self) -> None:
        self.connected = False

    def _read(self, table: dict[int, int], address: int, count: int, device_id: int) -> Result:
        self.requests += 1
        if device_id != self.unit.slave:
            raise ModbusIOException("no response")
        values = []
        for number in range(address + 1, address + 1 + count):
            if number not in table:
                return Result(code=2)
            values.append(table[number])
        return Result(values)

    async def read_input_registers(self, address: int, *, count: int = 1, device_id: int = 1, **_) -> Result:
        return self._read(self.unit.input, address, count, device_id)

    async def read_holding_registers(self, address: int, *, count: int = 1, device_id: int = 1, **_) -> Result:
        return self._read(self.unit.holding, address, count, device_id)

    async def write_register(self, address: int, value: int, *, device_id: int = 1, **_) -> Result:
        if device_id != self.unit.slave:
            raise ModbusIOException("no response")
        number = address + 1
        if number not in self.unit.holding:
            return Result(code=2)
        self.unit.on_write(number, value)
        return Result([value])
