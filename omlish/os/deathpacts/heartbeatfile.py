"""
TODO:
 - chaining
"""
import os
import time
import typing as ta

from ... import check
from ..forkhooks import ProcessOriginTracker
from ..temp import make_temp_file
from .base import BaseDeathpact


##


class HeartbeatFileDeathpact(BaseDeathpact):
    def __init__(
            self,
            path: str,
            ttl_s: float = 10.,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._path = path
        self._ttl_s = ttl_s

        self._process_origin = ProcessOriginTracker()

    @property
    def path(self) -> str:
        return self._path

    def is_parent(self) -> bool:
        return self._process_origin.is_in_origin_process()

    #

    def __enter__(self) -> ta.Self:
        check.state(self.is_parent())

        self.update()

        return self

    def close(self) -> None:
        if self.is_parent():
            try:
                os.unlink(self._path)
            except FileNotFoundError:
                pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    #

    @classmethod
    def _now(cls) -> float:
        return time.monotonic()

    def update(self) -> None:
        check.state(self.is_parent())

        new = make_temp_file()
        with open(new, 'w') as f:
            f.write(str(self._now()))

        # FIXME: same filesystem
        os.replace(new, self._path)

    def read(self) -> float:
        try:
            with open(self._path) as f:
                return float(f.read())
        except FileNotFoundError:
            return float('-inf')

    def age(self) -> float:
        return self._now() - self.read()

    def should_die(self) -> bool:
        return self.age() >= self._ttl_s
