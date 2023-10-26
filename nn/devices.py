from __future__ import annotations

import functools
import importlib
import inspect
import pathlib
import typing as ta

from .helpers import getenv

if ta.TYPE_CHECKING:
    from .execution import Compiled
    from .execution import Interpreted


class _Device:
    def __init__(self) -> None:
        super().__init__()
        self._buffers: list[str] = [
            x.stem[len("ops_"):].upper()
            for x in (pathlib.Path(__file__).parent / "runtime").iterdir()
            if x.stem.startswith("ops_")
        ]

    def canonicalize(self, device: ta.Optional[str]) -> str:
        return (
            (
                device.split(":", 1)[0].upper() +
                ((":" + device.split(":", 1)[1]) if ":" in device else "")
            ).replace(":0", "")
            if device is not None
            else self.DEFAULT
        )

    @functools.lru_cache(maxsize=None)  # this class is a singleton, pylint: disable=method-cache-max-size-none
    def __getitem__(self, x: str) -> ta.Union[Interpreted, Compiled]:
        x = x.split(":")[0].upper()
        return [
            cls
            for cname, cls in inspect.getmembers(importlib.import_module(f".runtime.ops_{x.lower()}", __package__))
            if (cname.lower() == x.lower() + "buffer") and x in self._buffers
        ][0]

    @functools.cached_property
    def DEFAULT(self) -> str:
        device_from_env: ta.Optional[str] = functools.reduce(
            lambda val, ele: ele if getenv(ele) == 1 else val, self._buffers, None
        )

        if device_from_env:
            print(device_from_env)
            return device_from_env

        for device in [
            "METAL",
            "CUDA",
            "OPENCL",

            # "LLVM",
            # "CLANG",
            # "TORCH",
            # "WEBGPU",
        ]:
            try:
                if self[device]:
                    return device
            except Exception as e:  # noqa
                breakpoint()
                pass

        return "CPU"


Device = _Device()
