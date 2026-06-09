from fastapi import APIRouter, HTTPException

from poslucharne.devices import Screen
from poslucharne.room import Room


def create_router(room: Room) -> APIRouter:
    router = APIRouter(prefix="/screens", tags=["screens"])

    def _get_screen(name: str) -> Screen:
        scr = room.screens.get(name)
        if scr is None:
            raise HTTPException(status_code=404, detail=f"screen {name!r} not found")
        return scr

    @router.get("/")
    def list_screens():
        return list(room.screens)

    @router.get("/{name}/")
    async def screen_status(name: str):
        scr = _get_screen(name)
        position = await scr.get_position()
        return {"name": name, "position": position.name}

    @router.post("/{name}/up/")
    async def screen_up(name: str):
        scr = _get_screen(name)
        await scr.up()
        return {"ok": True}

    @router.post("/{name}/down/")
    async def screen_down(name: str):
        scr = _get_screen(name)
        await scr.down()
        return {"ok": True}

    @router.post("/{name}/stop/")
    async def screen_stop(name: str):
        scr = _get_screen(name)
        await scr.stop()
        return {"ok": True}

    return router
