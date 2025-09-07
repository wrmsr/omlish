# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - dotted paths!
 - per-attr repr transform / filter
 - __ne__ ? cases where it still matters
 - ordering ?
"""
import types  # noqa
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

                repr: bool = True,  # noqa
                hash: bool = True,  # noqa
                eq: bool = True,
        ) -> None:
            if '.' in name:
                raise NotImplementedError('Dotted paths not yet supported')
            if not name.isidentifier() or name.startswith('__'):
                raise AttributeError(f'Invalid attr: {name!r}')
            self._name = name

            if display is None:
                display = name[1:] if name.startswith('_') and len(name) > 1 else name
            self._display = display

            self._repr = repr
            self._hash = hash
            self._eq = eq

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

        @property
        def hash(self) -> bool:
            return self._hash

        @property
        def eq(self) -> bool:
            return self._eq

    @ta.overload
    def __init__(
            self,
            *attrs: ta.Sequence[ta.Union[
                str,
                ta.Tuple[str, str],
                Attr,
            ]],
            with_module: bool = False,
            use_qualname: bool = False,
            with_id: bool = False,
            repr_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
            recursive: bool = False,
            subtypes_eq: bool = False,
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
            subtypes_eq: bool = False,
    ) -> None:
        ...

    def __init__(
            self,
            *args,
            with_module=False,
            use_qualname=False,
            with_id=False,
            repr_filter=None,
            recursive=False,
            subtypes_eq=False,
    ) -> None:
        if args and len(args) == 1 and callable(args[0]):
            self._attrs: ta.Sequence[AttrOps.Attr] = self._capture_attrs(args[0])
        else:
            self._attrs = list(map(AttrOps.Attr.of, args))

        self._with_module: bool = with_module
        self._use_qualname: bool = use_qualname
        self._with_id: bool = with_id
        self._repr_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = repr_filter
        self._recursive: bool = recursive
        self._subtypes_eq: bool = subtypes_eq

    @property
    def attrs(self) -> ta.Sequence[Attr]:
        return self._attrs

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
                f'{a._display}={v!r}'  # noqa
                for a in self._attrs
                if a._repr  # noqa
                for v in [getattr(o, a._name)]  # noqa
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

    #

    _hash: ta.Callable[[T], int]

    @property
    def hash(self) -> ta.Callable[[T], int]:
        try:
            return self._hash
        except AttributeError:
            pass

        def _hash(o: T) -> int:
            return hash(tuple(
                getattr(o, a._name)  # noqa
                for a in self._attrs
                if a._hash  # noqa
            ))

        self._hash = _hash
        return _hash

    #

    _eq: ta.Callable[[T, ta.Any], ta.Union[bool, 'types.NotImplementedType']]

    @property
    def eq(self) -> ta.Callable[[T, ta.Any], ta.Union[bool, 'types.NotImplementedType']]:
        try:
            return self._eq
        except AttributeError:
            pass

        def _eq(o: T, x: ta.Any) -> 'ta.Union[bool, types.NotImplementedType]':
            if self._subtypes_eq:
                if not isinstance(x, type(o)):
                    return NotImplemented
            else:
                if type(x) is not type(o):
                    return NotImplemented

            return all(
                getattr(o, a._name) == getattr(x, a._name)  # noqa
                for a in self._attrs
                if a._eq  # noqa
            )

        self._eq = _eq
        return _eq

    @property
    def hash_eq(self) -> ta.Tuple[
        ta.Callable[[T], int],
        ta.Callable[[T, ta.Any], ta.Union[bool, 'types.NotImplementedType']],
    ]:
        return (self.hash, self.eq)

    #

    @property
    def repr_hash_eq(self) -> ta.Tuple[
        ta.Callable[[T], str],
        ta.Callable[[T], int],
        ta.Callable[[T, ta.Any], ta.Union[bool, 'types.NotImplementedType']],
    ]:
        return (self.repr, self.hash, self.eq)

    #

    class NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def install(
            self,
            locals_dct: ta.MutableMapping[str, ta.Any],
            *,
            repr: ta.Union[bool, ta.Type[NOT_SET]] = NOT_SET,  # noqa
            hash: ta.Union[bool, ta.Type[NOT_SET]] = NOT_SET,  # noqa
            eq: ta.Union[bool, ta.Type[NOT_SET]] = NOT_SET,
    ) -> 'AttrOps[T]':
        if all(a is self.NOT_SET for a in (repr, hash, eq)):
            repr = hash = eq = True  # noqa
        if repr:
            locals_dct.update(__repr__=self.repr)
        if hash:
            locals_dct.update(__hash__=self.hash)
        if eq:
            locals_dct.update(__eq__=self.eq)
        return self


attr_ops = AttrOps[ta.Any]


##


def attr_repr(obj: ta.Any, *attrs: str, **kwargs: ta.Any) -> str:
    return AttrOps(*attrs, **kwargs).repr(obj)
