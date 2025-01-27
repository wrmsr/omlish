# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc


@dc.dataclass(frozen=True)
class Fileno:
    fd: int

    def fileno(self) -> int:
        return self.fd
