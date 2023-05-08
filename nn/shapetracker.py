import math
import typing as ta

from .dims import View
from .dims import Shape


class ShapeTracker:
    def __init__(
            self,
            shape: ta.Union[Shape, 'ShapeTracker'],
            views: ta.Optional[ta.Iterable['View']] = None,
    ) -> None:
        super().__init__()

        if views is not None:
            self._views = list(views)
        elif isinstance(shape, ShapeTracker):
            self._views = list(shape._views)
        else:
            self._views = [View.of_shape(shape)]

    @staticmethod
    def of(o: ta.Union['ShapeTracker', Shape]) -> 'ShapeTracker':
        if isinstance(o, ShapeTracker):
            return o
        if isinstance(o, Shape):
            return ShapeTracker(o)
        raise TypeError(o)

    @property
    def view(self) -> View:
        return self._views[-1]

    @property
    def shape(self) -> Shape:
        return self.view.shape

    @property
    def size(self) -> int:
        v = self.view
        return math.prod([s for s, st in zip(v.shape, v.stride) if st != 0])
