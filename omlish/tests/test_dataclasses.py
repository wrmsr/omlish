from .. import dataclasses as dc


@dc.dataclass(frozen=True)
class Point:
    x: int
    y: int
    name: str = 'foo'


def test_dataclasses():
    pt = Point(1, 2)
    print(pt)
