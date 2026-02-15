#!/usr/bin/env python3
"""Interactive CLI for controlling The Lampster.

A menu-driven interface for discovering, connecting, and controlling
The Lampster RGB lamp via Bluetooth.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from lampster.client import LampsterClient
from lampster.models import RGBColor, WhiteColor


class LampsterCLI:
    """Interactive CLI for The Lampster."""

    def __init__(self):
        self.client: Optional[LampsterClient] = None
        self.running = True
        self.debug_file = None
        self.debug_path = Path("debug")
        self.debug_path.mkdir(exist_ok=True)
        self.config_path = Path("config.json")

        # Load config and debug state
        self.debug_enabled = self._load_config().get("debug_enabled", False)

        # Auto-enable debug logging if it was enabled in last session
        if self.debug_enabled:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = self.debug_path / f"cli_session_{timestamp}.log"
            self.debug_file = open(log_filename, "w")
            self.debug_log("=== Debug logging started ===")
            self.debug_log(f"Session log: {log_filename}")
            print(f"✓ Debug logging enabled (auto-loaded from config)")
            print(f"  Log: {log_filename}\n")

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_config(self, config: dict):
        """Save configuration to file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")

    def debug_log(self, message: str):
        """Log a debug message if debug logging is enabled."""
        if self.debug_enabled and self.debug_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            self.debug_file.write(f"[{timestamp}] {message}\n")
            self.debug_file.flush()

    def toggle_debug_logging(self):
        """Toggle debug logging on/off."""
        if self.debug_enabled:
            # Disable debug logging
            self.debug_log("=== Debug logging disabled by user ===")
            if self.debug_file:
                self.debug_file.close()
                self.debug_file = None
            self.debug_enabled = False
            self._save_config({"debug_enabled": False})
            print("✓ Debug logging disabled")
        else:
            # Enable debug logging
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = self.debug_path / f"cli_session_{timestamp}.log"
            self.debug_file = open(log_filename, "w")
            self.debug_enabled = True
            self._save_config({"debug_enabled": True})
            self.debug_log("=== Debug logging started ===")
            self.debug_log(f"Session log: {log_filename}")
            print(f"✓ Debug logging enabled: {log_filename}")

    def close_debug_log(self):
        """Close debug log file if open."""
        if self.debug_file:
            self.debug_log("=== Session ended ===")
            self.debug_file.close()
            self.debug_file = None

    def clear_screen(self):
        """Clear the terminal screen."""
        print("\033[2J\033[H", end="")

    def print_header(self):
        """Print the CLI header."""
        print("=" * 70)
        print("  The Lampster - Interactive Control CLI")
        print("=" * 70)
        print()

    def print_status(self):
        """Print current connection and lamp status."""
        if self.client and self.client.is_connected:
            state = self.client.state
            print(f"📡 Status: Connected")
            print(f"💡 Power: {'ON' if state.is_on else 'OFF'}")
            print(f"🎨 Mode: {state.mode.upper()}")
            if state.mode == "rgb" and state.rgb_color:
                print(f"🌈 RGB: {state.rgb_color}")
            elif state.mode == "white" and state.white_color:
                print(f"🌡️  White: {state.white_color}")
        else:
            print("📡 Status: Not connected")

        if self.debug_enabled:
            print(f"🐛 Debug: ENABLED")
        print()

    def print_main_menu(self):
        """Print the main menu (disconnected state)."""
        print("Commands:")
        print("  1) Discover and connect")
        print("  9) Toggle debug logging")
        print("  0) Exit")
        print()

    def print_connected_menu(self):
        """Print the connected menu."""
        print("Commands:")
        print("  1) Toggle power")
        print("  2) Set RGB color")
        print("  3) Set white temperature")
        print("  4) Set brightness")
        print("  5) Disconnect")
        print("  9) Toggle debug logging")
        print("  0) Exit")
        print()

    async def discover_devices(self):
        """Discover Lampster devices."""
        print("\n🔍 Scanning for Lampster devices...")
        try:
            devices = await LampsterClient.discover(timeout=5.0)
            print(f"\n✓ Found {len(devices)} device(s):\n")

            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device.name}")
                print(f"     Address: {device.address}")
                print()

            return devices
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return []

    async def connect_device(self):
        """Discover and connect to a Lampster device."""
        self.debug_log("COMMAND: Connect device")
        devices = await self.discover_devices()
        if not devices:
            self.debug_log("ERROR: No devices found")
            print("No devices found. Make sure your lamp is powered on.")
            await asyncio.sleep(2)
            return

        self.debug_log(f"INFO: Found {len(devices)} device(s)")
        for i, device in enumerate(devices, 1):
            self.debug_log(f"  Device {i}: {device.name} ({device.address})")

        # If only 1 device, use it as default
        default = "1" if len(devices) == 1 else ""
        prompt = f"Select device number [default: {default}] (or 0 to cancel): " if default else "Select device number (or 0 to cancel): "

        try:
            user_input = input(prompt).strip()
            if not user_input and default:
                user_input = default
            self.debug_log(f"INPUT: Device selection = '{user_input}'")

            choice = int(user_input)
            if choice == 0:
                self.debug_log("ACTION: Connection cancelled by user")
                return
            if 1 <= choice <= len(devices):
                device = devices[choice - 1]
                self.debug_log(f"ACTION: Connecting to {device.name} at {device.address}")
                print(f"\n📡 Connecting to {device.name}...")

                self.client = LampsterClient(device.address)
                await self.client.connect()

                self.debug_log(f"STATE: Connected successfully to {device.name}")
                print(f"✓ Connected successfully!")
                await asyncio.sleep(1)  # Brief pause before entering connected menu
            else:
                self.debug_log(f"WARNING: Invalid device selection {choice}")
                print("Invalid selection")
                await asyncio.sleep(1)
        except ValueError as e:
            self.debug_log(f"ERROR: ValueError in device selection: {e}")
            print("Invalid input")
            await asyncio.sleep(1)
        except Exception as e:
            self.debug_log(f"ERROR: Connection failed: {type(e).__name__}: {e}")
            import traceback
            self.debug_log(f"TRACEBACK: {traceback.format_exc()}")
            print(f"✗ Connection failed: {e}")
            await asyncio.sleep(2)

    async def toggle_power(self):
        """Toggle lamp power on/off."""
        self.debug_log("COMMAND: Toggle power")
        if not self.client or not self.client.is_connected:
            self.debug_log("ERROR: Not connected to device")
            print("✗ Not connected to a device")
            await asyncio.sleep(1)
            return

        try:
            state = self.client.state
            self.debug_log(f"STATE: Current state - is_on={state.is_on}, mode={state.mode}")
            if state.is_on:
                self.debug_log("ACTION: Powering off lamp")
                await self.client.power_off()
                self.debug_log("STATE: Lamp powered OFF")
                print("✓ Lamp powered OFF")
            else:
                self.debug_log("ACTION: Powering on lamp")
                await self.client.power_on()
                self.debug_log("STATE: Lamp powered ON")
                print("✓ Lamp powered ON")
            await asyncio.sleep(0.5)
        except Exception as e:
            self.debug_log(f"ERROR: Exception in toggle_power: {type(e).__name__}: {e}")
            import traceback
            self.debug_log(f"TRACEBACK: {traceback.format_exc()}")
            print(f"✗ Error: {e}")
            await asyncio.sleep(2)

    async def set_rgb_color(self):
        """Set RGB color interactively (loop mode)."""
        self.debug_log("COMMAND: Enter RGB color selection")
        if not self.client or not self.client.is_connected:
            self.debug_log("ERROR: Not connected to device")
            print("✗ Not connected to a device")
            await asyncio.sleep(1)
            return

        colors = {
            "1": ("Red", RGBColor(100, 0, 0)),
            "2": ("Green", RGBColor(0, 100, 0)),
            "3": ("Blue", RGBColor(0, 0, 100)),
            "4": ("Yellow", RGBColor(100, 100, 0)),
            "5": ("Cyan", RGBColor(0, 100, 100)),
            "6": ("Magenta", RGBColor(100, 0, 100)),
            "7": ("White", RGBColor(100, 100, 100)),
            "8": ("Orange", RGBColor(100, 50, 0)),
            "9": ("Purple", RGBColor(50, 0, 100)),
        }

        while True:
            self.clear_screen()
            self.print_header()
            self.print_status()
            print("\n🌈 RGB Color Selection")
            print("=" * 70)
            print("\nQuick colors:")
            print("  1) Red      2) Green    3) Blue      4) Yellow")
            print("  5) Cyan     6) Magenta  7) White     8) Orange")
            print("  9) Purple   0) Custom   (ESC to exit)")
            print()

            try:
                choice = input("Select color: ").strip()
                self.debug_log(f"INPUT: RGB color choice = '{choice}'")

                # ESC key or 'q' or empty to exit
                if not choice or choice == '\x1b' or choice.lower() == 'q':
                    self.debug_log("ACTION: Exit RGB color selection")
                    return

                if choice in colors:
                    name, color = colors[choice]
                    self.debug_log(f"ACTION: Setting RGB to {name} {color}")
                    await self.client.set_rgb_color(color)
                    self.debug_log(f"STATE: RGB color set to {name}")
                    print(f"✓ Color set to {name}")
                    await asyncio.sleep(0.5)  # Brief pause to see confirmation
                elif choice == "0":
                    # Custom color
                    print("\nEnter RGB values (0-100):")
                    r = int(input("  Red: ").strip())
                    g = int(input("  Green: ").strip())
                    b = int(input("  Blue: ").strip())
                    self.debug_log(f"INPUT: Custom RGB = ({r}, {g}, {b})")

                    color = RGBColor(r, g, b)
                    self.debug_log(f"ACTION: Setting custom RGB {color}")
                    await self.client.set_rgb_color(color)
                    self.debug_log(f"STATE: Custom RGB color set")
                    print(f"✓ Custom color set")
                    await asyncio.sleep(0.5)
                else:
                    self.debug_log(f"WARNING: Invalid RGB selection '{choice}'")
                    print("Invalid selection")
                    await asyncio.sleep(0.5)

            except ValueError as e:
                self.debug_log(f"ERROR: ValueError in RGB selection: {e}")
                print("✗ Invalid input - values must be 0-100")
                await asyncio.sleep(1)
            except Exception as e:
                self.debug_log(f"ERROR: Exception in RGB selection: {type(e).__name__}: {e}")
                import traceback
                self.debug_log(f"TRACEBACK: {traceback.format_exc()}")
                print(f"✗ Error: {e}")
                await asyncio.sleep(2)
                return

    async def set_white_temp(self):
        """Set white temperature interactively (loop mode)."""
        self.debug_log("COMMAND: Enter white temperature selection")
        if not self.client or not self.client.is_connected:
            self.debug_log("ERROR: Not connected to device")
            print("✗ Not connected to a device")
            await asyncio.sleep(1)
            return

        presets = {
            "1": ("Warm", WhiteColor(100, 0)),
            "2": ("Neutral", WhiteColor(50, 50)),
            "3": ("Cool", WhiteColor(0, 100)),
        }

        while True:
            self.clear_screen()
            self.print_header()
            self.print_status()
            print("\n🌡️  White Temperature Selection")
            print("=" * 70)
            print("\nPresets:")
            print("  1) Warm (100% warm)")
            print("  2) Neutral (50/50)")
            print("  3) Cool (100% cool)")
            print("  4) Custom   (ESC to exit)")
            print()

            try:
                choice = input("Select preset: ").strip()
                self.debug_log(f"INPUT: White temperature choice = '{choice}'")

                # ESC key or 'q' or empty to exit
                if not choice or choice == '\x1b' or choice.lower() == 'q':
                    self.debug_log("ACTION: Exit white temperature selection")
                    return

                if choice in presets:
                    name, color = presets[choice]
                    self.debug_log(f"ACTION: Setting white to {name} {color}")
                    await self.client.set_white_color(color)
                    self.debug_log(f"STATE: White temperature set to {name}")
                    print(f"✓ Temperature set to {name}")
                    await asyncio.sleep(0.5)  # Brief pause to see confirmation
                elif choice == "4":
                    # Custom
                    print("\nEnter values (0-100):")
                    warm = int(input("  Warm: ").strip())
                    cold = int(input("  Cold: ").strip())
                    self.debug_log(f"INPUT: Custom white = (warm={warm}, cold={cold})")

                    color = WhiteColor(warm, cold)
                    self.debug_log(f"ACTION: Setting custom white {color}")
                    await self.client.set_white_color(color)
                    self.debug_log(f"STATE: Custom white temperature set")
                    print(f"✓ Custom temperature set")
                    await asyncio.sleep(0.5)
                else:
                    self.debug_log(f"WARNING: Invalid white selection '{choice}'")
                    print("Invalid selection")
                    await asyncio.sleep(0.5)

            except ValueError as e:
                self.debug_log(f"ERROR: ValueError in white selection: {e}")
                print("✗ Invalid input - values must be 0-100")
                await asyncio.sleep(1)
            except Exception as e:
                self.debug_log(f"ERROR: Exception in white selection: {type(e).__name__}: {e}")
                import traceback
                self.debug_log(f"TRACEBACK: {traceback.format_exc()}")
                print(f"✗ Error: {e}")
                await asyncio.sleep(2)
                return

    async def set_brightness(self):
        """Set brightness by scaling current color."""
        self.debug_log("COMMAND: Set brightness")
        if not self.client or not self.client.is_connected:
            self.debug_log("ERROR: Not connected to device")
            print("✗ Not connected to a device")
            await asyncio.sleep(1)
            return

        state = self.client.state
        self.debug_log(f"STATE: Current mode={state.mode}, is_on={state.is_on}")

        self.clear_screen()
        self.print_header()
        self.print_status()
        print("\n💡 Brightness Control")
        print("=" * 70)
        print("\nCurrent mode:", state.mode.upper())

        if state.mode == "off":
            self.debug_log("WARNING: Lamp is off")
            print("✗ Lamp is off - turn it on first")
            await asyncio.sleep(1)
            return

        try:
            brightness = int(input("\nEnter brightness (0-100): ").strip())
            self.debug_log(f"INPUT: Brightness = {brightness}")

            if not 0 <= brightness <= 100:
                self.debug_log(f"WARNING: Invalid brightness value {brightness}")
                print("✗ Brightness must be 0-100")
                await asyncio.sleep(1)
                return

            if state.mode == "rgb" and state.rgb_color:
                # Scale RGB by brightness
                scale = brightness / 100
                new_color = RGBColor(
                    int(100 * scale),
                    int((state.rgb_color.green / (state.rgb_color.red or 1)) * 100 * scale),
                    int((state.rgb_color.blue / (state.rgb_color.red or 1)) * 100 * scale)
                )
                self.debug_log(f"ACTION: Setting RGB brightness to {brightness}% -> {new_color}")
                await self.client.set_rgb_color(new_color)
                self.debug_log(f"STATE: RGB brightness set to {brightness}%")
                print(f"✓ RGB brightness set to {brightness}%")
                await asyncio.sleep(1)

            elif state.mode == "white" and state.white_color:
                # Scale white by brightness
                scale = brightness / 100
                total = state.white_color.warm + state.white_color.cold
                if total > 0:
                    warm_ratio = state.white_color.warm / total
                    cold_ratio = state.white_color.cold / total
                    new_color = WhiteColor(
                        int(warm_ratio * 100 * scale),
                        int(cold_ratio * 100 * scale)
                    )
                else:
                    new_color = WhiteColor(int(50 * scale), int(50 * scale))

                self.debug_log(f"ACTION: Setting white brightness to {brightness}% -> {new_color}")
                await self.client.set_white_color(new_color)
                self.debug_log(f"STATE: White brightness set to {brightness}%")
                print(f"✓ White brightness set to {brightness}%")
                await asyncio.sleep(1)
            else:
                self.debug_log("WARNING: No current color to adjust")
                print("✗ No current color to adjust")
                await asyncio.sleep(1)

        except ValueError as e:
            self.debug_log(f"ERROR: ValueError in brightness: {e}")
            print("✗ Invalid input")
            await asyncio.sleep(1)
        except Exception as e:
            self.debug_log(f"ERROR: Exception in brightness: {type(e).__name__}: {e}")
            import traceback
            self.debug_log(f"TRACEBACK: {traceback.format_exc()}")
            print(f"✗ Error: {e}")
            await asyncio.sleep(2)

    async def disconnect(self):
        """Disconnect from device."""
        self.debug_log("COMMAND: Disconnect")
        if self.client and self.client.is_connected:
            self.debug_log("ACTION: Disconnecting from device")
            await self.client.disconnect()
            self.debug_log("STATE: Disconnected")
            print("✓ Disconnected")
            await asyncio.sleep(1)
        else:
            self.debug_log("WARNING: Not connected to any device")
            print("Not connected")
            await asyncio.sleep(1)

    async def run_connected_menu(self):
        """Run the connected device menu loop."""
        while self.client and self.client.is_connected and self.running:
            self.clear_screen()
            self.print_header()
            self.print_status()
            self.print_connected_menu()

            try:
                choice = input("Enter command: ").strip()
                self.debug_log(f"INPUT: Connected menu choice = '{choice}'")

                if choice == "1":
                    await self.toggle_power()
                elif choice == "2":
                    await self.set_rgb_color()
                elif choice == "3":
                    await self.set_white_temp()
                elif choice == "4":
                    await self.set_brightness()
                elif choice == "5":
                    await self.disconnect()
                    return  # Return to main menu
                elif choice == "9":
                    self.toggle_debug_logging()
                    await asyncio.sleep(1)
                elif choice == "0":
                    self.debug_log("ACTION: User exiting application")
                    print("\nExiting...")
                    await self.disconnect()
                    self.running = False
                    return
                else:
                    self.debug_log(f"WARNING: Invalid command '{choice}'")
                    print("Invalid command")
                    await asyncio.sleep(0.5)

            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                await self.disconnect()
                self.running = False
                return
            except EOFError:
                print("\n\nEOF - exiting")
                self.running = False
                return
            except Exception as e:
                print(f"\n✗ Unexpected error: {e}")
                input("\nPress Enter to continue...")

    async def run(self):
        """Run the interactive CLI."""
        self.clear_screen()
        self.print_header()
        print("Welcome! Use this tool to discover and control your Lampster.\n")
        await asyncio.sleep(1)

        try:
            while self.running:
                self.clear_screen()
                self.print_header()
                self.print_status()
                self.print_main_menu()

                try:
                    choice = input("Enter command: ").strip()
                    self.debug_log(f"INPUT: Main menu choice = '{choice}'")

                    if choice == "1":
                        await self.connect_device()
                        # If connected, switch to connected menu
                        if self.client and self.client.is_connected:
                            await self.run_connected_menu()
                    elif choice == "9":
                        self.toggle_debug_logging()
                        await asyncio.sleep(1)
                    elif choice == "0":
                        self.debug_log("ACTION: User exiting application")
                        print("\nExiting...")
                        self.running = False
                        break
                    else:
                        self.debug_log(f"WARNING: Invalid command '{choice}'")
                        print("Invalid command")
                        await asyncio.sleep(0.5)

                except KeyboardInterrupt:
                    self.debug_log("ACTION: Interrupted by user (Ctrl+C)")
                    print("\n\nInterrupted by user")
                    break
                except EOFError:
                    self.debug_log("ACTION: EOF received")
                    print("\n\nEOF - exiting")
                    break
                except Exception as e:
                    self.debug_log(f"ERROR: Unexpected error in main loop: {type(e).__name__}: {e}")
                    import traceback
                    self.debug_log(f"TRACEBACK: {traceback.format_exc()}")
                    print(f"\n✗ Unexpected error: {e}")
                    input("\nPress Enter to continue...")
        finally:
            # Ensure debug log is closed on exit
            self.close_debug_log()

        print("\nGoodbye!")


async def main():
    """Entry point for the CLI."""
    cli = LampsterCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
