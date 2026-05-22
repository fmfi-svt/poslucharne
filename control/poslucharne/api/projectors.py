from fastapi import APIRouter, HTTPException

from poslucharne.devices import Projector
from poslucharne.room import Room
from pydantic import BaseModel


def create_router(room: Room) -> APIRouter:
    router = APIRouter(prefix="/projectors", tags=["projectors"])

    def _get_projector(name: str) -> Projector:
        proj = room.projectors.get(name)
        if proj is None:
            raise HTTPException(status_code=404, detail=f"projector {name!r} not found")
        return proj

    @router.get("/")
    def list_projectors():
        return list(room.projectors)

    @router.get("/{name}/")
    async def projector_status(name: str):
        proj = _get_projector(name)
        power = await proj.get_power()
        input_ = await proj.get_input()
        return {"name": name, "power": power.name, "input": input_}

    @router.post("/{name}/power_on/")
    async def projector_power_on(name: str):
        proj = _get_projector(name)
        await proj.power_on()
        return {"ok": True}

    @router.post("/{name}/power_off/")
    async def projector_power_off(name: str):
        proj = _get_projector(name)
        await proj.power_off()
        return {"ok": True}

    @router.post("/{name}/blank/")
    async def projector_blank(name: str):
        proj = _get_projector(name)
        await proj.blank()
        return {"ok": True}

    @router.post("/{name}/unblank/")
    async def projector_unblank(name: str):
        proj = _get_projector(name)
        await proj.unblank()
        return {"ok": True}

    @router.post("/{name}/reboot/")
    async def projector_reboot(name: str):
        proj = _get_projector(name)
        await proj.reboot()
        return {"ok": True}

    class SetInputRequest(BaseModel):
        input: str

    @router.post("/{name}/input/")
    async def projector_set_input(name: str, body: SetInputRequest):
        proj = _get_projector(name)
        await proj.set_input(body.input)
        return {"ok": True}

    return router
