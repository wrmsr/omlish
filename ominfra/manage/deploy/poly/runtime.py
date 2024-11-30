# ruff: noqa: UP007
import os.path
import stat
import typing as ta

from omlish.lite.logs import log
from omlish.lite.subprocesses import subprocess_check_call

from .base import Runtime


class RuntimeImpl(Runtime):
    def __init__(self) -> None:
        super().__init__()

    def stat(self, p: str) -> ta.Optional[Runtime.Stat]:
        try:
            st = os.stat(p)
        except FileNotFoundError:
            return None
        else:
            return Runtime.Stat(
                path=p,
                is_dir=bool(st.st_mode & stat.S_IFDIR),
            )

    def make_dirs(self, p: str, exist_ok: bool = False) -> None:
        os.makedirs(p, exist_ok=exist_ok)

    def write_file(self, p: str, c: ta.Union[str, bytes]) -> None:
        if os.path.exists(p):
            raise RuntimeError(f'Path exists: {p}')
        with open(p, 'w' if isinstance(c, str) else 'wb') as f:
            f.write(c)

    def sh(self, *ss: str) -> None:
        s = ' && '.join(ss)
        log.info('Executing: %s', s)
        subprocess_check_call(s, shell=True)
