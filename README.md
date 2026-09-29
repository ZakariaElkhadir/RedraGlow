# RedraGlow

<p align="center">
  <b>A native, lightweight Linux RGB backlight CLI controller & automation suite for Redragon Anubis K539 and BY Tech mechanical keyboards.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Linux-FCC624?style=flat&logo=linux&logoColor=black" alt="Platform Linux" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Protocol-Raw%20USB%20HID-blue" alt="USB HID" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License MIT" />
</p>

---

## 💡 The Story & Motivation

Most mechanical keyboards on the market—such as the **Redragon Anubis K539-RGB** (and other boards powered by the **BY Tech `0x258a:0x0049`** microcontroller)—only offer proprietary, Windows-only configuration software. For Linux users, there is zero official software support.

Rather than booting into Windows, running slow virtual machines, or struggling with wine wrappers, **RedraGlow** bypasses the manufacturer software entirely by reverse-engineering the raw USB HID protocol.

**RedraGlow** provides:
1. **`redraglow` CLI**: A fast, zero-dependency, standalone CLI tool to instantly switch RGB colors, adjust brightness, or toggle lights right from your terminal.
2. **GNOME Integration**: An optional background service and GNOME Shell extension that reactively changes your keyboard backlight when switching input languages (e.g. White for English, Red for your secondary layout).

---

## ✨ Features

- ⚡ **Instant CLI Control**: Switch colors or brightness in milliseconds (`redraglow cyan`, `redraglow "#FF5500" -b 3`).
- 🎨 **35+ Built-in Color Presets**: Includes named presets (`red`, `cyan`, `gold`, `mint`, `ice`, `lavender`, `emerald`, etc.) and full support for any `#RRGGBB` or `RRGGBB` hex code.
- ☀️ **5-Level Brightness Control**: Easily fine-tune brightness from `0` (off) to `4` (maximum).
- 🖥️ **Interactive Terminal Preview**: View all available presets with real 24-bit truecolor ANSI swatches using `redraglow --list`.
- 🔒 **One-Step Rootless Setup**: Configure `udev` permissions in seconds with `redraglow --setup-udev`—no root/sudo needed during daily use.
- 🩺 **Hardware Diagnostics**: Quickly verify connection status, HID paths, and device permissions with `redraglow --status`.
- 🌐 **GNOME Input Source Synchronization**: Automatically shift backlight colors according to the active input layout.

---

## ⌨️ Hardware Compatibility

Tested and compatible with mechanical keyboards utilizing the BY Tech USB microcontroller:

| Property | Value |
| :--- | :--- |
| **Vendor ID (VID)** | `0x258a` (BY Tech) |
| **Product ID (PID)** | `0x0049` |
| **Usage Page** | `65280` (`0xFF00`) |
| **Confirmed Models** | Redragon Anubis K539-RGB (Wired USB Mode) |
| **Connection** | Wired USB (Bluetooth / 2.4GHz dongle modes use different protocol layers) |

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/ZakariaElkhadir/RedraGlow.git
cd RedraGlow

# Install required Python packages
pip install -r requirements.txt
```

### 2. Configure udev Rules (Run Without Root)

Run the built-in setup helper to grant non-root access to the keyboard:

```bash
python3 redraglow.py --setup-udev
```

Or run the one-liner directly:

```bash
echo 'SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="0049", MODE="0666"' | sudo tee /etc/udev/rules.d/99-keyboard.rules && sudo udevadm control --reload-rules && sudo udevadm trigger
```

*Unplug and re-plug the keyboard once to apply.*

### 3. (Optional) Install `redraglow` to PATH

To run `redraglow` from anywhere in your terminal:

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/redraglow.py" ~/.local/bin/redraglow
chmod +x redraglow.py
```

*(Ensure `~/.local/bin` is in your `$PATH`)*

---

## 🛠️ CLI Usage Examples

```bash
# Set a predefined color
redraglow cyan
redraglow emerald
redraglow purple

# Set a custom HEX color
redraglow "#FF5500"
redraglow 00FFCC

# Set color with custom brightness (0 = off, 4 = max)
redraglow gold --brightness 2
redraglow red -b 1

# Turn off backlight completely
redraglow off
redraglow --off

# List all color presets with terminal swatches
redraglow --list

# Check keyboard connection & permission status
redraglow --status
```

---

## 🎨 Color Palette Preview

Run `redraglow --list` to display all predefined colors with truecolor swatches directly in your terminal:

| Base Colors | Blue / Cyan Shades | Green Shades | Warm / Purple Shades |
| :--- | :--- | :--- | :--- |
| `white` (`#FFFFFF`) | `cyan` (`#00FFFF`) | `green` (`#00FF00`) | `orange` (`#FFA500`) |
| `black` (`#000000`) | `sky` (`#87CEEB`) | `emerald` (`#50C878`)| `gold` (`#FFD700`) |
| `red` (`#FF0000`) | `azure` (`#007FFF`) | `mint` (`#98FF98`) | `amber` (`#FFBF00`) |
| `yellow` (`#FFFF00`) | `teal` (`#008080`) | `lime` (`#00FF00`) | `coral` (`#FF7F50`) |
| `blue` (`#0000FF`) | `ice` (`#A5F2F3`) | `forest` (`#228B22`) | `purple` (`#800080`) |
| `ivory` (`#FFFFF0`) | `navy` (`#000080`) | `olive` (`#808000`) | `lavender` (`#E6E6FA`)|

---

## 🔄 Automated GNOME Layout Indicator

If you want the keyboard backlight to dynamically indicate your active typing language (e.g., White for English, Red for Arabic or Russian):

1. **Install the GNOME Extension**:
   ```bash
   cp -r input-source-monitor@eshfield ~/.local/share/gnome-shell/extensions/
   ```
2. Restart GNOME Shell (or log out and back in) and enable it:
   ```bash
   gnome-extensions enable input-source-monitor@eshfield
   ```
3. Run the monitor daemon:
   ```bash
   python3 main.py
   ```

---

## 🔬 How It Works (Protocol Reverse Engineering)

The tool communicates directly with Linux hidraw devices (`/dev/hidraw*`) using the standard `hidapi` library:

1. **Device Discovery**: Scans connected USB HID devices matching `VID 0x258a`, `PID 0x0049`, and vendor usage page `65280` (`0xFF00`).
2. **Feature Reports**:
   - **Packet 1 (Color)**: A 1032-byte padded feature report containing the RGB byte sequence mapped to the LED controller matrix.
   - **Packet 2 (Brightness & Mode)**: A 1032-byte report configuring the intensity byte (`0x30` to `0x34`) and lighting profile.

---

## 📜 Credits & Acknowledgments

- **Zakaria Elkhadir**: Extended CLI architecture, `redraglow` tool, color normalization engine, brightness adjustment, udev diagnostic helper, and project modernization.
- **Henry Eshfield**: Original USB HID packet capture research and GNOME input-source D-Bus extension ([Anubeam](https://github.com/eshfield/Anubeam)).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
