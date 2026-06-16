from fastapi import APIRouter, HTTPException

from poslucharne.devices import Matrix
from poslucharne.room import Room
from pydantic import BaseModel


def create_router(room: Room) -> APIRouter:
    router = APIRouter(prefix="/matrixes", tags=["matrixes"])

    def _get_matrix(name: str) -> Matrix:
        mat = room.matrixes.get(name)
        if mat is None:
            raise HTTPException(status_code=404, detail=f"matrix {name!r} not found")
        return mat

    @router.get("/")
    def list_matrixes():
        return list(room.matrixes)

    @router.get("/{name}/")
    async def matrix_status(name: str):
        mat = _get_matrix(name)
        power = await mat.get_power()
        return {"name": name, "power": power.name}

    @router.post("/{name}/power_on/")
    async def matrix_power_on(name: str):
        mat = _get_matrix(name)
        await mat.power_on()
        return {"ok": True}

    @router.post("/{name}/power_off/")
    async def matrix_power_off(name: str):
        mat = _get_matrix(name)
        await mat.power_off()
        return {"ok": True}

    @router.post("/{name}/reboot/")
    async def matrix_reboot(name: str):
        mat = _get_matrix(name)
        await mat.reboot()
        return {"ok": True}

    class MatrixConnectRequest(BaseModel):
        input: str
        output: str

    @router.post("/{name}/connect/")
    async def matrix_connect(name: str, body: MatrixConnectRequest):
        mat = _get_matrix(name)
        await mat.connect(body.input, body.output)
        return {"ok": True}

    class MatrixConnectManyRequest(BaseModel):
        input: str
        outputs: list[str]

    @router.post("/{name}/connect_many/")
    async def matrix_connect_many(name: str, body: MatrixConnectManyRequest):
        mat = _get_matrix(name)
        for output in body.outputs:
            await mat.connect(body.input, output)
        return {"ok": True}

    return router
