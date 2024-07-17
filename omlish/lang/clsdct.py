import functools
import sys
import types
import typing as ta


_CLS_DCT_ATTR_SETS = [
    {
        '__module__',
        '__qualname__',
    },
    {
        '__all__',
    },
]


def _skip_cls_dct_frames(f: types.FrameType) -> types.FrameType:
    if sys.implementation.name == 'pypy':
        if f.f_code is functools.partial.__call__.__code__:  # noqa
            return _skip_cls_dct_frames(f.f_back)  # type: ignore

    return f


def is_possibly_cls_dct(dct: ta.Mapping[str, ta.Any]) -> bool:
    return any(all(a in dct for a in s) for s in _CLS_DCT_ATTR_SETS)


def get_caller_cls_dct(offset: int = 0) -> ta.MutableMapping[str, ta.Any]:
    f = sys._getframe(offset + 2)  # noqa
    cls_dct = _skip_cls_dct_frames(f).f_locals
    if not is_possibly_cls_dct(cls_dct):
        raise TypeError(cls_dct)
    return cls_dct


class ClassDctFn:

    def __init__(self, fn: ta.Callable, offset: int | None = None, *, wrap=True) -> None:
        super().__init__()

        self._fn = fn
        self._offset = offset if offset is not None else 1

        if wrap:
            functools.update_wrapper(self, fn)

    def __get__(self, instance, owner=None):
        return type(self)(self._fn.__get__(instance, owner), self._offset)  # noqa

    def __call__(self, *args, **kwargs):
        try:
            cls_dct = kwargs.pop('cls_dct')
        except KeyError:
            f = sys._getframe(self._offset)  # noqa
            cls_dct = _skip_cls_dct_frames(f).f_locals
        if not is_possibly_cls_dct(cls_dct):
            raise TypeError(cls_dct)
        return self._fn(cls_dct, *args, **kwargs)


def cls_dct_fn(offset=1, *, wrap=True):  # noqa
    def outer(fn):
        return ClassDctFn(fn, offset, wrap=wrap)

    return outer
