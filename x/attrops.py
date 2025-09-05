# @omlish-lite
"""
TODO:
 - class Attr(ta.NamedTuple)
 - dotted paths!
"""
import typing as ta


T = ta.TypeVar('T')


##


@ta.final
class AttrOps(ta.Generic[T]):
    @ta.final
    class Attr:
        def __init__(
                self,
                name: str,
                *,
                display: ta.Optional[str] = None,
        ) -> None:
            if not name.isidentifier():
                raise AttributeError(f'Invalid attr: {name!r}')
            self._name = name
            if display is None:
                display = name
            self._display = display

        @classmethod
        def of(
                cls,
                o: ta.Union[
                    str,
                    ta.Tuple[str, str],
                    'AttrOps.Attr',
                ],
        ) -> 'AttrOps.Attr':
            if isinstance(o, AttrOps.Attr):
                return o
            elif isinstance(o, str):
                return cls(o)
            else:
                name, disp = o
                return cls(
                    name,
                    display=disp,
                )

        @property
        def name(self) -> str:
            return self._name

        @property
        def display(self) -> str:
            return self._display

    @ta.overload
    def __init__(
            self,
            attrs: ta.Sequence[ta.Union[
                str,
                ta.Tuple[str, str],
                Attr,
            ]],
            /,
            *,
            with_module: bool = False,
            use_qualname: bool = False,
            with_id: bool = False,
            repr_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
            recursive: bool = False,
    ) -> None:
        ...

    @ta.overload
    def __init__(
            self,
            attrs_fn: ta.Callable[[T], ta.Tuple[ta.Union[
                ta.Any,
                ta.Tuple[str, ta.Any],
                Attr,
            ], ...]],
            /,
            *,
            with_module: bool = False,
            use_qualname: bool = False,
            with_id: bool = False,
            repr_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
            recursive: bool = False,
    ) -> None:
        ...

    def __init__(
            self,
            arg,
            with_module=False,
            use_qualname=False,
            with_id=False,
            repr_filter=None,
            recursive=False,
    ) -> None:
        if callable(arg):
            self._attrs: ta.Sequence[AttrOps.Attr] = self._capture_attrs(arg)
        else:
            self._attrs = list(map(AttrOps.Attr.of, arg))

        self._with_module: bool = with_module
        self._use_qualname: bool = use_qualname
        self._with_id: bool = with_id
        self._repr_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = repr_filter
        self._recursive: bool = recursive

    #

    @ta.final
    class _AttrCapturer:
        def __init__(self, fn):
            self.__fn = fn

        def __getattr__(self, attr):
            return self.__fn(self, attr)

    @classmethod
    def _capture_attrs(cls, fn: ta.Callable) -> ta.Sequence[Attr]:
        def access(parent, attr):
            dct[(ret := cls._AttrCapturer(access))] = (parent, attr)
            return ret

        dct: dict = {}
        raw = fn(root := cls._AttrCapturer(access))

        def rec(cap):  # noqa
            if cap is root:
                return
            parent, attr = dct[cap]
            yield from rec(parent)
            yield attr

        attrs: ta.List[AttrOps.Attr] = []
        for o in raw:
            if isinstance(o, AttrOps.Attr):
                attrs.append(o)
                continue

            if isinstance(o, tuple):
                disp, cap, = o
            else:
                disp, cap = None, o

            path = tuple(rec(cap))

            attrs.append(AttrOps.Attr(
                '.'.join(path),
                display=disp,
            ))

        return attrs

    #

    _repr: ta.Callable[[T], str]

    @property
    def repr(self) -> ta.Callable[[T], str]:
        try:
            return self._repr
        except AttributeError:
            pass

        def _repr(o: T) -> str:
            vs = ', '.join(
                f'{attr.display}={v!r}'
                for attr in self._attrs
                for v in [getattr(o, attr.name)]
                if self._repr_filter is None or self._repr_filter(v)
            )

            return (
                f'{o.__class__.__module__ + "." if self._with_module else ""}'
                f'{o.__class__.__qualname__ if self._use_qualname else o.__class__.__name__}'
                f'{("@" + hex(id(o))[2:]) if self._with_id else ""}'
                f'({vs})'
            )

        if self._recursive:
            _repr = self._reprlib().recursive_repr()(_repr)

        self._repr = _repr
        return _repr

    _reprlib_: ta.ClassVar[ta.Any]

    @classmethod
    def _reprlib(cls) -> ta.Any:
        try:
            return cls._reprlib_
        except AttributeError:
            pass

        import reprlib  # noqa

        cls._reprlib_ = reprlib
        return reprlib


##


class Point:
    x: int
    y: int

    a = AttrOps['Point'](lambda o: (o.x, o.y))


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
