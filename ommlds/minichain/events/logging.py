import asyncio
import fcntl
import os.path
import typing as ta

from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish.formats import json

from .types import Event


##


class JsonlFileEventLogger:
    @dc.dataclass(frozen=True)
    class Config:
        file_path: str

        _: dc.KW_ONLY

        no_lock: bool = False

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = config

        self._lock = asyncio.Lock()

    async def log_events(self, events: ta.Iterable[Event]) -> None:
        ms = [msh.marshal(e) for e in events]
        js = [json.dumps_compact(m) for m in ms]
        j = '\n'.join([*js, ''])

        os.makedirs(os.path.dirname(self._config.file_path), exist_ok=True)

        async with self._lock:
            with open(self._config.file_path, 'a') as f:  # noqa
                if not (nl := self._config.no_lock):
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        raise RuntimeError(f'Driver event log file {self._config.file_path} is locked') from None

                try:
                    f.write(j)

                finally:
                    if not nl:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    async def log_event(self, event: Event) -> None:
        await self.log_events([event])
