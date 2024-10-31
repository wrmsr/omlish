import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class Magic:
    key: str

    file: str | None

    start_line: int
    end_line: int

    body: str

    prepared: ta.Any
