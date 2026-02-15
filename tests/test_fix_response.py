"""Test the response=True fix for mode characteristic.

Based on Noki's docs:
- Mode (0x0021): char-write-req (WITH response)
- RGB (0x002a): char-write-cmd (WITHOUT response)

This was our bug - we used response=False for both!
"""

import asyncio
import logging

from lampster.client import LampsterClient
from lampster.models import RGBColor

logging.basicConfig(level=logging.INFO)

DEVICE_ADDRESS = "66C9BEF2-A12D-B137-E5CE-A2B780CE0B8A"


async def main():
    """Test RGB control with correct response parameter."""
    print("=" * 70)
    print("Testing Fix: response=True for Mode Characteristic")
    print("=" * 70)
    print("\nBased on Noki's protocol:")
    print("  MODE (0x0021): char-write-req = response=True")
    print("  RGB (0x002a): char-write-cmd = response=False")
    print()

    input("Make sure lamp is plugged in. Press ENTER to start...")

    client = LampsterClient(DEVICE_ADDRESS)

    try:
        print("\nConnecting...")
        await client.connect()
        print("✓ Connected\n")

        # Test sequence with proper response parameters
        colors = [
            ("RED", RGBColor(100, 0, 0)),
            ("GREEN", RGBColor(0, 100, 0)),
            ("BLUE", RGBColor(0, 0, 100)),
            ("PURPLE", RGBColor(100, 0, 100)),
            ("YELLOW", RGBColor(100, 100, 0)),
            ("CYAN", RGBColor(0, 100, 100)),
            ("WHITE", RGBColor(100, 100, 100)),
        ]

        print("Testing RGB colors with CORRECT protocol:")
        print("(Mode writes will now wait for device acknowledgment)\n")

        for i, (name, color) in enumerate(colors, 1):
            print(f"[{i}/{len(colors)}] Setting {name:8} {color}...")
            await client.set_rgb_color(color)
            await asyncio.sleep(2)

        print("\n" + "=" * 70)
        print("Color test complete!")
        print("=" * 70)

        print("\nDid you see the colors change?")
        print("  1) Yes - all colors worked!")
        print("  2) No - lamp didn't respond")
        print("  3) Partial - some worked, some didn't")

        choice = input("\nYour answer (1/2/3): ").strip()

        if choice == "1":
            print("\n🎉 SUCCESS! The response=True fix worked!")
            print("The mode characteristic needed acknowledgment.")
        elif choice == "2":
            print("\n😞 Still not working. More investigation needed.")
        else:
            print("\n🤔 Partial success - may need more debugging.")

        print("\nTurning off...")
        await client.power_off()
        await asyncio.sleep(1)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if client.is_connected:
            await client.disconnect()
            print("\nDisconnected")


if __name__ == "__main__":
    asyncio.run(main())
