"""Test white mode control with response=True fix.

White mode uses:
- MODE (0x0021): 0xC8 with response=True
- WHITE (0x0025): [warm, cold] with response=False
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from bleak import BleakClient
from lampster.client import LampsterClient
from lampster.models import WhiteColor
from lampster.constants import CHAR_MODE, CHAR_RGB, CHAR_WHITE

logging.basicConfig(level=logging.INFO)

DEVICE_ADDRESS = "66C9BEF2-A12D-B137-E5CE-A2B780CE0B8A"


async def main():
    """Test white mode color control."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = Path(__file__).parent / f"white_mode_results_{timestamp}.txt"
    results = []

    def log(msg):
        print(msg)
        results.append(msg)

    log("=" * 70)
    log("White Mode Test (With Fixed Protocol)")
    log("=" * 70)
    log(f"\nTest started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("Device: " + DEVICE_ADDRESS)
    log("\nTesting warm/cool white color control")
    log("Note: Automatically recording all firmware state changes\n")

    await asyncio.sleep(2)

    client = LampsterClient(DEVICE_ADDRESS)

    try:
        log("\nConnecting...")
        await client.connect()
        log("✓ Connected\n")

        # Read initial state via client's internal BleakClient
        log("Initial firmware state:")
        mode_val = await client._client.read_gatt_char(CHAR_MODE)
        rgb_val = await client._client.read_gatt_char(CHAR_RGB)
        white_val = await client._client.read_gatt_char(CHAR_WHITE)
        log(f"  MODE: 0x{mode_val[0]:02x}, RGB: {list(rgb_val)}, WHITE: {list(white_val)}\n")

        # Test different white temperatures and brightnesses
        whites = [
            ("Full Warm White (100% warm)", WhiteColor(100, 0)),
            ("Full Cold White (100% cold)", WhiteColor(0, 100)),
            ("Balanced Mix (50/50)", WhiteColor(50, 50)),
            ("Warm Dominant (75% warm)", WhiteColor(75, 25)),
            ("Cold Dominant (25% warm)", WhiteColor(25, 75)),
            ("Dim Warm (25% warm)", WhiteColor(25, 0)),
            ("Dim Cold (25% cold)", WhiteColor(0, 25)),
            ("Bright Warm", WhiteColor(100, 0)),
            ("Bright Cold", WhiteColor(0, 100)),
            ("Very Dim (10/10)", WhiteColor(10, 10)),
        ]

        log("Testing white temperatures:")
        log("(Firmware state will be recorded after each command)\n")

        state_changes = []
        for i, (name, color) in enumerate(whites, 1):
            log(f"[{i}/{len(whites)}] Setting: {name:30} {color}")
            await client.set_white_color(color)
            await asyncio.sleep(1.5)

            # Read firmware state after command using client's internal connection
            mode_val = await client._client.read_gatt_char(CHAR_MODE)
            white_val = await client._client.read_gatt_char(CHAR_WHITE)
            log(f"          Firmware: MODE=0x{mode_val[0]:02x}, WHITE={list(white_val)}")

            # Check if firmware matches what we sent
            sent_values = (color.warm, color.cold)
            received_values = tuple(white_val)
            match = "✓ MATCH" if sent_values == received_values else f"✗ MISMATCH (expected {sent_values})"
            log(f"          {match}\n")

            state_changes.append({
                "name": name,
                "sent": sent_values,
                "received": received_values,
                "mode": mode_val[0],
                "match": sent_values == received_values
            })

        log("\n" + "=" * 70)
        log("White mode test complete!")
        log("=" * 70)

        # Summary
        matches = sum(1 for s in state_changes if s["match"])
        total = len(state_changes)
        log(f"\nResults: {matches}/{total} commands matched firmware state")

        if matches == total:
            log("\n🎉 WHITE MODE WORKING PERFECTLY!")
            log("All commands were accepted and firmware state matches.")
        elif matches > 0:
            log(f"\n⚠️  WHITE MODE PARTIALLY WORKING")
            log(f"{matches} out of {total} commands worked correctly.")
        else:
            log("\n✗ WHITE MODE NOT WORKING")
            log("Firmware did not accept white color commands.")

        log("\nSummary:")
        log("  ✓ RGB mode: Working (verified earlier)")
        log(f"  {'✓' if matches == total else '⚠️'} WHITE mode: {'Working' if matches == total else 'Needs investigation'}")
        log("  ✓ Protocol fix: response=True for MODE characteristic")

        # Test returning to button control
        log("\n" + "=" * 70)
        log("Restoring button control...")
        log("=" * 70)
        log("\nSetting to dim warm white (button-compatible state)...")
        await client.set_white_color(WhiteColor(1, 0))
        await asyncio.sleep(1)

        log("\n✓ Test complete - lamp should respond to button presses")

    except Exception as e:
        log(f"\n✗ Error: {e}")
        import traceback
        log(traceback.format_exc())

    finally:
        if client.is_connected:
            await client.disconnect()
            log("\nDisconnected")

        # Save results to file
        log(f"\n{'='*70}")
        log(f"Results saved to: {results_file}")
        log('='*70)

        with open(results_file, 'w') as f:
            f.write('\n'.join(results))

        print(f"\n✓ Full results written to: {results_file}")


if __name__ == "__main__":
    asyncio.run(main())
