from .. import dataclasses as dc


@dc.dataclass(frozen=True)
class Point:
    x: int
    y: int
    name: str = dc.field(default='foo', kw_only=True)


def test_dataclasses():
    pt = Point(1, 2)
    print(pt)


def test_reorder():
    @dc.dataclass()
    class C:
        x: int
        y: int = 5

    REQUIRED = object()

    @dc.dataclass()
    class D(C):
        z: int = dc.field(default=REQUIRED)

    # FIXME:
    # assert [f.name for f in dc.fields(D)] == ['x', 'z', 'y']
