"""Time platform — alarm time."""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_ALARM_TIME
from .coordinator import HabityCoordinator


def _device_info(entry: ConfigEntry) -> dict:
    """Return device information for Habity entities."""
    return {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": "Habity",
        "manufacturer": "Habity",
        "model": "Bedside Clock",
    }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Habity alarm time entity."""
    coordinator: HabityCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([HabityAlarmTime(coordinator, entry)])


class HabityAlarmTime(CoordinatorEntity, TimeEntity):
    """Represent the next scheduled Habity alarm time."""

    _attr_name = "Alarm Time"
    _attr_icon = "mdi:clock-time-eight-outline"

    def __init__(self, coordinator: HabityCoordinator, entry: ConfigEntry) -> None:
        """Initialize the alarm time entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_ALARM_TIME}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> time | None:
        """Return the configured alarm time."""
        if self.coordinator.data is None:
            return None

        next_alarm = self.coordinator.data.get("next_alarm")
        if not next_alarm:
            return None

        try:
            hour, minute = next_alarm.split(":")[:2]
            return time(hour=int(hour), minute=int(minute))
        except (TypeError, ValueError):
            return None

    async def async_set_value(self, value: time) -> None:
        """Set the alarm time on the device."""
        await self.coordinator.async_set_alarm(next_alarm=value.strftime("%H:%M"))
