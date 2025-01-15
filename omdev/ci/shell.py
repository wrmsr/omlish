# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc


@dc.dataclass(frozen=True)
class ShellCmd:
    s: str
