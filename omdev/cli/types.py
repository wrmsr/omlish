import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class CliCmd:
    cmd_name: str


@dc.dataclass(frozen=True)
class CliModule(CliCmd):
    mod_name: str


@dc.dataclass(frozen=True)
class CliFunc(CliCmd):
    fn: ta.Callable
