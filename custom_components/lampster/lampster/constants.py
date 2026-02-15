"""BLE constants for The Lampster.

Protocol documentation: https://github.com/Noki/the-lampster
All characteristic UUIDs and command values are based on Noki's reverse engineering work.
"""

# BLE Service and Characteristic UUIDs
# Discovered via characteristic enumeration on actual device
# Based on handles from Noki's documentation:
#   0x0021 (mode), 0x0025 (white), 0x002a (RGB)
SERVICE_UUID = "01ff5553-ba5e-f4ee-5ca1-eb1e5e4b1ce0"
CHAR_MODE = "01ff5554-ba5e-f4ee-5ca1-eb1e5e4b1ce0"    # Handle 0x0020 (≈ 0x0021)
CHAR_WHITE = "01ff5556-ba5e-f4ee-5ca1-eb1e5e4b1ce0"  # Handle 0x0024 (≈ 0x0025)
CHAR_RGB = "01ff5559-ba5e-f4ee-5ca1-eb1e5e4b1ce0"    # Handle 0x0029 (≈ 0x002a)

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
