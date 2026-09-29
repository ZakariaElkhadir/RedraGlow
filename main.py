import asyncio
import logging
import sys
from typing import Optional

from dbus_fast import DBusError
from dbus_fast.aio import MessageBus, ProxyInterface

from keyboard_controller import KeyboardController

START_TIMEOUT_SECONDS = 10

BUS_NAME = "org.gnome.InputSourceMonitor"
BUS_PATH = "/org/gnome/InputSourceMonitor"

RED = "FF0000"
WHITE = "FFFFFF"
COLORS = {
    "us": WHITE,
    "ru": RED,
}

logger = logging.getLogger("redraglow")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)


async def wait_for_input_source_interface(bus: MessageBus) -> Optional[ProxyInterface]:
    for i in range(1, START_TIMEOUT_SECONDS + 1):
        try:
            introspection = await bus.introspect(BUS_NAME, BUS_PATH)
            proxy = bus.get_proxy_object(BUS_NAME, BUS_PATH, introspection)
            logger.info("Connected to D-Bus")
            return proxy.get_interface(BUS_NAME)
        except DBusError:
            logger.info(f"Try #{i}: DBus service is not ready, retrying")
            await asyncio.sleep(1)

    return None


async def main():
    keyboard: Optional[KeyboardController] = None
    bus: Optional[MessageBus] = None

    try:
        keyboard = KeyboardController(logger)
        if not keyboard.connect():
            logger.error("Keyboard connection failure")
            return

        bus = await MessageBus().connect()

        interface = await wait_for_input_source_interface(bus)
        if interface is None:
            logger.error(f"D-Bus service is not available after {START_TIMEOUT_SECONDS} seconds")
            return

        last_source: dict[str, Optional[str]] = {"value": None}

        def handle_source_change(source: str) -> None:
            if source == last_source["value"]:
                return

            last_source["value"] = source
            color = COLORS.get(source)
            if not color:
                logger.warning(f"Unexpected input source: {source}")
                return

            keyboard.change_color(color)

        interface.on_source_changed(handle_source_change)  # type: ignore

        logger.info("Listening for input source changes. Press Ctrl+C to exit")
        await asyncio.Future()
    except DBusError as e:
        logger.error(f"D-Bus error: {e}")
    except asyncio.CancelledError:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    finally:
        if keyboard is not None:
            keyboard.close()
        if bus is not None:
            bus.disconnect()
        logger.info("Exit")


if __name__ == "__main__":
    asyncio.run(main())
