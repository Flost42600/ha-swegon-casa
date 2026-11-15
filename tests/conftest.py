"""Shared fixtures: a simulated unit plugged in place of the pymodbus client."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from .simulator import FakeClient, Unit

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture
def unit() -> Unit:
    return Unit()


@pytest.fixture
def fake_bus(unit: Unit):
    """Every SwegonModbus talks to the simulated unit."""
    clients: list[FakeClient] = []

    def make(self):
        client = FakeClient(unit)
        clients.append(client)
        return client

    with patch("custom_components.swegon_casa.modbus.SwegonModbus._make_client", make):
        yield clients
