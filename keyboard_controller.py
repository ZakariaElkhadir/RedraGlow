import logging
from logging import Logger
import re
from typing import Optional

import hid
from hid import HIDException

VENDOR_ID = 0x258a
PRODUCT_ID = 0x0049
USAGE_PAGE = 65280
PACKET_LENGTH = 1032
DEFAULT_BRIGHTNESS = 4
MIN_BRIGHTNESS = 0
MAX_BRIGHTNESS = 4

COLOR_NAME_HEX = {
    # Base colors
    "black": "000000",
    "white": "FFFFFF",
    "red": "FF0000",
    "green": "00FF00",
    "blue": "0000FF",
    "yellow": "FFFF00",
    "brown": "A52A2A",

    # White shades
    "ivory": "FFFFF0",
    "snow": "FFFAFA",
    "beige": "F5F5DC",
    "cream": "FFFDD0",
    "pearl": "EAE0C8",

    # Blue shades
    "cyan": "00FFFF",
    "navy": "000080",
    "sky": "87CEEB",
    "azure": "007FFF",
    "teal": "008080",
    "turquoise": "40E0D0",
    "indigo": "4B0082",
    "ice": "A5F2F3",

    # Red/Pink shades
    "magenta": "FF00FF",
    "pink": "FFC0CB",
    "hotpink": "FF69B4",
    "coral": "FF7F50",
    "salmon": "FA8072",
    "crimson": "DC143C",
    "maroon": "800000",

    # Green shades
    "lime": "00FF00",
    "olive": "808000",
    "emerald": "50C878",
    "mint": "98FF98",
    "forest": "228B22",

    # Orange/Yellow shades
    "orange": "FFA500",
    "gold": "FFD700",
    "amber": "FFBF00",
    "warmwhite": "FFD1A4",

    # Purple shades
    "purple": "800080",
    "violet": "EE82EE",
    "lavender": "E6E6FA",
    "plum": "DDA0DD",
}


def normalize_color(color: str) -> str:
    """Resolve a color name or hex code into a 6-character hex string (RRGGBB)."""
    clean = color.strip().lower()
    if clean in COLOR_NAME_HEX:
        return COLOR_NAME_HEX[clean]

    # Strip leading '#'
    if clean.startswith("#"):
        clean = clean[1:]

    # 3-character hex (#RGB -> RRGGBB)
    if len(clean) == 3 and re.fullmatch(r"[0-9a-fA-F]{3}", clean):
        return "".join([c * 2 for c in clean]).upper()

    # 6-character hex
    if len(clean) == 6 and re.fullmatch(r"[0-9a-fA-F]{6}", clean):
        return clean.upper()

    raise ValueError(
        f"Unknown color '{color}'. Use a valid hex code (e.g. #FF5500 or FF5500) "
        f"or one of the known color names: {', '.join(sorted(COLOR_NAME_HEX.keys()))}"
    )


class KeyboardController:
    def __init__(self, logger: Optional[Logger] = None):
        self.device = None
        self.logger = logger or logging.getLogger("redraglow")
        self.current_color = "FFFFFF"
        self.current_brightness = DEFAULT_BRIGHTNESS

    def connect(self) -> bool:
        found_device = False
        device_path = None

        for d in hid.enumerate(VENDOR_ID, PRODUCT_ID):
            if d.get("usage_page") == USAGE_PAGE:
                found_device = True
                device_path = d.get("path")
                try:
                    self.device = hid.Device(path=device_path)
                    break
                except HIDException as e:
                    self.logger.error(
                        f"HIDException when opening {device_path}: {e}\n"
                        "Note: Make sure udev rules are installed (/etc/udev/rules.d/99-keyboard.rules) "
                        "or run with appropriate permissions."
                    )
                    return False

        if not found_device:
            self.logger.error(
                f"Keyboard device (VID=0x{VENDOR_ID:04x}, PID=0x{PRODUCT_ID:04x}, USAGE_PAGE={USAGE_PAGE}) not found"
            )
            return False

        if self.device is None:
            self.logger.error("Failed to initialize HID device handle.")
            return False

        self.logger.info(f"Connected to {self.device.manufacturer} — {self.device.product}")
        return True

    def change_color(self, color: str, brightness: Optional[int] = None) -> None:
        if self.device is None:
            raise RuntimeError("Keyboard device is not connected. Call connect() first.")

        hex_color = normalize_color(color)
        self.current_color = hex_color

        if brightness is not None:
            self.current_brightness = max(MIN_BRIGHTNESS, min(MAX_BRIGHTNESS, int(brightness)))

        intensity_byte = bytes([0x30 + self.current_brightness])

        # Packet 1 sets the color RGB
        packet1 = bytearray()
        packet1.extend(bytes.fromhex(
            "06 08 b8 00 40 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        packet1.extend(bytes.fromhex(hex_color))
        packet1.extend(bytes.fromhex(
            "00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff "
            "00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff "
            "ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff "
            "00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 "
            "ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff "
            "00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 "
            "ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff "
            "ff ff ff ff 00 ff 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 "
            "00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 "
            "ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff "
            "ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 "
            "ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff "
            "00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 "
            "00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff "
            "ff 00 ff 00 ff 00 ff ff ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff "
            "ff ff ff ff 00 00 00 00 ff 00 ff 00 ff ff 00 ff 00 ff 00 ff ff ff ff ff"))

        # Packet 2 sets brightness intensity and mode
        packet2 = bytearray()
        packet2.extend(bytes.fromhex(
            "06 03 b6 00 00 00 00 00 00 00 00 00 00 00 5a a5 03 03 00 00 00 01 20 01 00 00 00 00 55 "
            "55 01 00 00 00 00 00 ff ff 00"))
        packet2.extend(intensity_byte)
        packet2.extend(bytes.fromhex(
            "07 33 07 33 07 33 07 33 07 33 07 33 07 33 07 33 07 33 00 33 07 33 07 33 07 33 07 33 07 "
            "33 07 33 07 33 07 33 07 33 5a a5 00 10 07 44 07 44 07 44 07 44 07 44 07 44 07 44 04 04 "
            "04 04 04 04 04 04 04 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
            "00 00 00 00 00 00 00 00 00 00 5a a5 03 03"))

        try:
            self.device.send_feature_report(_pad_packet(packet1))
            self.device.send_feature_report(_pad_packet(packet2))
        except Exception as e:
            self.logger.error(f"Error sending packet: {e}")

    def set_brightness(self, brightness: int) -> None:
        self.change_color(self.current_color, brightness=brightness)

    def turn_off(self) -> None:
        self.change_color("000000", brightness=0)

    def close(self) -> None:
        if self.device is not None:
            self.device.close()
            self.device = None


def _pad_packet(data: bytes, length: int = PACKET_LENGTH) -> bytes:
    result = bytearray(data)
    if len(data) < length:
        zeroes = b'\x00' * (length - len(data))
        result.extend(zeroes)
    return bytes(result)
