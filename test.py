import logging

from keyboard_controller import KeyboardController

RED = "FF0000"

logger = logging.getLogger("anubeam")


def main():
    keyboard = KeyboardController(logger)
    result = keyboard.connect()
    if not result:
        logger.error("Keyboard connection failure")
        return

    keyboard.change_color(RED)


if __name__ == "__main__":
    main()
