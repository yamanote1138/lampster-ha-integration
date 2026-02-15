"""Test white mode control.

Update DEVICE_ADDRESS with your device address from test_discovery.py
"""

import asyncio
import logging

from lampster.client import LampsterClient
from lampster.models import WhiteColor

logging.basicConfig(level=logging.INFO)

# Device address from test_discovery.py
DEVICE_ADDRESS = "66C9BEF2-A12D-B137-E5CE-A2B780CE0B8A"


async def main():
    """Test white mode control."""
    if DEVICE_ADDRESS == "XX:XX:XX:XX:XX:XX":
        print("ERROR: Please update DEVICE_ADDRESS in this file")
        print("Run test_discovery.py first to find your device address")
        return

    print("=" * 60)
    print("The Lampster - White Mode Test")
    print("=" * 60)

    client = LampsterClient(DEVICE_ADDRESS)

    try:
        print("\nConnecting to device...")
        await client.connect()
        await client.power_on()
        print(f"✓ Connected and powered on\n")

        # Test different white temperatures and brightnesses
        whites = [
            ("Full Warm White", WhiteColor(100, 0)),
            ("Full Cold White", WhiteColor(0, 100)),
            ("Balanced Mix", WhiteColor(50, 50)),
            ("Warm Dominant", WhiteColor(75, 25)),
            ("Cold Dominant", WhiteColor(25, 75)),
            ("Dim Warm", WhiteColor(25, 0)),
            ("Dim Cold", WhiteColor(0, 25)),
            ("Dim Mixed", WhiteColor(25, 25)),
            ("Bright Warm", WhiteColor(100, 0)),
            ("Bright Cold", WhiteColor(0, 100)),
        ]

        for i, (name, color) in enumerate(whites, 1):
            print(f"{i}. Setting {name:18} {color}...")
            await client.set_white_color(color)
            print(f"   ✓ State: {client.state}")
            await asyncio.sleep(2)

        print("\n" + "=" * 60)
        print("✓ White mode test completed successfully!")
        print("=" * 60)
        print("\nTurning off lamp...")
        await client.power_off()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("- Verify the device address is correct")
        print("- Check that power control works (run test_power.py)")
        print("- Ensure lamp is in range and powered on")

    finally:
        if client.is_connected:
            await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
