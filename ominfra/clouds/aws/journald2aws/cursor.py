# ruff: noqa: UP007
import os.path
import typing as ta

from omlish.lite.logs import log


class JournalctlToAwsCursor:
    def __init__(
            self,
            cursor_file: ta.Optional[str] = None,
            *,
            ensure_locked: ta.Optional[ta.Callable[[], None]] = None,
    ) -> None:
        super().__init__()
        self._cursor_file = cursor_file
        self._ensure_locked = ensure_locked

    #

    def get(self) -> ta.Optional[str]:
        if self._ensure_locked is not None:
            self._ensure_locked()

        if not (cf := self._cursor_file):
            return None
        cf = os.path.expanduser(cf)

        try:
            with open(cf) as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def set(self, cursor: str) -> None:
        if self._ensure_locked is not None:
            self._ensure_locked()

        if not (cf := self._cursor_file):
            return
        cf = os.path.expanduser(cf)

        log.info('Writing cursor file %s : %s', cf, cursor)
        with open(ncf := cf + '.next', 'w') as f:
            f.write(cursor)

        os.rename(ncf, cf)
