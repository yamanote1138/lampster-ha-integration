"""Light platform for The Lampster integration."""
from __future__ import annotations

import logging
from typing import Any

from .lampster.exceptions import CommandError, ConnectionError as LampsterConnectionError
from .lampster.models import RGBColor, WhiteColor

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LampsterCoordinator

_LOGGER = logging.getLogger(__name__)

# Color temperature range in Kelvin
# Warm white: ~2700K, Cool white: ~6500K
MIN_KELVIN = 2700
MAX_KELVIN = 6500


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up The Lampster light from a config entry."""
    coordinator: LampsterCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([LampsterLight(coordinator)])


class LampsterLight(CoordinatorEntity[LampsterCoordinator], LightEntity):
    """Representation of The Lampster light."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_color_modes = {ColorMode.RGB, ColorMode.COLOR_TEMP}

    def __init__(self, coordinator: LampsterCoordinator) -> None:
        """Initialize the light."""
        super().__init__(coordinator)

        self._attr_unique_id = coordinator.address
        self._address = coordinator.address

        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.address)},
            "name": "Lampster",
            "manufacturer": "The Lampster, the licitatie",
            "model": "LA-2017B",
        }

        # Initialize state from coordinator data
        self._update_from_coordinator()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_from_coordinator()
        super()._handle_coordinator_update()

    def _update_from_coordinator(self) -> None:
        """Update entity state from coordinator data."""
        if not self.coordinator.data:
            return

        state = self.coordinator.data
        self._attr_is_on = state.is_on

        if state.mode == "rgb" and state.rgb_color:
            self._attr_color_mode = ColorMode.RGB
            # Convert 0-100 to 0-255
            self._attr_rgb_color = (
                int(state.rgb_color.red * 2.55),
                int(state.rgb_color.green * 2.55),
                int(state.rgb_color.blue * 2.55),
            )
            # Calculate brightness from RGB
            self._attr_brightness = max(self._attr_rgb_color)

        elif state.mode == "white" and state.white_color:
            self._attr_color_mode = ColorMode.COLOR_TEMP
            # Convert warm/cold ratio to Kelvin
            warm = state.white_color.warm
            cold = state.white_color.cold
            total = warm + cold
            if total > 0:
                # More warm = lower Kelvin (warmer)
                warm_ratio = warm / total
                self._attr_color_temp_kelvin = int(
                    MIN_KELVIN + (1 - warm_ratio) * (MAX_KELVIN - MIN_KELVIN)
                )
                self._attr_brightness = int(total * 2.55)
            else:
                # Default if both zero
                self._attr_color_temp_kelvin = 3500
                self._attr_brightness = 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        try:
            # Handle brightness
            brightness = kwargs.get(ATTR_BRIGHTNESS, self._attr_brightness or 255)

            # Handle RGB color
            if ATTR_RGB_COLOR in kwargs:
                rgb = kwargs[ATTR_RGB_COLOR]

                # Scale RGB by brightness (0-255 to 0-100)
                brightness_factor = brightness / 255
                scaled_r = int((rgb[0] / 255) * 100 * brightness_factor)
                scaled_g = int((rgb[1] / 255) * 100 * brightness_factor)
                scaled_b = int((rgb[2] / 255) * 100 * brightness_factor)

                color = RGBColor(scaled_r, scaled_g, scaled_b)
                await self.coordinator.async_command("set_rgb_color", color)

            # Handle color temperature
            elif ATTR_COLOR_TEMP_KELVIN in kwargs:
                kelvin = kwargs[ATTR_COLOR_TEMP_KELVIN]

                # Convert Kelvin to warm/cold ratio
                # Lower Kelvin = warmer = more warm LED
                kelvin_range = MAX_KELVIN - MIN_KELVIN
                warm_ratio = 1 - ((kelvin - MIN_KELVIN) / kelvin_range)

                # Scale by brightness (0-255 to 0-100)
                brightness_0_100 = int((brightness / 255) * 100)
                warm = int(warm_ratio * brightness_0_100)
                cold = int((1 - warm_ratio) * brightness_0_100)

                color = WhiteColor(warm, cold)
                await self.coordinator.async_command("set_white_color", color)

            # Just brightness change on existing color
            elif ATTR_BRIGHTNESS in kwargs and self._attr_color_mode:
                if self._attr_color_mode == ColorMode.RGB:
                    # Reapply RGB with new brightness
                    brightness_factor = brightness / 255
                    scaled_r = int((self._attr_rgb_color[0] / 255) * 100 * brightness_factor)
                    scaled_g = int((self._attr_rgb_color[1] / 255) * 100 * brightness_factor)
                    scaled_b = int((self._attr_rgb_color[2] / 255) * 100 * brightness_factor)

                    color = RGBColor(scaled_r, scaled_g, scaled_b)
                    await self.coordinator.async_command("set_rgb_color", color)
                else:
                    # Reapply white with new brightness
                    kelvin = self._attr_color_temp_kelvin or 3500
                    kelvin_range = MAX_KELVIN - MIN_KELVIN
                    warm_ratio = 1 - ((kelvin - MIN_KELVIN) / kelvin_range)

                    brightness_0_100 = int((brightness / 255) * 100)
                    warm = int(warm_ratio * brightness_0_100)
                    cold = int((1 - warm_ratio) * brightness_0_100)

                    color = WhiteColor(warm, cold)
                    await self.coordinator.async_command("set_white_color", color)

            # No specific attributes, just turn on with last known settings
            else:
                if not self._attr_is_on:
                    await self.coordinator.async_command("power_on")

        except (CommandError, LampsterConnectionError, Exception) as err:
            _LOGGER.error("Failed to turn on light: %s", err)
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        try:
            await self.coordinator.async_command("power_off")

        except (CommandError, LampsterConnectionError, Exception) as err:
            _LOGGER.error("Failed to turn off light: %s", err)
            raise
