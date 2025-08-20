# ruff: noqa: UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True)
class CliCmd:
    name: ta.Union[str, ta.Sequence[str]]

    @property
    def primary_name(self) -> str:
        if isinstance(self.name, str):
            return self.name
        else:
            return self.name[0]


@dc.dataclass(frozen=True)
class CliModule(CliCmd):
    module: str


@dc.dataclass(frozen=True)
class CliFunc(CliCmd):
    fn: ta.Callable
