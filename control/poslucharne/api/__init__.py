from fastapi import FastAPI

from poslucharne.room import Room
from poslucharne.api.projectors import create_router as projectors_router
from poslucharne.api.matrixes import create_router as matrixes_router


def create_app(room: Room) -> FastAPI:
    app = FastAPI(title="Posluchárne Control Server")

    @app.get("/")
    def room_info():
        return {
            "name": room.name,
            "projectors": list(room.projectors),
            "matrixes": list(room.matrixes),
        }

    app.include_router(projectors_router(room))
    app.include_router(matrixes_router(room))

    return app
