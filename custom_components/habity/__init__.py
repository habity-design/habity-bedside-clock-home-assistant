"""Habity integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_USE_SSL, DOMAIN
from .coordinator import HabityCoordinator
from .udp_listener import HA_EVENT_UDP, async_start_udp_listener

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SWITCH, Platform.SENSOR, Platform.TIME]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Habity from a config entry."""
    host = entry.data[CONF_HOST]
    use_ssl = entry.data.get(CONF_USE_SSL, False)

    coordinator = HabityCoordinator(hass, host, use_ssl=use_ssl)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "udp_sensors": {},
    }

    # Start the shared UDP listener only once — reused across all config entries.
    if "stop_udp" not in hass.data[DOMAIN]:
        stop_udp = await async_start_udp_listener(hass, _make_udp_callback(hass))
        hass.data[DOMAIN]["stop_udp"] = stop_udp

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


def _make_udp_callback(hass: HomeAssistant):
    """Return a UDP callback that routes packets to the correct device by source IP."""

    def on_udp_packet(packet: dict, addr: tuple) -> None:
        source_ip = addr[0]
        event_type = packet.get("type")
        state = packet.get("state")

        # Find the entry whose host matches the packet's source IP.
        matched_entry_id = None
        for entry_id, data in hass.data[DOMAIN].items():
            if entry_id == "stop_udp":
                continue
            if data["coordinator"].host == source_ip:
                matched_entry_id = entry_id
                break

        if matched_entry_id is None:
            _LOGGER.debug(
                "Habity UDP packet from unknown device %s — ignoring", source_ip
            )
            return

        coordinator: HabityCoordinator = hass.data[DOMAIN][matched_entry_id]["coordinator"]

        # Handle audio state — pause/resume polling, don't fire as sensor.
        if event_type == "audio":
            coordinator.set_audio_playing(state == "playing")
            return

        # Fire a generic HA event for automations.
        hass.bus.fire(
            HA_EVENT_UDP,
            {
                "type": event_type,
                "state": state,
                "entry_id": matched_entry_id,
                "source_ip": source_ip,
            },
        )

        # Update the matching UDP sensor entity.
        udp_sensors = hass.data[DOMAIN][matched_entry_id].get("udp_sensors", {})
        sensor = udp_sensors.get(event_type)
        if sensor:
            sensor.handle_udp_update(state)

    return on_udp_packet


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # Stop the shared UDP listener only when the last entry is removed.
        remaining = [k for k in hass.data[DOMAIN] if k != "stop_udp"]
        if not remaining:
            stop_udp = hass.data[DOMAIN].pop("stop_udp", None)
            if stop_udp:
                stop_udp()

    return unload_ok
