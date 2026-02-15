# The Lampster - Home Assistant Integration

Home Assistant custom integration for The Lampster RGB Bluetooth lamp (Model: LA-2017B).

## Features

- ✅ **Automatic Bluetooth Discovery** - Device appears automatically in HA
- ✅ **RGB Color Control** - Full RGB color picker support
- ✅ **Color Temperature** - Warm to cool white (2700K - 6500K)
- ✅ **Brightness Control** - Adjust light intensity
- ✅ **Power Control** - Turn on/off
- ✅ **State Tracking** - Reads actual device state
- ✅ **Local Control** - No cloud required

## Requirements

- Home Assistant 2023.1 or newer
- Bluetooth adapter with BLE support
- Python 3.11 or newer
- The Lampster device (Model: LA-2017B)

## Installation

### Method 1: Manual Installation

1. Copy the `custom_components/lampster` directory to your Home Assistant `config/custom_components/` directory:

   ```bash
   # On your HA machine
   cd /config
   mkdir -p custom_components
   cp -r /path/to/lampster-ha-integration/custom_components/lampster custom_components/
   ```

2. Ensure the lampster library is importable by Home Assistant:

   ```bash
   # Copy the core library
   cp -r /path/to/lampster-ha-integration/lampster /config/custom_components/lampster/
   ```

3. Restart Home Assistant

4. Go to **Settings** → **Devices & Services** → **Add Integration**

5. Search for "Lampster" and follow the setup flow

### Method 2: Development Testing

For development/testing without copying files:

1. Create a symbolic link from your HA config to the integration:

   ```bash
   cd /config/custom_components
   ln -s /path/to/lampster-ha-integration/custom_components/lampster lampster
   ```

2. Restart Home Assistant

## Configuration

### Automatic Discovery

The integration will automatically discover Lampster devices via Bluetooth. When a device is found, you'll see a notification in Home Assistant to set it up.

### Manual Setup

1. Navigate to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Lampster"
4. Select your device from the list
5. Click **Submit**

The integration will create a light entity named `light.lampster`.

## Usage

### Via UI

Use the standard Home Assistant light controls:

- **Power**: Toggle on/off
- **Brightness**: Slide to adjust (0-100%)
- **Color**: RGB color picker
- **Temperature**: Warm to cool white slider

### Via Automations

```yaml
# Turn on with specific RGB color
service: light.turn_on
target:
  entity_id: light.lampster
data:
  rgb_color: [255, 0, 0]  # Red
  brightness: 200

# Set color temperature (warm white)
service: light.turn_on
target:
  entity_id: light.lampster
data:
  color_temp_kelvin: 2700
  brightness: 150

# Turn off
service: light.turn_off
target:
  entity_id: light.lampster
```

### Via Scripts

```yaml
# script.yaml
lampster_red:
  alias: "Lampster: Red"
  sequence:
    - service: light.turn_on
      target:
        entity_id: light.lampster
      data:
        rgb_color: [255, 0, 0]
        brightness: 255

lampster_warm_white:
  alias: "Lampster: Warm White"
  sequence:
    - service: light.turn_on
      target:
        entity_id: light.lampster
      data:
        color_temp_kelvin: 2700
        brightness: 200
```

## Technical Details

### BLE Protocol

Protocol based on reverse engineering by [Noki](https://github.com/Noki/the-lampster).

**Device Information:**
- Model: LA-2017B
- Manufacturer: "The Lampster, the licitatie"
- Hardware: 100B
- Firmware: 10

**BLE Characteristics:**
- Mode: `01ff5554-ba5e-f4ee-5ca1-eb1e5e4b1ce0` (Handle 0x0020)
- RGB: `01ff5559-ba5e-f4ee-5ca1-eb1e5e4b1ce0` (Handle 0x0029)
- White: `01ff5556-ba5e-f4ee-5ca1-eb1e5e4b1ce0` (Handle 0x0024)

### Color Conversions

**RGB Mode:**
- Home Assistant: 0-255 per channel
- Device: 0-100 per channel
- Brightness scaling applied during conversion

**Color Temperature Mode:**
- Home Assistant: Kelvin (2700K - 6500K)
- Device: Warm/cold percentage (0-100 each)
- Lower Kelvin = warmer = more warm LED
- Higher Kelvin = cooler = more cold LED

## Troubleshooting

### Integration doesn't appear

1. Check that Bluetooth is enabled in Home Assistant
2. Ensure the device is powered on and nearby (< 2m recommended)
3. Check Home Assistant logs: **Settings** → **System** → **Logs**
4. Look for errors containing "lampster"

### Device not discovered

1. Ensure device name contains "Lamp" (should be "Lampster")
2. Check Bluetooth range - move device closer
3. Power cycle the device
4. Restart Home Assistant

### Connection issues

1. Only one Bluetooth connection at a time - close the official app
2. Power cycle the device
3. Check Home Assistant logs for specific errors
4. Ensure no other integrations are using the device

### Colors not changing

1. Verify device is connected (check entity state)
2. Power cycle the device
3. Remove and re-add the integration
4. Check debug logs for BLE errors

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.lampster: debug
    lampster: debug
```

Then restart Home Assistant.

## Known Limitations

1. **Single Connection**: Device only supports one Bluetooth connection at a time
2. **No Button Control**: Physical button disabled when using BLE (by design)
3. **State Persistence**: Device remembers last color even when powered off
4. **Range**: Bluetooth LE has limited range (~10m line of sight, less through walls)
5. **Power Off from RGB**: Requires switching to white mode first (handled automatically)

## Development

### Project Structure

```
custom_components/lampster/
├── __init__.py          # Integration setup
├── manifest.json        # Integration metadata
├── const.py            # Constants
├── config_flow.py      # Discovery and config UI
├── light.py            # Light entity implementation
├── strings.json        # UI strings
└── translations/
    └── en.json         # English translations
```

### Core Library

The integration uses the `lampster` Python library for BLE communication. See the main README for library documentation.

### Testing

1. Enable debug logging (see above)
2. Monitor logs: `tail -f /config/home-assistant.log | grep lampster`
3. Test basic operations: on/off, RGB colors, white temperatures
4. Test automations and scripts
5. Test device reconnection (power cycle device)

## Attribution

All BLE protocol information based on reverse engineering by **[Noki](https://github.com/Noki/the-lampster)**.

## License

MIT License - See LICENSE file for details

## Support

- **Issues**: [GitHub Issues](https://github.com/yamanote1138/lampster-ha-integration/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yamanote1138/lampster-ha-integration/discussions)
- **Protocol Documentation**: [Noki's the-lampster](https://github.com/Noki/the-lampster)
