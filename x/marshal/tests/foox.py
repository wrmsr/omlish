import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class Foox:
    il: list[int]
