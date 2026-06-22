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

    async def async_get_ota_status(self) -> dict:
        """GET /api/ota/status to retrieve firmware update state."""
        url = f"{self._scheme}://{self.host}/api/ota/status"

        try:
            async with self._session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(
                f"Error retrieving Habity OTA status from {self.host}: {err}"
            ) from err

    async def async_check_ota(self) -> None:
        """GET /api/ota/check to trigger an update check."""
        url = f"{self._scheme}://{self.host}/api/ota/check"

        try:
            async with self._session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()
        except aiohttp.ClientError as err:
            raise UpdateFailed(
                f"Error checking Habity OTA updates from {self.host}: {err}"
            ) from err
