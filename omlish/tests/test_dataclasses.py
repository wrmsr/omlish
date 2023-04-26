from .. import dataclasses as dc


@dc.dataclass(frozen=True)
class Point:
    x: int
    y: int
    name: str = dc.field(default='foo', kw_only=True)


def test_dataclasses():
    pt = Point(1, 2)
    print(pt)
