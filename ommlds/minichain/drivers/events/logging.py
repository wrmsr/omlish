import fcntl
import os.path

from omlish import dataclasses as dc
from omlish import marshal as msh
from omlish.formats import json

from ..types import Event


##


class EventLogger:
    @dc.dataclass(frozen=True)
    class Config:
        file_path: str

        _: dc.KW_ONLY

        no_lock: bool = False

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = config

    async def handle_event(self, event: Event) -> None:
        m = msh.marshal(event, Event)
        j = json.dumps_compact(m)

        os.makedirs(os.path.dirname(self._config.file_path), exist_ok=True)

        with open(self._config.file_path, 'a') as f:  # noqa
            if not (nl := self._config.no_lock):
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    raise RuntimeError(f'Driver event log file {self._config.file_path} is locked') from None

            try:
                f.write(j + '\n')

            finally:
                if not nl:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
