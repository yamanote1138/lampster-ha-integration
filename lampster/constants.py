"""BLE constants for The Lampster.

Protocol documentation: https://github.com/Noki/the-lampster
All characteristic UUIDs and command values are based on Noki's reverse engineering work.
"""

# BLE Service and Characteristic UUIDs
# Note: These are typical UUIDs for devices like this. May need adjustment
# based on actual device enumeration during testing.
SERVICE_UUID = "0000ffe5-0000-1000-8000-00805f9b34fb"
CHAR_MODE = "0000ffe9-0000-1000-8000-00805f9b34fb"  # Characteristic handle 0x0021
CHAR_WHITE = "0000ffea-0000-1000-8000-00805f9b34fb"  # Characteristic handle 0x0025
CHAR_RGB = "0000ffeb-0000-1000-8000-00805f9b34fb"  # Characteristic handle 0x002a

# Mode control commands (written to CHAR_MODE)
MODE_POWER_ON = 0xC0
MODE_POWER_OFF = 0x40
MODE_RGB = 0xA8
MODE_WHITE = 0xC8
MODE_OFF = 0x28

# Value ranges for color control
MIN_VALUE = 0x00  # 0%
MAX_VALUE = 0x64  # 100 in decimal = 100%

# Device identification
DEVICE_NAME_PREFIX = "Lamp"  # Devices typically have "Lamp" in their name
