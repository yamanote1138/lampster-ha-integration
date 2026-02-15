# The Lampster - Home Assistant Integration

Home Assistant custom integration for controlling The Lampster RGB Bluetooth lamp.

## 🙏 Attribution

**This integration is based on the protocol documentation from [Noki's The Lampster project](https://github.com/Noki/the-lampster).**

All protocol information, BLE characteristic mappings, and command specifications come from Noki's excellent reverse engineering work. This project would not be possible without their documentation. Please visit and ⭐ star [their repository](https://github.com/Noki/the-lampster)!

## Features

- ✨ **Full RGB color control** - 16.7 million colors (0-100% per channel)
- 🌡️ **White color temperature** - Warm to cold white adjustment
- 💡 **Brightness control** - Smooth dimming
- 🔍 **Automatic device discovery** - Find your Lampster via Bluetooth
- 🏠 **Native Home Assistant integration** - Full UI support
- 🔄 **Mode switching** - Seamless RGB and white mode transitions

## Current Status

**Phase 1: Local Testing** ✅ **COMPLETE** (v0.2.0)

The core Python library and BLE protocol are fully working:
- ✅ Discover Lampster devices via BLE
- ✅ RGB color control (7+ colors tested and working)
- ✅ White color temperature control (10 variations tested - 100% success)
- ✅ Mode switching (RGB ↔ WHITE)
- ✅ Protocol fix: MODE characteristic requires `response=True`
- ✅ Comprehensive test suite with automatic result recording
- ✅ Button control behavior documented

**Known Behavior:**
- BLE control and button control are mutually exclusive (expected)
- BLE POWER_OFF command doesn't work (use WHITE mode to restore button)
- Device auto-powers on when plugged in

**Phase 2: Home Assistant Integration** 🚧 **READY TO START**

Ready to build the full HA custom component on top of the validated core library.

## Requirements

- **Python**: 3.11 or higher
- **Bluetooth**: Built-in or USB Bluetooth adapter
- **Platform**: macOS (Phase 1), Linux/Home Assistant (Phase 2)
- **The Lampster**: The actual lamp device

## Quick Start (Phase 1: Local Testing)

### Installation

```bash
# Clone the repository
cd /path/to/lampster-ha-integration

# Install dependencies with uv
uv sync

# Or use pip in a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Discovery

Find your Lampster device:

```bash
uv run tests/test_discovery.py
```

This will scan for nearby Lampster devices and display their addresses. Copy the address for use in other tests.

### Update Device Address

Edit the test files and update `DEVICE_ADDRESS` with your device's address:

```python
DEVICE_ADDRESS = "XX:XX:XX:XX:XX:XX"  # Replace with your device address
```

### Run Tests

Test each function individually:

```bash
# Test power control
uv run tests/test_power.py

# Test RGB colors
uv run tests/test_rgb.py

# Test white modes
uv run tests/test_white.py

# Run comprehensive test
uv run tests/test_all_modes.py
```

## Usage Example

```python
import asyncio
from lampster import LampsterClient, RGBColor, WhiteColor

async def main():
    # Connect to your Lampster
    client = LampsterClient("XX:XX:XX:XX:XX:XX")
    await client.connect()

    # Turn on and set to red
    await client.power_on()
    await client.set_rgb_color(RGBColor(100, 0, 0))

    # Switch to warm white
    await client.set_white_color(WhiteColor(100, 0))

    # Turn off
    await client.power_off()
    await client.disconnect()

asyncio.run(main())
```

## Protocol Details

The Lampster uses Bluetooth Low Energy (BLE) with three main characteristics:

| Characteristic | Handle | Function |
|----------------|--------|----------|
| Mode Control | 0x0021 | Power on/off, mode selection |
| RGB Control | 0x002a | RGB LED control (0-100 per channel) |
| White Control | 0x0025 | Warm/Cold white LEDs (0-100 each) |

### Commands

**Mode Control** (Characteristic 0x0021):
- `0xC0` - Power on
- `0x40` - Power off
- `0xA8` - RGB mode
- `0xC8` - White mode
- `0x28` - Off mode

**RGB Control** (Characteristic 0x002a):
- Format: `[RR, GG, BB]` where each value is 0x00-0x64 (0-100)

**White Control** (Characteristic 0x0025):
- Format: `[WW, CC]` where WW=warm white, CC=cold white (0x00-0x64)

For complete protocol documentation, see: https://github.com/Noki/the-lampster

## Project Structure

```
lampster-ha-integration/
├── lampster/                  # Core library
│   ├── client.py             # LampsterClient - main BLE control
│   ├── constants.py          # BLE UUIDs and commands
│   ├── models.py             # RGBColor, WhiteColor, LampState
│   └── exceptions.py         # Custom exceptions
│
├── tests/                     # Phase 1: Local testing scripts
│   ├── test_discovery.py     # Device discovery
│   ├── test_power.py         # Power control testing
│   ├── test_rgb.py           # RGB mode testing
│   ├── test_white.py         # White mode testing
│   └── test_all_modes.py     # Comprehensive testing
│
└── custom_components/         # Phase 2: HA integration (coming soon)
    └── lampster/
```

## Troubleshooting

### No devices found
- Ensure your Lampster is powered on
- Keep the lamp close to your computer (within 2 meters)
- Check that Bluetooth is enabled on your system
- Try power cycling the lamp

### Connection fails
- Verify the device address is correct
- Unpair the device from system Bluetooth settings if previously paired
- Try power cycling the lamp
- Check signal strength (keep lamp close)

### Commands not working
- Ensure connection is established before sending commands
- Check logs with `logging.basicConfig(level=logging.DEBUG)`
- Verify characteristic UUIDs match your device (use characteristic enumeration in test_discovery.py)
- Some devices may have different UUIDs than documented

### Characteristic UUID issues
The documented characteristic handles (0x0021, 0x0025, 0x002a) may be device-specific. To find your device's actual UUIDs:

1. Uncomment the characteristic enumeration in `tests/test_discovery.py`
2. Run the discovery script to see all characteristics
3. Update UUIDs in `lampster/constants.py` if needed

## Development Roadmap

### ✅ Phase 1: Local Testing (Complete)
- [x] Core library implementation
- [x] BLE client with bleak
- [x] Discovery functionality
- [x] Power control
- [x] RGB color control
- [x] White mode control
- [x] Test scripts for validation

### 🚧 Phase 2: Home Assistant Integration (Next)
- [ ] Integration manifest and setup
- [ ] Config flow with device discovery
- [ ] Light entity implementation
- [ ] Color mode support (RGB + color temp)
- [ ] Brightness control
- [ ] State management
- [ ] Testing in Home Assistant

### 🔮 Phase 3: Polish & Release
- [ ] Error handling improvements
- [ ] Connection retry logic
- [ ] HACS integration
- [ ] Documentation
- [ ] Community release

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

When contributing:
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
- Properly attribute any protocol discoveries to Noki's work

## License

MIT License (coming soon)

## Credits

- **Protocol Documentation**: [Noki](https://github.com/Noki) - Reverse engineered the BLE protocol
- **Integration Development**: [Your Name]
- **Home Assistant**: [https://www.home-assistant.io](https://www.home-assistant.io)
- **Bleak Library**: Cross-platform BLE library for Python

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/lampster-ha-integration/issues)
- **Protocol Questions**: See [Noki's repository](https://github.com/Noki/the-lampster)
- **Home Assistant**: [Home Assistant Community](https://community.home-assistant.io)

---

Made with ❤️ for The Lampster community
