from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from poslucharne.room import Room


class PowerState(enum.IntEnum):
    UNKNOWN = -1
    OFF = 0
    ON = 1


class Device:
    def __init__(self, name: str, room: Room, **config: Any) -> None:
        self.name = name
        self.room = room
        self.config = config


class PowerableDevice:
    async def get_power(self) -> PowerState:
        raise NotImplementedError()

    async def power_on(self) -> None:
        raise NotImplementedError()

    async def power_off(self) -> None:
        raise NotImplementedError()

    async def reboot(self) -> None:
        await self.power_off()
        await self.power_on()


class Projector(PowerableDevice, Device):
    async def blank(self) -> None:
        raise NotImplementedError()

    async def unblank(self) -> None:
        raise NotImplementedError()

    async def set_input(self, input: str) -> None:
        raise NotImplementedError()

    async def get_input(self) -> str | None:
        raise NotImplementedError()


class Matrix(PowerableDevice, Device):
    async def connect(self, input: str, output: str) -> None:
        raise NotImplementedError()


class ScreenPosition(enum.IntEnum):
    UNKNOWN = -1
    DOWN = 0
    UP = 1


class Screen(Device):
    async def up(self) -> None:
        raise NotImplementedError()

    async def down(self) -> None:
        raise NotImplementedError()

    async def stop(self) -> None:
        raise NotImplementedError()

    async def get_position(self) -> ScreenPosition:
        raise NotImplementedError()
