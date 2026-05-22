import argparse
import uvicorn
from poslucharne.room import Room
from poslucharne.api import create_app


def main():
    parser = argparse.ArgumentParser(description="Posluchárne Control Server")
    parser.add_argument(
        "room_file",
        help="Path to the room YAML configuration file",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    room = Room.from_file(args.room_file)
    app = create_app(room)

    print(f"Room: {room.name}")
    print(f"Listening on http://{args.host}:{args.port}")

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
