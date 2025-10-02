# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
TODO:
 - dotted paths!
 - per-attr repr transform / filter
 - __ne__ ? cases where it still matters
 - ordering ?
 - repr_filter: ta.Union[ta.Callable[[ta.Any], ta.Optional[str]], ta.Literal['not_none', 'truthy']]] ?
  - unify repr/repr_fn/repr_filter
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
                repr_fn: ta.Optional[ta.Callable[[ta.Any], ta.Optional[str]]] = None,

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
            self._repr_fn = repr_fn

            self._hash = hash
            self._eq = eq

        @classmethod
        def of(
                cls,
                o: ta.Union[
                    'AttrOps.Attr',
                    str,
                    ta.Tuple[str, ta.Union[str, ta.Mapping[str, ta.Any]]],
                    ta.Mapping[str, ta.Any],
                ],
        ) -> 'AttrOps.Attr':
            if isinstance(o, AttrOps.Attr):
                return o
            elif isinstance(o, str):
                return cls(o)
            elif isinstance(o, tuple):
                name, x = o
                kw: ta.Mapping[str, ta.Any]
                if isinstance(x, str):
                    kw = dict(display=x)
                elif isinstance(x, ta.Mapping):
                    kw = x
                else:
                    raise TypeError(x)
                return cls(name, **kw)
            elif isinstance(o, ta.Mapping):
                return cls(**o)
            else:
                raise TypeError(o)

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

    @staticmethod
    def opt_repr(o: ta.Any) -> ta.Optional[str]:
        return repr(o) if o is not None else None

    @staticmethod
    def truthy_repr(o: ta.Any) -> ta.Optional[str]:
        return repr(o) if o else None

    #

    @ta.overload
    def __init__(
            self,
            *attrs: ta.Sequence[ta.Union[
                str,
                ta.Tuple[str, ta.Union[str, ta.Mapping[str, ta.Any]]],
                ta.Mapping[str, ta.Any],
                Attr,
            ]],

            with_module: bool = False,
            use_qualname: bool = False,
            with_id: bool = False,
            terse: bool = False,
            repr_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
            recursive: bool = False,

            cache_hash: ta.Union[bool, str] = False,
            subtypes_eq: bool = False,
    ) -> None:
        ...

    @ta.overload
    def __init__(
            self,
            attrs_fn: ta.Callable[[T], ta.Tuple[ta.Union[
                ta.Any,
                ta.Tuple[ta.Any, ta.Union[str, ta.Mapping[str, ta.Any]]],
                Attr,
            ], ...]],
            /,
            *,

            with_module: bool = False,
            use_qualname: bool = False,
            with_id: bool = False,
            terse: bool = False,
            repr_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
            recursive: bool = False,

            cache_hash: ta.Union[bool, str] = False,
            subtypes_eq: bool = False,
    ) -> None:
        ...

    def __init__(
            self,
            *args,

            with_module=False,
            use_qualname=False,
            with_id=False,
            terse=False,
            repr_filter=None,
            recursive=False,

            cache_hash=False,
            subtypes_eq=False,
    ) -> None:
        if args and len(args) == 1 and callable(args[0]):
            self._attrs: ta.Sequence[AttrOps.Attr] = self._capture_attrs(args[0])
        else:
            self._attrs = list(map(AttrOps.Attr.of, args))

        self._with_module: bool = with_module
        self._use_qualname: bool = use_qualname
        self._with_id: bool = with_id
        self._terse: bool = terse
        self._repr_filter: ta.Optional[ta.Callable[[ta.Any], bool]] = repr_filter
        self._recursive: bool = recursive

        self._cache_hash: ta.Union[bool, str] = cache_hash
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
            if isinstance(o, (AttrOps.Attr, ta.Mapping)):
                attrs.append(AttrOps.Attr.of(o))
                continue

            kw: ta.Mapping[str, ta.Any]
            if isinstance(o, tuple):
                cap, x = o
                if isinstance(x, str):
                    kw = dict(display=x)
                elif isinstance(x, ta.Mapping):
                    kw = x
                else:
                    raise TypeError(x)
            else:
                cap, kw = o, {}

            path = tuple(rec(cap))

            attrs.append(AttrOps.Attr(
                '.'.join(path),
                **kw,
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
            vs: ta.List[str] = []
            for a in self._attrs:
                if not a._repr:  # noqa
                    continue
                v = getattr(o, a._name)  # noqa
                if self._repr_filter is not None and not self._repr_filter(v):
                    continue
                if (rfn := a._repr_fn) is None:  # noqa
                    rfn = repr
                if (vr := rfn(v)) is None:
                    continue
                if self._terse:
                    vs.append(vr)
                else:
                    vs.append(f'{a._display}={vr}')  # noqa

            return (
                f'{o.__class__.__module__ + "." if self._with_module else ""}'
                f'{o.__class__.__qualname__ if self._use_qualname else o.__class__.__name__}'
                f'{("@" + hex(id(o))[2:]) if self._with_id else ""}'  # noqa
                f'({", ".join(vs)})'
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

    _DEFAULT_CACHED_HASH_ATTR: ta.ClassVar[str] = '__cached_hash__'

    _hash: ta.Callable[[T], int]

    @property
    def hash(self) -> ta.Callable[[T], int]:
        try:
            return self._hash
        except AttributeError:
            pass

        def _calc_hash(o: T) -> int:
            return hash(tuple(
                getattr(o, a._name)  # noqa
                for a in self._attrs
                if a._hash  # noqa
            ))

        if (ch := self._cache_hash) is not False:
            if ch is True:
                cha = self._DEFAULT_CACHED_HASH_ATTR
            elif isinstance(ch, str):
                cha = ch
            else:
                raise TypeError(ch)

            def _cached_hash(o: T) -> int:
                try:
                    return object.__getattribute__(o, cha)
                except AttributeError:
                    object.__setattr__(o, cha, h := _calc_hash(o))
                return h

            _hash = _cached_hash

        else:
            _hash = _calc_hash

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
