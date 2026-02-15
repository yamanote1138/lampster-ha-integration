"""BLE client for controlling The Lampster.

Protocol based on: https://github.com/Noki/the-lampster
"""

import asyncio
import logging
from typing import Optional

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

from .constants import (
    CHAR_MODE,
    CHAR_RGB,
    CHAR_WHITE,
    DEVICE_NAME_PREFIX,
    MODE_OFF,
    MODE_POWER_OFF,
    MODE_POWER_ON,
    MODE_RGB,
    MODE_WHITE,
)
from .exceptions import CommandError, ConnectionError, DiscoveryError
from .models import LampState, RGBColor, WhiteColor

_LOGGER = logging.getLogger(__name__)


class LampsterClient:
    """Client for controlling The Lampster via Bluetooth LE."""

    def __init__(self, address: str):
        """Initialize client with device address.

        Args:
            address: Bluetooth MAC address of the device (e.g., "XX:XX:XX:XX:XX:XX")
        """
        self.address = address
        self._client: Optional[BleakClient] = None
        self._state = LampState(is_on=False, mode="off")

    @staticmethod
    async def discover(timeout: float = 10.0) -> list[BLEDevice]:
        """Discover Lampster devices nearby.

        Args:
            timeout: Scan timeout in seconds

        Returns:
            List of discovered BLE devices matching Lampster pattern

        Raises:
            DiscoveryError: If no devices are found
        """
        _LOGGER.info("Scanning for Lampster devices...")
        devices = await BleakScanner.discover(timeout=timeout)

        # Filter for devices that match Lampster pattern
        lampster_devices = [
            d for d in devices if d.name and DEVICE_NAME_PREFIX in d.name
        ]

        if not lampster_devices:
            raise DiscoveryError("No Lampster devices found")

        _LOGGER.info(f"Found {len(lampster_devices)} Lampster device(s)")
        return lampster_devices

    async def connect(self, timeout: float = 10.0) -> bool:
        """Connect to the Lampster device.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._client = BleakClient(self.address, timeout=timeout)
            await self._client.connect()
            _LOGGER.info(f"Connected to Lampster at {self.address}")
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}") from e

    async def disconnect(self):
        """Disconnect from the device."""
        if self._client and self._client.is_connected:
            await self._client.disconnect()
            _LOGGER.info("Disconnected from Lampster")

    async def _write_mode(self, mode: int):
        """Write to mode characteristic.

        Args:
            mode: Mode command byte

        Raises:
            ConnectionError: If not connected
            CommandError: If write fails
        """
        if not self._client or not self._client.is_connected:
            raise ConnectionError("Not connected to device")

        try:
            # Try write-without-response for mode switching
            await self._client.write_gatt_char(CHAR_MODE, bytes([mode]), response=False)
            _LOGGER.debug(f"Wrote mode: 0x{mode:02x}")
        except Exception as e:
            raise CommandError(f"Failed to write mode: {e}") from e

    async def power_on(self):
        """Turn the lamp on.

        Raises:
            ConnectionError: If not connected
            CommandError: If command fails
        """
        await self._write_mode(MODE_POWER_ON)
        self._state.is_on = True
        _LOGGER.info("Lamp powered on")

    async def power_off(self):
        """Turn the lamp off.

        Raises:
            ConnectionError: If not connected
            CommandError: If command fails
        """
        await self._write_mode(MODE_POWER_OFF)
        self._state.is_on = False
        self._state.mode = "off"
        _LOGGER.info("Lamp powered off")

    async def set_rgb_mode(self):
        """Switch to RGB mode.

        Raises:
            ConnectionError: If not connected
            CommandError: If command fails
        """
        await self._write_mode(MODE_RGB)
        self._state.mode = "rgb"
        _LOGGER.debug("Switched to RGB mode")

    async def set_white_mode(self):
        """Switch to white mode.

        Raises:
            ConnectionError: If not connected
            CommandError: If command fails
        """
        await self._write_mode(MODE_WHITE)
        self._state.mode = "white"
        _LOGGER.debug("Switched to white mode")

    async def set_rgb_color(self, color: RGBColor):
        """Set RGB color (automatically switches to RGB mode).

        Args:
            color: RGBColor object with values 0-100

        Raises:
            ConnectionError: If not connected
            CommandError: If command fails
        """
        if not self._client or not self._client.is_connected:
            raise ConnectionError("Not connected to device")

        try:
            # Switch to RGB mode first
            await self.set_rgb_mode()

            # Write color (without response, as per Noki's char-write-cmd)
            await self._client.write_gatt_char(CHAR_RGB, color.to_bytes(), response=False)
            _LOGGER.info(f"Set RGB color: {color}")

            self._state.rgb_color = color
        except Exception as e:
            raise CommandError(f"Failed to set RGB color: {e}") from e

    async def set_white_color(self, color: WhiteColor):
        """Set white color (automatically switches to white mode).

        Args:
            color: WhiteColor object with warm/cold values 0-100

        Raises:
            ConnectionError: If not connected
            CommandError: If command fails
        """
        if not self._client or not self._client.is_connected:
            raise ConnectionError("Not connected to device")

        try:
            # Switch to white mode first
            await self.set_white_mode()

            # Write color (without response, as per Noki's char-write-cmd)
            await self._client.write_gatt_char(CHAR_WHITE, color.to_bytes(), response=False)
            _LOGGER.info(f"Set white color: {color}")

            self._state.white_color = color
        except Exception as e:
            raise CommandError(f"Failed to set white color: {e}") from e

    @property
    def state(self) -> LampState:
        """Get current lamp state.

        Note: State is tracked locally as the device doesn't support reading.
        """
        return self._state

    @property
    def is_connected(self) -> bool:
        """Check if connected to device."""
        return self._client is not None and self._client.is_connected
