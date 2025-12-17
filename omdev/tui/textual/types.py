import typing as ta

from textual.geometry import Spacing


##


class TopRightBottomLeft(ta.Protocol):
    """
    A ducktype for at least the following:
     - textual.geometry.Spacing - margin, padding
     - textual.css._style_properties.Edges - border
    """

    @property
    def top(self) -> ta.Any: ...

    @property
    def right(self) -> ta.Any: ...

    @property
    def bottom(self) -> ta.Any: ...

    @property
    def left(self) -> ta.Any: ...


@ta.overload
def trbl_to_dict(trbl: Spacing) -> dict[str, int]:
    ...


@ta.overload
def trbl_to_dict(trbl: TopRightBottomLeft) -> dict[str, ta.Any]:
    ...


def trbl_to_dict(trbl):
    return {
        'top': trbl.top,
        'right': trbl.right,
        'bottom': trbl.bottom,
        'left': trbl.left,
    }
