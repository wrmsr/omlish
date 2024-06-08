import typing as ta

from ... import dataclasses as dc


@dc.dataclass()
class C:
    i: int
    s: str
    x: dict[str, ta.Any]


def test_unknown_fields():
    pass
