# Habity Bedside Clock — Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-blue.svg)](https://www.home-assistant.io)

A Home Assistant integration for the [Habity Bedside Clock](https://habity.design), exposing alarm time and button presses via local HTTP & UDP.

---

## Features

- 📡 Local polling — no cloud, no account required
- 🕐 Exposes next alarm time
- ⏰ Set next alarm time
- ⚙️ Toggle next alarm on/off
- 💡 Toggle the nightlight
- ⚡ Instant button press update


🔋 Features that works on battery alone:

To use all features of this integration, the Habity Bedside Clock must be connected to power. On battery alone, the clock disconnects from Wi-Fi to save power and only reconnects briefly to broadcast events such as button presses, active alarms, and the next alarm time.
Sending commands to the clock (for example, toggling the light or changing the alarm time) requires constant power.


---

## Requirements

- Home Assistant 2023.1 or newer
- Habity Bedside Clock connected to your local network

---

## Installation

### Via HACS (recommended)

Available in HACS. Search for "Habity bedside clock" to download.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=habity-design&repository=habity-bedside-clock-home-assistant&category=integration)



### Manual

1. Copy the `custom_components/habity` folder into your `config/custom_components/` directory
2. Restart Home Assistant

---

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Habity**
3. Enter the IP address of your clock
4. Done

---

## Support

Found a bug or have a question? [Open an issue](https://github.com/habity-design/habity-bedside-clock-home-assistant/issues) on GitHub.

Learn more about the Habity Bedside Clock at [habity.design](https://habity.design).
