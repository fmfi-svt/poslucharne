from __future__ import annotations

import importlib
from typing import TypeVar

import yaml

from poslucharne.devices import Device, Matrix, Projector, Screen

T = TypeVar("T")


class Room:
    def __init__(self, config: dict):
        self.config: dict = config
        self.name: str = self.config["name"]

        self.projectors = self._create_devices(
            self.config.get("projectors", []), Projector
        )
        self.matrixes = self._create_devices(self.config.get("matrixes", []), Matrix)
        self.screens = self._create_devices(self.config.get("screens", []), Screen)

    def _create_devices(
        self, device_list: list[dict], device_type: type[T]
    ) -> dict[str, T]:
        devices = {}

        for device in device_list:
            module_name, class_name = device["kind"].rsplit(".", 1)
            module = importlib.import_module(module_name)
            class_: type[Device] = getattr(module, class_name)

            if not issubclass(class_, device_type):
                raise ValueError(
                    f"{class_.__name__} is not a subclass of {device_type.__name__}"
                )

            name = device["name"]
            if name in devices:
                raise ValueError(f"duplicate device name {name}")

            devices[name] = class_(name=name, room=self, **device["config"])

        return devices

    @classmethod
    def from_file(cls, filename) -> Room:
        with open(filename) as f:
            config = yaml.safe_load(f)
        return Room(config)
