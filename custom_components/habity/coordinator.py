"""REST polling coordinator for Habity."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)


class HabityCoordinator(DataUpdateCoordinator):
    """Polls GET /state every 30 seconds."""

    def __init__(self, hass: HomeAssistant, host: str, use_ssl: bool = False) -> None:
        self.host = host
        self._scheme = "https" if use_ssl else "http"
        self._audio_playing: bool = False
        # verify_ssl=False is required for ESP32 self-signed certificates
        self._session = async_get_clientsession(hass, verify_ssl=False)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=POLL_INTERVAL),
        )

    def set_audio_playing(self, playing: bool) -> None:
        """Called by the UDP listener to pause/resume polling."""
        self._audio_playing = playing
        if playing:
            _LOGGER.debug("Habity: audio playing, polling paused")
        else:
            _LOGGER.debug("Habity: audio stopped, polling resumed")

    async def _async_update_data(self) -> dict:
        if self._audio_playing:
            _LOGGER.debug("Habity: skipping poll, audio is playing")
            return self.data  # Return cached data, no network call

        url = f"{self._scheme}://{self.host}/state"
        try:
            async with self._session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with Habity at {self.host}: {err}") from err

    async def async_set_alarm(self, alarm_enabled: bool | None = None, next_alarm: str | None = None) -> None:
        """POST /alarm to update alarm state on the device."""
        payload: dict = {}
        if alarm_enabled is not None:
            payload["alarm_enabled"] = alarm_enabled
        if next_alarm is not None:
            payload["next_alarm"] = next_alarm

        url = f"{self._scheme}://{self.host}/alarm"
        try:
            async with self._session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                resp.raise_for_status()
                updated = await resp.json()
                self.async_set_updated_data(updated)
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to POST /alarm to Habity: %s", err)

    async def async_set_light(self, light_on: bool) -> None:
        """POST /light to control the front light (LED + backlight) on the device."""
        url = f"{self._scheme}://{self.host}/light"
        try:
            async with self._session.post(
                url,
                json={"light_on": light_on},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                resp.raise_for_status()
                updated = await resp.json()
                self.async_set_updated_data(updated)
        except aiohttp.ClientError as err:
            _LOGGER.error("Failed to POST /light to Habity: %s", err)

    def set_light_state(self, light_on: bool) -> None:
        """Called by the UDP listener when the physical STOP button toggles the light.

        Merges into the coordinator's cached data (same "light_on" key /state
        returns) so LightSwitch updates instantly instead of waiting for the
        next 30s poll — mirrors how async_set_alarm's POST response updates it.
        """
        if self.data is None:
            return
        self.async_set_updated_data({**self.data, "light_on": light_on})
