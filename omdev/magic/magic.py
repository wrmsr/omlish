# ruff: noqa: UP007 UP045
import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True)
class Magic:
    key: str

    file: ta.Optional[str]

    start_line: int
    end_line: int

    body: str

    prepared: ta.Any
