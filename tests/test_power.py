"""Test power on/off functionality.

Update DEVICE_ADDRESS with your device address from test_discovery.py
"""

import asyncio
import logging

from lampster.client import LampsterClient

logging.basicConfig(level=logging.INFO)

# TODO: Update with your device address from test_discovery.py
DEVICE_ADDRESS = "XX:XX:XX:XX:XX:XX"


async def main():
    """Test power on/off."""
    if DEVICE_ADDRESS == "XX:XX:XX:XX:XX:XX":
        print("ERROR: Please update DEVICE_ADDRESS in this file")
        print("Run test_discovery.py first to find your device address")
        return

    print("=" * 60)
    print("The Lampster - Power Control Test")
    print("=" * 60)

    client = LampsterClient(DEVICE_ADDRESS)

    try:
        print("\n1. Connecting to device...")
        await client.connect()
        print(f"   ✓ Connected: {client.is_connected}")

        print("\n2. Turning lamp ON...")
        await client.power_on()
        print(f"   ✓ State: {client.state}")
        await asyncio.sleep(3)

        print("\n3. Turning lamp OFF...")
        await client.power_off()
        print(f"   ✓ State: {client.state}")
        await asyncio.sleep(2)

        print("\n4. Turning lamp ON again...")
        await client.power_on()
        print(f"   ✓ State: {client.state}")
        await asyncio.sleep(2)

        print("\n5. Turning lamp OFF...")
        await client.power_off()
        print(f"   ✓ State: {client.state}")

        print("\n" + "=" * 60)
        print("✓ Power control test completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("- Verify the device address is correct")
        print("- Make sure the lamp is powered on and in range")
        print("- Try power cycling the lamp")

    finally:
        if client.is_connected:
            print("\nDisconnecting...")
            await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
