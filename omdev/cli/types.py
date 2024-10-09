# ruff: noqa: UP007
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class CliCmd:
    cmd_name: ta.Union[str, ta.Sequence[str]]

    @property
    def primary_name(self) -> str:
        if isinstance(self.cmd_name, str):
            return self.cmd_name
        else:
            return self.cmd_name[0]


@dc.dataclass(frozen=True)
class CliModule(CliCmd):
    mod_name: str


@dc.dataclass(frozen=True)
class CliFunc(CliCmd):
    fn: ta.Callable
