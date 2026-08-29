"""Switch platform — Alarm enabled/disabled, and the front light (LED + backlight)."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_ALARM_SWITCH, ENTITY_LIGHT_SWITCH
from .coordinator import HabityCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HabityCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([AlarmSwitch(coordinator, entry), LightSwitch(coordinator, entry)])


class AlarmSwitch(CoordinatorEntity, SwitchEntity):
    """Represents the alarm enabled/disabled switch."""

    _attr_name = "Alarm"
    _attr_icon = "mdi:alarm"

    def __init__(self, coordinator: HabityCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_ALARM_SWITCH}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Habity",
            "manufacturer": "Habity",
            "model": "Bedside Clock",
        }

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("alarm_enabled")

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_alarm(alarm_enabled=True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_alarm(alarm_enabled=False)


class LightSwitch(CoordinatorEntity, SwitchEntity):
    """Represents the device's front light (LED + backlight, toggled as one unit).

    Backed by /state's "light_on" field like AlarmSwitch, but that field can
    also change from the physical STOP button between polls -- the UDP
    listener's "light" packets (Habity_HA_SendUDP("light", ...) in
    InputHandler.c) are merged into the coordinator's data as they arrive
    (see HabityCoordinator.set_light_state) so this reflects button presses
    instantly instead of waiting up to POLL_INTERVAL seconds.
    """

    _attr_name = "Light"
    _attr_icon = "mdi:lightbulb"

    def __init__(self, coordinator: HabityCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{ENTITY_LIGHT_SWITCH}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Habity",
            "manufacturer": "Habity",
            "model": "Bedside Clock",
        }

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("light_on")

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_light(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_light(False)
