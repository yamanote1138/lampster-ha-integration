{% if installed %}
## Changes in version {{version}}

{% if version_installed.replace("v", "").replace(".","") | int < 100  %}
### 🎉 Welcome to v1.0.0!

This is the first stable release of The Lampster integration with Home Assistant best practices:

- ✅ **Robust BLE Connection** - Uses bleak-retry-connector with 10s timeout
- ✅ **Automatic State Polling** - Detects manual button presses every 30 seconds
- ✅ **Coordinator Pattern** - Proper HA Bluetooth integration architecture
- ✅ **Full Color Control** - RGB colors and color temperature (2700K-6500K)
- ✅ **Brightness Control** - Smooth brightness adjustment
- ✅ **Auto-Discovery** - Device appears automatically when powered on

{% endif %}
{% endif %}

## About

Control your Lampster RGB Bluetooth lamp (Model: LA-2017B) directly from Home Assistant.

### Features

- 🎨 **RGB Color Picker** - Choose any color
- 🌡️ **Color Temperature** - Warm white (2700K) to cool white (6500K)
- 💡 **Brightness** - Adjust light intensity 0-100%
- 🔵 **Auto-Discovery** - Automatically finds your Lampster
- ⏱️ **Manual Button Detection** - Syncs when you use the physical button
- 📊 **Device Info** - Shows model and manufacturer in device page

### Supported Devices

- The Lampster (Model: LA-2017B)
- Hardware Revision: 100B
- Firmware: 10

### Requirements

- Home Assistant 2023.1 or newer
- Bluetooth adapter with BLE support (built-in or USB dongle)
- Lampster within Bluetooth range (~10m)

### Setup

After installation:

1. Go to **Settings** → **Devices & Services**
2. If auto-discovery worked, click **Configure** on the discovered Lampster
3. If not, click **Add Integration** and search for "Lampster"
4. Select your device from the list
5. The light entity will be added: `light.lampster`

### Usage

Control the light like any other HA light:

- Use the light controls in the UI
- Create automations with color/brightness changes
- Use with voice assistants (Alexa, Google Home, Siri via HomeKit)
- Include in scenes and scripts

### Known Limitations

- Only one Bluetooth connection at a time (close official app if connected)
- Physical button is disabled when controlled via Bluetooth
- ~10m range depending on environment
- Manual button press detection has 30-second polling delay

### Support

- **Issues**: [GitHub Issues](https://github.com/yamanote1138/lampster-ha-integration/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yamanote1138/lampster-ha-integration/discussions)

### Credits

Protocol documentation based on reverse engineering by [Noki](https://github.com/Noki/the-lampster).
