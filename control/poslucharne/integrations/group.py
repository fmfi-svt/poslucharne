from typing import Generator
from poslucharne.devices import PowerState, Projector
import asyncio


class ProjectorGroup(Projector):
    @property
    def projectors(self) -> Generator[Projector, None, None]:
        for projector in self.config.get("items", []):
            yield self.room.projectors[projector]

    async def get_power(self) -> PowerState:
        states = await asyncio.gather(*[p.get_power() for p in self.projectors])
        for state in states:
            if state in [PowerState.UNKNOWN, PowerState.ON]:
                return state
        return PowerState.OFF

    async def power_on(self) -> None:
        await asyncio.gather(*[p.power_on() for p in self.projectors])

    async def power_off(self) -> None:
        await asyncio.gather(*[p.power_off() for p in self.projectors])

    async def reboot(self) -> None:
        await asyncio.gather(*[p.reboot() for p in self.projectors])

    async def blank(self) -> None:
        await asyncio.gather(*[p.blank() for p in self.projectors])

    async def unblank(self) -> None:
        await asyncio.gather(*[p.unblank() for p in self.projectors])

    async def set_input(self, input: str) -> None:
        await asyncio.gather(*[p.set_input(input) for p in self.projectors])

    async def get_input(self) -> str | None:
        inputs = set(await asyncio.gather(*[p.get_input() for p in self.projectors]))
        if len(inputs) == 1:
            return inputs.pop()
        return None
