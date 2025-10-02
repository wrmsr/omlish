"""
TODO:
 - StrView, BytesView - in lieu of hkt lol
 - cext? even necessary?
 - __eq__, cmp, __hash__
 - __buffer__
 - optimize `slice(None)`, keep as SeqView but fast path ops
 - shorter repr if __len__ > some threshold
  - use materialize()?
"""
import typing as ta


T = ta.TypeVar('T')


##


def iterslice(
        seq: ta.Sequence[T],
        slc: slice,
) -> ta.Iterator[T]:
    return map(seq.__getitem__, range(*slc.indices(len(seq))))


def iterrange(
        seq: ta.Sequence[T],
        start: int | None = None,
        stop: int | None = None,
        step: int | None = None,
) -> ta.Iterator[T]:
    return iterslice(seq, slice(start, stop, step))


##


@ta.final
class SeqView(ta.Sequence[T]):
    def __init__(self, data: ta.Sequence[T], slice_: slice = slice(None)) -> None:
        if data.__class__ is SeqView:
            self._data = data._data  # type: ignore[attr-defined]  # noqa
            self._range = data._range[slice_]  # type: ignore[attr-defined]  # noqa
        else:
            self._data = data
            self._range = range(*slice_.indices(len(data)))

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    _data: ta.Sequence[T]
    _range: range

    @classmethod
    def _from_range(cls, base: ta.Sequence[T], rng: range) -> 'SeqView[T]':
        self = object.__new__(cls)
        self._data = base
        self._range = rng
        return self

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._data!r}, {self.slice!r})'

    #

    def __len__(self) -> int:
        return len(self._range)

    def __getitem__(self, key: int | slice) -> ta.Union[T, 'SeqView[T]']:  # type: ignore[override]
        if isinstance(key, slice):
            nr = self._range[key]
            return SeqView._from_range(self._data, nr)
        return self._data[self._range[key]]

    def __iter__(self) -> ta.Iterator[T]:
        return map(self._data.__getitem__, self._range)

    def __reversed__(self) -> ta.Iterator[T]:
        return map(self._data.__getitem__, reversed(self._range))

    def count(self, value: ta.Any) -> int:
        c = 0
        for i in self._range:
            if self._data[i] == value:
                c += 1
        return c

    def index(self, value: ta.Any, start: int = 0, stop: int | None = None) -> int:
        sub = self._range[slice(start, stop, 1)]
        for off, i in enumerate(sub):
            if self._data[i] == value:
                return off
        raise ValueError(f'{value!r} is not in view')

    #

    @property
    def data(self) -> ta.Sequence[T]:
        return self._data

    _slice: slice

    @property
    def slice(self) -> slice:
        try:
            return self._slice
        except AttributeError:
            pass

        step = self._range.step
        start = self._range.start
        if len(self._range) == 0:
            stop = start
        else:
            last = start + (len(self._range) - 1) * step
            stop = last + (1 if step > 0 else -1)
        slc = slice(start, stop, step)

        self._slice = slc
        return slc

    def materialize(self) -> ta.Sequence[T]:
        return self._data[self.slice]
