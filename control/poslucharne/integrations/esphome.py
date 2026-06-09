import logging

import httpx

from poslucharne.devices import Screen, ScreenPosition

logger = logging.getLogger(__name__)


class ESPHomeScreen(Screen):
    async def _set_switch(self, entity_id: str, state: bool) -> None:
        url = f"http://{self.config['address']}/switch/{entity_id}"
        async with httpx.AsyncClient() as client:
            if state:
                resp = await client.post(f"{url}/turn_on", timeout=10)
            else:
                resp = await client.post(f"{url}/turn_off", timeout=10)
            resp.raise_for_status()

    async def _turn_all_off(self) -> None:
        for key in ("up_switch", "down_switch", "stop_switch"):
            await self._set_switch(self.config[key], False)

    async def up(self) -> None:
        await self._turn_all_off()
        await self._set_switch(self.config["up_switch"], True)

    async def down(self) -> None:
        await self._turn_all_off()
        await self._set_switch(self.config["down_switch"], True)

    async def stop(self) -> None:
        await self._turn_all_off()
        if "stop_switch" in self.config:
            await self._set_switch(self.config["stop_switch"], True)

    async def get_position(self) -> ScreenPosition:
        return ScreenPosition.UNKNOWN
