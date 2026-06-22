"""Update platform for Habity firmware."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HabityCoordinator

SCAN_INTERVAL = timedelta(hours=6)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Habity firmware update entity."""
    coordinator: HabityCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([HabityFirmwareUpdate(coordinator, entry)])


class HabityFirmwareUpdate(UpdateEntity):
    """Represent Habity firmware update availability."""

    _attr_name = "Firmware"
    _attr_title = "Habity Firmware"
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.PROGRESS

    def __init__(self, coordinator: HabityCoordinator, entry: ConfigEntry) -> None:
        """Initialize the firmware update entity."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_firmware_update"
        self._status: dict = {}

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Habity",
            "manufacturer": "Habity",
            "model": "Bedside Clock",
        }

    @property
    def installed_version(self) -> str | None:
        """Return the installed firmware version."""
        return self._status.get("current")

    @property
    def latest_version(self) -> str | None:
        """Return the latest available firmware version."""
        return self._status.get("remote") or self._status.get("current")

    @property
    def in_progress(self) -> bool | None:
        """Return whether an update process is currently active."""
        busy = self._status.get("busy")
        return bool(busy) if busy is not None else None

    @property
    def update_percentage(self) -> int | None:
        """Return update progress percentage."""
        progress = self._status.get("progress")
        return int(progress) if progress is not None else None

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional OTA status details."""
        return {
            "phase": self._status.get("phase"),
            "ok": self._status.get("ok"),
            "message": self._status.get("msg"),
            "downloaded": self._status.get("downloaded"),
            "total": self._status.get("total"),
            "update_available": self._status.get("update_available"),
        }

    def version_is_newer(self, latest_version: str, installed_version: str) -> bool:
        """Return True if the device reports that an update is available."""
        return bool(self._status.get("update_available"))

    async def async_update(self) -> None:
        """Check for OTA updates and fetch OTA status."""
        await self.coordinator.async_check_ota()
        self._status = await self.coordinator.async_get_ota_status()
