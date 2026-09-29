#!/usr/bin/env python3
"""
RedraGlow - Native Linux CLI tool for controlling Redragon & BY Tech RGB mechanical keyboards.
Compatible with vendor ID 0x258a, product ID 0x0049.
"""

import argparse
import logging
import os
import sys

from keyboard_controller import (
    COLOR_NAME_HEX,
    DEFAULT_BRIGHTNESS,
    MAX_BRIGHTNESS,
    MIN_BRIGHTNESS,
    KeyboardController,
    normalize_color,
)

# ANSI terminal colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
GRAY = "\033[90m"


def hex_to_ansi_rgb(hex_code: str) -> str:
    """Return ANSI 24-bit background color escape code for a given hex color."""
    try:
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return f"\033[48;2;{r};{g};{b}m  {RESET}"
    except Exception:
        return "  "


def print_color_palette():
    """Print all available colors with colored swatches."""
    print(f"\n{BOLD}Available Predefined Colors:{RESET}")
    print(f"{GRAY}You can use any of these names OR any custom hex code like #FF5500 or 00FFCC{RESET}\n")

    items = sorted(COLOR_NAME_HEX.items())
    col_width = 24
    num_cols = 3

    for i in range(0, len(items), num_cols):
        row = items[i : i + num_cols]
        line = ""
        for name, hex_val in row:
            swatch = hex_to_ansi_rgb(hex_val)
            entry = f"{swatch} {BOLD}{name:<12}{RESET} {GRAY}#{hex_val}{RESET}"
            line += entry.ljust(col_width + 15)
        print(line)
    print()


def check_status(controller: KeyboardController) -> bool:
    """Check keyboard connection and udev permissions."""
    print(f"\n{BOLD}{CYAN}=== Keyboard Status & Diagnostics ==={RESET}")
    import hid

    from keyboard_controller import PRODUCT_ID, USAGE_PAGE, VENDOR_ID

    devices = [d for d in hid.enumerate(VENDOR_ID, PRODUCT_ID) if d.get("usage_page") == USAGE_PAGE]

    if not devices:
        print(f"[{RED}FAIL{RESET}] No keyboard detected with VID: 0x{VENDOR_ID:04x}, PID: 0x{PRODUCT_ID:04x}")
        print(f"       Make sure the keyboard is connected via USB cable (wired mode).")
        return False

    dev = devices[0]
    raw_path = dev.get("path", b"").decode("utf-8", errors="ignore")
    print(f"[{GREEN}OK{RESET}] Keyboard detected:")
    print(f"     Manufacturer : {dev.get('manufacturer_string')}")
    print(f"     Product      : {dev.get('product_string')}")
    print(f"     HID Path     : {raw_path}")

    # Check permission
    can_open = False
    try:
        h = hid.Device(path=dev.get("path"))
        h.close()
        can_open = True
    except Exception:
        can_open = False

    if can_open:
        print(f"[{GREEN}OK{RESET}] Device read/write permissions: Granted (Ready to control without sudo!)")
    else:
        print(f"[{YELLOW}WARN{RESET}] Device permissions: Restricted ({raw_path})")
        print(f"       You currently need root permissions or udev rules to control the device.")
        print(f"       Run: {BOLD}redraglow --setup-udev{RESET} to fix this.")

    print()
    return can_open


def print_udev_setup():
    """Print the udev setup instructions."""
    print(f"\n{BOLD}{CYAN}=== Setup udev Rules (Run without sudo) ==={RESET}")
    print("Run the following command once in your terminal:\n")
    cmd = (
        'echo \'SUBSYSTEM=="hidraw", ATTRS{idVendor}=="258a", ATTRS{idProduct}=="0049", MODE="0666"\' | '
        "sudo tee /etc/udev/rules.d/99-keyboard.rules && "
        "sudo udevadm control --reload-rules && sudo udevadm trigger"
    )
    print(f"{GREEN}{cmd}{RESET}\n")
    print("After running this command, unplug and plug the keyboard back in (or the trigger will handle it).")
    print("You will then be able to change colors freely without sudo!\n")


def main():
    parser = argparse.ArgumentParser(
        prog="redraglow",
        description="CLI tool to control RGB backlight on BY Tech / Redragon mechanical keyboards.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  redraglow red
  redraglow cyan
  redraglow "#00ffcc" --brightness 3
  redraglow purple -b 2
  redraglow off
  redraglow --list
  redraglow --status
  redraglow --setup-udev
        """,
    )

    parser.add_argument(
        "color",
        nargs="?",
        default=None,
        help="Color name (e.g. red, blue, cyan, purple) or hex code (#FF0000, 00FF88)",
    )
    parser.add_argument(
        "-c",
        "--color",
        dest="opt_color",
        help="Specify color (alternative to positional argument)",
    )
    parser.add_argument(
        "-b",
        "--brightness",
        type=int,
        choices=range(MIN_BRIGHTNESS, MAX_BRIGHTNESS + 1),
        default=DEFAULT_BRIGHTNESS,
        help=f"Brightness level from {MIN_BRIGHTNESS} (off) to {MAX_BRIGHTNESS} (maximum). Default: {DEFAULT_BRIGHTNESS}",
    )
    parser.add_argument(
        "--off",
        action="store_true",
        help="Turn off keyboard backlighting",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all predefined color names with color swatches",
    )
    parser.add_argument(
        "-s",
        "--status",
        action="store_true",
        help="Check keyboard connection and permission status",
    )
    parser.add_argument(
        "--setup-udev",
        action="store_true",
        help="Print udev rules command to allow running without sudo",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed debug logging",
    )

    args = parser.parse_args()

    # Logging setup
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    logger = logging.getLogger("redraglow")

    controller = KeyboardController(logger)

    if args.list:
        print_color_palette()
        return 0

    if args.setup_udev:
        print_udev_setup()
        return 0

    if args.status:
        check_status(controller)
        return 0

    # Determine desired action
    target_color = args.opt_color or args.color

    if args.off or (target_color and target_color.lower() in ["off", "none", "0"]):
        target_color = "black"
        brightness = 0
    else:
        brightness = args.brightness

    if not target_color:
        # If no arguments provided, show short help
        parser.print_help()
        print(f"\n{YELLOW}Hint: Use 'redraglow --list' to see all available colors, or 'redraglow red' to set red.{RESET}\n")
        return 0

    # Validate color
    try:
        hex_code = normalize_color(target_color)
    except ValueError as e:
        print(f"{RED}Error:{RESET} {e}", file=sys.stderr)
        return 1

    # Connect to device
    if not controller.connect():
        print(
            f"\n{RED}Error:{RESET} Failed to connect to keyboard. "
            f"Check if it's connected, or run with sudo, or run {BOLD}redraglow --setup-udev{RESET}.",
            file=sys.stderr,
        )
        return 1

    try:
        swatch = hex_to_ansi_rgb(hex_code)
        if brightness == 0 or hex_code == "000000":
            print(f"Turning keyboard backlight {BOLD}OFF{RESET}...")
        else:
            print(
                f"Setting keyboard backlight to {swatch} {BOLD}#{hex_code}{RESET} "
                f"({target_color}) at brightness {BOLD}{brightness}/{MAX_BRIGHTNESS}{RESET}..."
            )

        controller.change_color(hex_code, brightness=brightness)
        print(f"{GREEN}Done!{RESET}")
        return 0
    except Exception as e:
        print(f"{RED}Error while applying color:{RESET} {e}", file=sys.stderr)
        return 1
    finally:
        controller.close()


if __name__ == "__main__":
    sys.exit(main() or 0)
