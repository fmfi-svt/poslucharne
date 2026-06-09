import argparse
import asyncio
import os
from pathlib import Path
import struct
import sys
import yaml
from typing import Any

import httpx
import fcntl
from loguru import logger

INPUT_EVENT_STRUCT = struct.Struct("llHHi")  # (sec, usec, type, code, value)
EV_KEY = 0x01
VALUE_KEY_DOWN = 1
EVIOCGRAB = 0x40044590


def load_config(config_path: Path) -> dict:
    with config_path.open("rb") as f:
        return yaml.safe_load(f)


async def execute_actions(actions: list[dict[str, Any]]) -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        for action in actions:
            try:
                logger.debug(f"Sending request {action}.")
                resp = await client.request(
                    action.get("method", "GET").upper(),
                    action.get("url", ""),
                    json=action.get("json", None),
                )
                resp.raise_for_status()
            except httpx.HTTPError as e:
                logger.error(f"Error while executing request {action}: {e}")
        logger.debug("Success.")


async def _run(config_path: Path) -> None:
    config = load_config(config_path)

    device_path: str = config["device"]
    raw_bindings: list[dict[str, Any]] = config.get("bindings", [])
    bindings: dict[str, list[dict[str, Any]]] = {
        b.get("keycode", ""): b.get("actions", []) for b in raw_bindings
    }

    fd = os.open(device_path, os.O_RDONLY | os.O_NONBLOCK)
    fcntl.ioctl(fd, EVIOCGRAB, 1)

    event_size = INPUT_EVENT_STRUCT.size

    try:
        while True:
            try:
                data = os.read(fd, event_size * 64)
            except BlockingIOError:
                await asyncio.sleep(0.1)
                continue
            except OSError as e:
                logger.error(f"Read error: {e}")
                break

            for offset in range(0, len(data) - event_size + 1, event_size):
                _, _, ev_type, code, value = INPUT_EVENT_STRUCT.unpack_from(
                    data, offset
                )

                if ev_type != EV_KEY:
                    continue

                if value != VALUE_KEY_DOWN:
                    continue

                if code not in bindings:
                    logger.debug(f"Unknown keycode {code}")
                    continue

                logger.info(f"Executing actions for {code}.")
                asyncio.create_task(execute_actions(bindings[code]))
    finally:
        fcntl.ioctl(fd, EVIOCGRAB, 0)
        os.close(fd)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.yml"),
        help="Path to config file (default: config.yml)",
    )
    parser.add_argument("--debug", action="store_true", help="Print debug information.")
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stderr, level="DEBUG" if args.debug else "INFO")

    asyncio.run(_run(args.config))


if __name__ == "__main__":
    main()
