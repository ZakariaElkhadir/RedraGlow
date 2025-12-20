from logging import Logger

import hid
from hid import HIDException

VENDOR_ID = 0x258a
PRODUCT_ID = 0x0049
USAGE_PAGE = 65280
PACKET_LENGTH = 1032

INTENSITY = b'\x31'  # 30 → 0, 31 → 1, 32 → 2 etc.


class KeyboardController:
    def __init__(self, logger: Logger):
        self.device = None
        self.logger = logger

    def connect(self) -> bool:
        for d in hid.enumerate(VENDOR_ID, PRODUCT_ID):
            if d.get("usage_page") == USAGE_PAGE:
                try:
                    self.device = hid.Device(path=d.get("path"))
                except HIDException as e:
                    self.logger.error(e)
                    return False
                break

        if self.device is None:
            self.logger.error("Keyboard not found")
            return False

        self.logger.info(f"Connected to {self.device.manufacturer} — {self.device.product}")
        return True

    def change_color(self, color: str) -> None:
        packet1 = bytearray()
        packet1.extend(bytes.fromhex(
            "06 08 b8 00 40 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        packet1.extend(bytes.fromhex(color))
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

        packet2 = bytearray()
        packet2.extend(bytes.fromhex(
            "06 03 b6 00 00 00 00 00 00 00 00 00 00 00 5a a5 03 03 00 00 00 01 20 01 00 00 00 00 55 "
            "55 01 00 00 00 00 00 ff ff 00"))
        packet2.extend(INTENSITY)
        packet2.extend(bytes.fromhex(
            "07 33 07 33 07 33 07 33 07 33 07 33 07 33 07 33 07 33 00 33 07 33 07 33 07 33 07 33 07 "
            "33 07 33 07 33 07 33 07 33 5a a5 00 10 07 44 07 44 07 44 07 44 07 44 07 44 07 44 04 04 "
            "04 04 04 04 04 04 04 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
            "00 00 00 00 00 00 00 00 00 00 5a a5 03 03"))

        try:
            self.device.send_feature_report(_pad_packet(packet1))
            self.device.send_feature_report(_pad_packet(packet2))
        except Exception as e:
            self.logger.error("Error sending packet:", e)

    def close(self) -> None:
        self.device.close()


def _pad_packet(data: bytes, length: int = PACKET_LENGTH) -> bytes:
    result = bytearray(data)
    if len(data) < length:
        zeroes = b'\x00' * (length - len(data))
        result.extend(zeroes)
    return bytes(result)
