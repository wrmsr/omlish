import dataclasses as dc
import typing as ta

from ..only_ import only


def test_only():
    @dc.dataclass(frozen=True)
    class Pt:
        x: int | None = None
        y: int | None = None
        xs: ta.Sequence[int] | None = None
        ys: ta.Sequence[int] | None = None

    assert only(Pt())

    assert only(Pt(x=0), 'x')
    assert only(Pt(x=0), 'x', all=True)

    assert not only(Pt(x=0))
    assert not only(Pt(x=0, y=1), 'x')

    assert not only(Pt(x=0, y=1), 'x')
    assert only(Pt(x=0, y=1), 'x', 'y')
    assert only(Pt(x=0, y=1), 'x', 'y', all=True)
    assert only(Pt(x=0), 'x', 'y')
    assert not only(Pt(x=0), 'x', 'y', all=True)

    assert only(Pt(xs=[]), 'xs')
    assert not only(Pt(xs=[]), 'xs', all=True)
