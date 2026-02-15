#!/usr/bin/env python3
"""Enumerate all BLE services, characteristics, and device information."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bleak import BleakClient
from lampster.client import LampsterClient


async def main():
    print("=" * 70)
    print("BLE Device Information & Service Enumeration")
    print("=" * 70)
    print()

    # Discover device
    print("🔍 Discovering Lampster...")
    try:
        devices = await LampsterClient.discover(timeout=5.0)
        device = devices[0]
        print(f"✓ Found: {device.name}")
        print(f"  Address: {device.address}")
        print()
    except Exception as e:
        print(f"✗ Discovery failed: {e}")
        return

    # Connect and enumerate
    print("📡 Connecting and enumerating services...")
    print()
    async with BleakClient(device.address) as client:
        print("✓ Connected")
        print()

        # Try to get device info from standard characteristics
        print("-" * 70)
        print("STANDARD DEVICE INFORMATION (Service 0x180A)")
        print("-" * 70)

        device_info_service = "0000180a-0000-1000-8000-00805f9b34fb"

        # Standard device info characteristics
        info_chars = {
            "00002a29-0000-1000-8000-00805f9b34fb": "Manufacturer Name",
            "00002a24-0000-1000-8000-00805f9b34fb": "Model Number",
            "00002a25-0000-1000-8000-00805f9b34fb": "Serial Number",
            "00002a27-0000-1000-8000-00805f9b34fb": "Hardware Revision",
            "00002a26-0000-1000-8000-00805f9b34fb": "Firmware Revision",
            "00002a28-0000-1000-8000-00805f9b34fb": "Software Revision",
        }

        for char_uuid, name in info_chars.items():
            try:
                value = await client.read_gatt_char(char_uuid)
                print(f"{name}: {value.decode('utf-8', errors='ignore')}")
            except Exception:
                pass  # Characteristic not available

        print()

        # Enumerate ALL services and characteristics
        print("-" * 70)
        print("ALL SERVICES AND CHARACTERISTICS")
        print("-" * 70)

        for service in client.services:
            print(f"\n📦 Service: {service.uuid}")
            print(f"   Description: {service.description}")

            for char in service.characteristics:
                print(f"\n   📝 Characteristic: {char.uuid}")
                print(f"      Handle: 0x{char.handle:04x}")
                print(f"      Properties: {', '.join(char.properties)}")
                print(f"      Description: {char.description}")

                # Try to read if readable
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        print(f"      Value: {value.hex()} ({len(value)} bytes)")
                        # Try to decode as string
                        try:
                            decoded = value.decode('utf-8', errors='ignore')
                            if decoded.isprintable():
                                print(f"      Decoded: {decoded}")
                        except:
                            pass
                    except Exception as e:
                        print(f"      Read failed: {e}")

                # Show descriptors
                for descriptor in char.descriptors:
                    print(f"      🔖 Descriptor: {descriptor.uuid} (Handle: 0x{descriptor.handle:04x})")

        print()
        print("=" * 70)
        print("Known Lampster Characteristics:")
        print("=" * 70)
        print("Mode:  Handle 0x0021 (Char 32)")
        print("RGB:   Handle 0x0025 (Char 37)")
        print("White: Handle 0x002a (Char 42)")
        print()
        print("Commands:")
        print("MODE_POWER_ON  = 0xc0 (192)")
        print("MODE_POWER_OFF = 0x40 (64)")
        print("MODE_RGB       = 0xa8 (168)")
        print("MODE_WHITE     = 0xc8 (200)")
        print()


if __name__ == "__main__":
    asyncio.run(main())
