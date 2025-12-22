# Anubeam

### Redragon Anubis keyboard (K539-RGB) input sources backlight indicator for Fedora/Ubuntu

Tested with Fedora 43 (GNOME 49) and Ubuntu 24.04 (GNOME 46), Python 3.13.9

Works only with a wired (USB) connection. Bluetooth and 2.4G receiver modes are not supported due to limitations of the
keyboard PC software.

See this [Habr article](https://habr.com/ru/articles/979382/) for a detailed installation and configuration guide

## Idea

A GNOME extension detects input source changes and exposes them over D-Bus so a Python script can adjust the keyboard
backlight

### 1. GNOME Extension (`input-source-monitor@eshfield`)

- Listens for input source changes in GNOME Shell
- Emits a D-Bus signal `SourceChanged` with the current layout ID (e.g. `us`, `ru`)

### 2. D-Bus Interface (`org.gnome.InputSourceMonitor`)

- Provides a communication channel between the GNOME Shell and user-space applications
- The Python script subscribes to these signals to react instantly when the layout changes

### 3. Python Script

- Runs continuously in the user session
- Connects to D-Bus and listens for `SourceChanged` signals
- Maps each layout ID to a color (e.g. white for English, red for Russian)
- Sends HID commands directly to the keyboard to change the backlight color

Together, these components form a fully automated system: **Keyboard layout changes** → **GNOME extension detects it** →
**D-Bus broadcasts it** → **Python service updates the keyboard light**

***

## Installation

### Step I: Install Input Source Monitor GNOME extension

This extension listens for changes in the current keyboard input source and broadcasts these events through
a custom D-Bus interface

1. Copy the directory `input-source-monitor@eshfield` to (create `extensions` folder if needed):

```
~/.local/share/gnome-shell/extensions/
```

2. Restart GNOME Shell (log out and back in)


3. Enable the extension:

```
gnome-extensions enable input-source-monitor@eshfield
```

### Step II: Set up udev Rules

To allow your script to control the keyboard device without root privileges, configure the proper udev permissions

1. Create a new udev rules file:

```
sudo nano /etc/udev/rules.d/99-keyboard.rules
```

2. Add the following rule:

> Note: The `idVendor`/`idProduct` values below correspond to the keyboard in wired USB mode

```
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="0049", MODE="0666"
```

3. Reload udev and apply the new rule:

```
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Step III: Install Python Dependencies

1. Install a Python version and create a new virtual environment. I recommend
   using [pyenv](https://github.com/pyenv/pyenv): installation steps A-D

```
pyenv install 3.13.9
pyenv virtualenv 3.13.9 anubeam-3.13.9
```

2. Navigate to project folder, activate created virtual environment and install required packages:

```
pip install -r requirements.txt
```

3. Package `hid` [requires](https://pypi.org/project/hid/) `hidapi` library. Fedora 43 has it already, on Ubuntu you
   need to install it manually:

```
sudo apt install libhidapi-hidraw0 -y
```

### Step IV: Add the Python Script to GNOME Session Startup

To make sure the keyboard light controller starts automatically with your desktop session, create a `.desktop` file:

```
mkdir -p ~/.config/autostart
nano ~/.config/autostart/anubeam.desktop
```

Add the following content (adjust paths to match your environment):

```
[Desktop Entry]
Type=Application
Name=Anubeam
Exec=systemd-cat -t anubeam <ABSOLUTE_PATH_TO_PYTHON_BIN> <ABSOLUTE_PATH_TO_MAIN_PY_FILE>
X-GNOME-Autostart-enabled=true
NoDisplay=false
Comment=Keyboard light controller
```

Log out and log back into the GNOME session, and you are done! The Anubeam Python script will now start automatically
when you log in. It will listen for keyboard layout changes over D-Bus and adjust the backlight color accordingly.

Logs can be viewed with:

```
journalctl --user -t anubeam
```

***

## Bytes Packets Structure Overview

To change the keyboard backlight, you need to send two packets, each 1032 bytes long (padded with zeroes after the
following structure)

### Packet 1

```
06 08 b8 00 40 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 __ __ __ 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff 00 ff 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff
```

`__ __ __` — light color values, e.g. `ff 00 00` for red

### Packet 2

```
06 03 b6 00 00 00 00 00 00 00 00 00 00 00 5a a5 03 03 00 00 00 01 20 01 00 00 00 00 55 55 01 00 00 00 00 00 ff ff 00 __ 07 33 07 33 07 33 07 33 07 33 07 33 07 33 07 33 07 33 00 33 07 33 07 33 07 33 07 33 07 33 07 33 07 33 07 33 07 33 5a a5 00 10 07 44 07 44 07 44 07 44 07 44 07 44 07 44 04 04 04 04 04 04 04 04 04 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 5a a5 03 03
```

`__` — light intensity values:

- `30` → off
- `31` → level 1
- `32` → level 2
- `33` → level 3
- `34` → level 4
