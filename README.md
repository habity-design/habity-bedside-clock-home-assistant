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
- ⚡ Instant button press update

---

## Requirements

- Home Assistant 2023.1 or newer
- Habity Bedside Clock connected to your local network

---

## Installation

### Via HACS (recommended)

The integration is not yet in the default HACS store, but you can add it right now as a **custom repository** — this takes about 30 seconds.

**Step 1 — Add the custom repository**

[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=habity-design&repository=habity-bedside-clock-home-assistant&category=integration)

Click the badge above, or do it manually:

1. Open **HACS** in your Home Assistant sidebar
2. Click the **⋮** menu (top right) and select **Custom repositories**
3. Paste this URL: `https://github.com/habity-design/habity-bedside-clock-home-assistant`
4. Set the category to **Integration** and click **Add**

**Step 2 — Install**

1. Search for **Habity** in HACS and click it
2. Click **Download** and confirm
3. Restart Home Assistant


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
