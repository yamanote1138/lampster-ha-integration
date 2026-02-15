"""Exceptions for The Lampster library."""


class LampsterException(Exception):
    """Base exception for Lampster errors."""

    pass


class ConnectionError(LampsterException):
    """Failed to connect to device."""

    pass


class CommandError(LampsterException):
    """Failed to send command to device."""

    pass


class DiscoveryError(LampsterException):
    """Failed to discover device."""

    pass
