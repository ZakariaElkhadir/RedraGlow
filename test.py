import logging
import sys

from keyboard_controller import KeyboardController, normalize_color

logger = logging.getLogger("redraglow")


def main():
    color_arg = sys.argv[1] if len(sys.argv) > 1 else "red"
    brightness = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    keyboard = KeyboardController(logger)
    result = keyboard.connect()
    if not result:
        logger.error("Keyboard connection failure")
        return

    try:
        hex_color = normalize_color(color_arg)
        print(f"Applying color {color_arg} (#{hex_color}) with brightness {brightness}...")
        keyboard.change_color(hex_color, brightness=brightness)
        print("Success!")
    finally:
        keyboard.close()


if __name__ == "__main__":
    main()
