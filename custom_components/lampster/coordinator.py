"""Coordinator for The Lampster integration."""
from __future__ import annotations

import logging
from typing import Any

from bleak_retry_connector import establish_connection

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.active_update_coordinator import (
    ActiveBluetoothDataUpdateCoordinator,
)
from homeassistant.core import HomeAssistant

from .lampster.client import LampsterClient
from .lampster.exceptions import CommandError, ConnectionError as LampsterConnectionError
from .lampster.models import LampState

_LOGGER = logging.getLogger(__name__)

# Minimum 10 seconds per HA docs: "BlueZ must resolve services when connecting"
CONNECT_TIMEOUT = 10


class LampsterCoordinator(ActiveBluetoothDataUpdateCoordinator[LampState]):
    """Coordinator to manage Lampster BLE connection and state updates."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            address=address,
            needs_poll_method=self._needs_poll,
            poll_method=self._async_poll,
            mode=bluetooth.BluetoothScanningMode.ACTIVE,
            connectable=True,
        )
        self._client: LampsterClient | None = None
        self._address = address

    def _needs_poll(
        self,
        service_info: bluetooth.BluetoothServiceInfoBleak,
        seconds_since_last_poll: float | None,
    ) -> bool:
        """Determine if we need to poll the device.

        Poll when:
        - First connection (no previous poll)
        - More than 30 seconds since last poll (check for manual changes)
        """
        if seconds_since_last_poll is None:
            return True

        # Poll every 30 seconds to detect manual button presses
        return seconds_since_last_poll > 30

    async def _async_poll(
        self, service_info: bluetooth.BluetoothServiceInfoBleak
    ) -> LampState:
        """Poll the device for current state.

        Uses bleak-retry-connector for robust connection handling.
        """
        # Get BLE device from HA's bluetooth integration
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, service_info.address, connectable=True
        )

        if not ble_device:
            raise LampsterConnectionError("Device not found or not connectable")

        # Establish connection with retry logic (10 second timeout)
        try:
            from bleak import BleakClient

            async with establish_connection(
                BleakClient,
                ble_device,
                service_info.name or self._address,
                disconnected_callback=self._handle_disconnect,
                max_attempts=3,
                timeout=CONNECT_TIMEOUT,
            ) as bleak_client:
                # Wrap in our client
                client = LampsterClient(self._address)
                client._client = bleak_client
                self._client = client

                # Read actual state from device
                state = await client.read_state()
                _LOGGER.debug("Polled device state: %s", state)
                return state

        except Exception as err:
            _LOGGER.debug("Failed to poll device: %s", err)
            raise

    def _handle_disconnect(self, client: LampsterClient) -> None:
        """Handle device disconnection."""
        _LOGGER.debug("Device disconnected")
        self._client = None

    async def async_command(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Execute a command on the device.

        Establishes connection if needed, executes command, then disconnects.
        """
        # Get current service info
        service_info = bluetooth.async_last_service_info(
            self.hass, self._address, connectable=True
        )

        if not service_info:
            raise LampsterConnectionError("Device not available")

        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self._address, connectable=True
        )

        if not ble_device:
            raise LampsterConnectionError("Device not found or not connectable")

        # Connect and execute command
        try:
            from bleak import BleakClient

            async with establish_connection(
                BleakClient,
                ble_device,
                service_info.name or self._address,
                max_attempts=3,
                timeout=CONNECT_TIMEOUT,
            ) as bleak_client:
                # Wrap in our client
                client = LampsterClient(self._address)
                client._client = bleak_client

                # Get the method from the client
                method = getattr(client, method_name)
                await method(*args, **kwargs)

                # Read state after command to update coordinator
                state = await client.read_state()
                self.async_set_updated_data(state)

        except Exception as err:
            _LOGGER.error("Failed to execute command %s: %s", method_name, err)
            raise
