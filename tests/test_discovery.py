"""Test device discovery and characteristic enumeration.

Run this first to find your Lampster device address and validate UUIDs.
"""

import asyncio
import logging

from bleak import BleakClient
from lampster.client import LampsterClient

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


async def discover_characteristics(address: str):
    """Discover all services and characteristics for a device.

    This helper validates the UUIDs from Noki's documentation against your actual device.
    """
    print(f"\nEnumerating characteristics for {address}...")
    print("=" * 60)

    try:
        async with BleakClient(address) as client:
            print(f"Connected: {client.is_connected}\n")

            for service in client.services:
                print(f"Service: {service.uuid}")
                print(f"  Description: {service.description}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid}")
                    print(f"    Handle: 0x{char.handle:04x}")
                    print(f"    Properties: {char.properties}")
                    print(f"    Description: {char.description}")
                print()
    except Exception as e:
        print(f"Error enumerating characteristics: {e}")


async def main():
    """Discover Lampster devices and optionally enumerate characteristics."""
    print("=" * 60)
    print("The Lampster - Device Discovery")
    print("=" * 60)
    print("\nSearching for Lampster devices...")

    try:
        devices = await LampsterClient.discover(timeout=10.0)

        print(f"\n✓ Found {len(devices)} device(s):\n")
        for i, device in enumerate(devices, 1):
            print(f"{i}. Name: {device.name}")
            print(f"   Address: {device.address}")
            print(f"   RSSI: {device.rssi} dBm")
            print()

        # If devices found, offer to enumerate characteristics
        if devices:
            print("\n" + "=" * 60)
            print("Next Steps:")
            print("=" * 60)
            print("\n1. Copy the device address from above")
            print("2. Update the DEVICE_ADDRESS in other test files")
            print("3. Run the other test scripts to validate functionality\n")

            # Optionally enumerate characteristics for first device
            print("To enumerate characteristics for the first device,")
            print("uncomment the following line in this script:\n")
            print(f"# await discover_characteristics('{devices[0].address}')")
            print()

            # Uncomment this to see all characteristics:
            # await discover_characteristics(devices[0].address)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("- Make sure your Lampster is powered on")
        print("- Keep the lamp close to your computer (within 2m)")
        print("- Check that Bluetooth is enabled on your Mac")


if __name__ == "__main__":
    asyncio.run(main())
