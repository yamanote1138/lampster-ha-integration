"""Test RGB color control.

Update DEVICE_ADDRESS with your device address from test_discovery.py
"""

import asyncio
import logging

from lampster.client import LampsterClient
from lampster.models import RGBColor

logging.basicConfig(level=logging.INFO)

# TODO: Update with your device address from test_discovery.py
DEVICE_ADDRESS = "XX:XX:XX:XX:XX:XX"


async def main():
    """Test RGB color control."""
    if DEVICE_ADDRESS == "XX:XX:XX:XX:XX:XX":
        print("ERROR: Please update DEVICE_ADDRESS in this file")
        print("Run test_discovery.py first to find your device address")
        return

    print("=" * 60)
    print("The Lampster - RGB Color Test")
    print("=" * 60)

    client = LampsterClient(DEVICE_ADDRESS)

    try:
        print("\nConnecting to device...")
        await client.connect()
        await client.power_on()
        print(f"✓ Connected and powered on\n")

        # Test different colors
        colors = [
            ("Red", RGBColor(100, 0, 0)),
            ("Green", RGBColor(0, 100, 0)),
            ("Blue", RGBColor(0, 0, 100)),
            ("Yellow", RGBColor(100, 100, 0)),
            ("Cyan", RGBColor(0, 100, 100)),
            ("Magenta", RGBColor(100, 0, 100)),
            ("White", RGBColor(100, 100, 100)),
            ("Dim White", RGBColor(30, 30, 30)),
            ("Orange", RGBColor(100, 50, 0)),
            ("Purple", RGBColor(50, 0, 100)),
        ]

        for i, (name, color) in enumerate(colors, 1):
            print(f"{i}. Setting {name:12} {color}...")
            await client.set_rgb_color(color)
            print(f"   ✓ State: {client.state}")
            await asyncio.sleep(2)

        print("\n" + "=" * 60)
        print("✓ RGB color test completed successfully!")
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
