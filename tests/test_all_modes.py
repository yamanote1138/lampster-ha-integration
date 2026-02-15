"""Comprehensive test of all Lampster modes and functionality.

Update DEVICE_ADDRESS with your device address from test_discovery.py
"""

import asyncio
import logging

from lampster.client import LampsterClient
from lampster.models import RGBColor, WhiteColor

logging.basicConfig(level=logging.INFO)

# TODO: Update with your device address from test_discovery.py
DEVICE_ADDRESS = "XX:XX:XX:XX:XX:XX"


async def main():
    """Comprehensive test of all modes."""
    if DEVICE_ADDRESS == "XX:XX:XX:XX:XX:XX":
        print("ERROR: Please update DEVICE_ADDRESS in this file")
        print("Run test_discovery.py first to find your device address")
        return

    print("=" * 60)
    print("The Lampster - Comprehensive Mode Test")
    print("=" * 60)
    print("\nThis test will cycle through all major functionality")
    print("and verify mode switching works correctly.\n")

    client = LampsterClient(DEVICE_ADDRESS)

    try:
        print("Connecting to device...")
        await client.connect()
        print(f"✓ Connected: {client.is_connected}\n")

        # Test sequence
        tests = [
            ("Power ON", lambda: client.power_on()),
            ("RGB Mode - Red", lambda: client.set_rgb_color(RGBColor(100, 0, 0))),
            ("RGB Mode - Green", lambda: client.set_rgb_color(RGBColor(0, 100, 0))),
            ("RGB Mode - Blue", lambda: client.set_rgb_color(RGBColor(0, 0, 100))),
            ("White Mode - Warm", lambda: client.set_white_color(WhiteColor(100, 0))),
            ("White Mode - Cold", lambda: client.set_white_color(WhiteColor(0, 100))),
            ("White Mode - Mixed", lambda: client.set_white_color(WhiteColor(50, 50))),
            ("RGB Mode - Purple", lambda: client.set_rgb_color(RGBColor(100, 0, 100))),
            ("RGB Mode - Yellow", lambda: client.set_rgb_color(RGBColor(100, 100, 0))),
            ("RGB Mode - Cyan", lambda: client.set_rgb_color(RGBColor(0, 100, 100))),
            ("RGB Mode - White", lambda: client.set_rgb_color(RGBColor(100, 100, 100))),
            ("Power OFF", lambda: client.power_off()),
        ]

        for i, (description, test_func) in enumerate(tests, 1):
            print(f"[{i}/{len(tests)}] {description}...")
            await test_func()
            print(f"      State: {client.state}")
            await asyncio.sleep(2)
            print()

        print("=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        print("\nSummary:")
        print("- Power control: ✓")
        print("- RGB color mode: ✓")
        print("- White mode: ✓")
        print("- Mode switching: ✓")
        print("\nYour Lampster is fully functional and ready for")
        print("Home Assistant integration development!")

    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        print("\nTest failed. Please check:")
        print("- Device address is correct")
        print("- Lamp is powered on and in range")
        print("- Individual tests (power, rgb, white) work")
        print("- Characteristic UUIDs match your device")

    finally:
        if client.is_connected:
            print("\nDisconnecting...")
            await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
