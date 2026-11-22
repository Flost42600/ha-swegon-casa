"""Constants for the Swegon CASA integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "swegon_casa"
MANUFACTURER: Final = "Swegon"
VERSION: Final = "0.2.1"  # keep in sync with manifest.json

CONF_KIND: Final = "kind"  # "serial" or "tcp"
CONF_SERIAL_PORT: Final = "serial_port"
CONF_BAUDRATE: Final = "baudrate"
CONF_PARITY: Final = "parity"
CONF_STOPBITS: Final = "stopbits"
CONF_TCP_PORT: Final = "tcp_port"
CONF_SLAVE: Final = "slave"
CONF_OFFSET: Final = "offset"

OPT_FEATURES: Final = "features"
OPT_SCAN_INTERVAL: Final = "scan_interval"
OPT_SETTINGS_INTERVAL: Final = "settings_interval"

DEFAULT_BAUDRATE: Final = 38400
DEFAULT_PARITY: Final = "N"
DEFAULT_STOPBITS: Final = 1
DEFAULT_TCP_PORT: Final = 502
DEFAULT_SCAN_INTERVAL: Final = 15  # seconds, measurements and status
DEFAULT_SETTINGS_INTERVAL: Final = 60  # seconds, holding registers

CARD_URL: Final = f"/{DOMAIN}/swegon-casa-card.js"
