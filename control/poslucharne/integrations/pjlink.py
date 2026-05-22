import asyncio
from poslucharne.devices import PowerState, Projector
from aiopjlink import PJLink, PJLinkERR3, Power, Sources
import logging

logger = logging.getLogger(__name__)


class PjlinkProjector(Projector):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.link = PJLink(
            address=self.config.get("address"),
            port=self.config.get("port", 4352),
            password=self.config.get("password"),
        )

    INPUT_MAPPING = {
        "VGA1": (Sources.Mode.RGB, "1"),
        "VGA2": (Sources.Mode.RGB, "2"),
        "VIDEO": (Sources.Mode.VIDEO, "1"),
        "HDMI1": (Sources.Mode.DIGITAL, "2"),
        "HDMI2": (Sources.Mode.DIGITAL, "3"),
        "USB": (Sources.Mode.STORAGE, "1"),
        "LAN": (Sources.Mode.NETWORK, "2"),
    }

    async def get_power(self) -> PowerState:
        async with self.link as conn:
            try:
                state = await conn.power.get()
            except PJLinkERR3:  # unavailable
                logger.debug("received ERR3 from projector")
                return PowerState.UNKNOWN

            if state in [Power.State.OFF, Power.State.COOLING]:
                return PowerState.OFF
            if state in [Power.State.ON, Power.State.WARMING]:
                return PowerState.ON
            return PowerState.UNKNOWN

    async def _wait_for_power(self, desired_state: Power.State):
        async with self.link as conn:
            for _ in range(90):
                try:
                    power = await conn.power.get()
                    logger.debug(f"projector state: {power}")
                    if power == desired_state:
                        return
                except PJLinkERR3:  # unavailable
                    logger.debug("received ERR3 from projector")

                await asyncio.sleep(1)
        raise TimeoutError("timeouted waiting for power transition")

    async def power_off(self) -> None:
        async with self.link as conn:
            await conn.power.turn_off()
        await self._wait_for_power(Power.State.OFF)

    async def power_on(self) -> None:
        async with self.link as conn:
            await conn.power.turn_on()
        await self._wait_for_power(Power.State.ON)

    async def blank(self) -> None:
        try:
            async with self.link as conn:
                await conn.mute.both(True)
        except PJLinkERR3:
            pass

    async def unblank(self) -> None:
        try:
            async with self.link as conn:
                await conn.mute.both(False)
        except PJLinkERR3:
            pass

    async def set_input(self, input: str) -> None:
        if input.upper() not in self.INPUT_MAPPING:
            raise ValueError(f"unknown input {input}")
        mode, index = self.INPUT_MAPPING[input]

        try:
            async with self.link as conn:
                await conn.sources.set(mode, index)
        except PJLinkERR3:
            pass

    async def get_input(self) -> str | None:
        try:
            async with self.link as conn:
                mode_index = await conn.sources.get()
        except PJLinkERR3:
            return None

        for input_name, input_mode_index in self.INPUT_MAPPING.items():
            if mode_index == input_mode_index:
                return input_name

        logger.warning(f"unknown projector input: {mode_index}")
        return None
