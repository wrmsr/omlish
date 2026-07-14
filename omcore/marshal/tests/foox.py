import dataclasses as dc


@dc.dataclass(frozen=True)
class Foox:
    il: list[int]
