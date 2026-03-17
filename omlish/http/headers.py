# @omlish-lite
# ruff: noqa: PYI034 UP006 UP007 UP045
"""
TODO:
 - handle secrets (but they're strs..)
 - *enforce* lower case access keys? `if not k.islower(): raise KeysMustBeLowerCaseHttpHeadersError(k)` ?
   - `(s := 'abcd').lower() is s` == `False`
 - kill `__new__` self hack, use (require?) `.of()`
"""
import collections.abc
import dataclasses as dc
import http.client
import typing as ta

from ..lite.check import check


StrOrBytes = ta.Union[str, bytes]  # ta.TypeAlias


##


CanHttpHeaders = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'HttpHeaders',

    http.client.HTTPMessage,

    ta.Mapping[str, ta.Union[StrOrBytes, ta.Sequence[StrOrBytes]]],
    ta.Mapping[bytes, ta.Union[StrOrBytes, ta.Sequence[StrOrBytes]]],
    ta.Mapping[StrOrBytes, ta.Union[StrOrBytes, ta.Sequence[StrOrBytes]]],

    ta.Sequence[ta.Tuple[StrOrBytes, StrOrBytes]],
]


@dc.dataclass()
class DuplicateHttpHeaderError(Exception):
    key: str


@ta.final
class HttpHeaders(ta.Mapping[str, ta.Sequence[str]]):
    def __init__(self, src: CanHttpHeaders) -> None:
        super().__init__()

        if isinstance(src, HttpHeaders):
            check.is_(src, self)
            return

        self._raw = self.unpack(src)

        self._all = tuple((self._as_key(k), v) for k, v in self._raw)

        dct: ta.Dict[str, ta.List[str]] = {}
        for k, v in self._all:
            dct.setdefault(k, []).append(v)
        self._dct = {k: tuple(v) for k, v in dct.items()}

    @classmethod
    def unpack(cls, src: ta.Optional[CanHttpHeaders]) -> ta.Sequence[ta.Tuple[str, str]]:
        if src is None:
            return ()

        if isinstance(src, HttpHeaders):
            return src.raw

        raw: ta.List[ta.Tuple[str, str]] = []

        if isinstance(src, http.client.HTTPMessage):
            raw = list(src.items())

        elif isinstance(src, collections.abc.Mapping):
            for k, v in src.items():
                if isinstance(v, (str, bytes)):
                    raw.append((cls._decode(k), cls._decode(v)))
                else:
                    for e in v:
                        raw.append((cls._decode(k), cls._decode(e)))

        elif isinstance(src, (str, bytes)):  # type: ignore
            raise TypeError(src)

        elif isinstance(src, collections.abc.Sequence):
            for t in src:
                if isinstance(t, (str, bytes)):
                    raise TypeError(t)

                k, v = t
                raw.append((cls._decode(k), cls._decode(v)))

        else:
            raise TypeError(src)

        return raw

    def __new__(cls, obj: CanHttpHeaders) -> 'HttpHeaders':
        if isinstance(obj, HttpHeaders):
            return obj

        return super().__new__(cls)

    @classmethod
    def of(cls, obj: ta.Optional[CanHttpHeaders]) -> 'HttpHeaders':
        if isinstance(obj, HttpHeaders):
            return obj

        elif not obj:
            return cls._EMPTY

        else:
            return cls(obj)

    _EMPTY: ta.ClassVar['HttpHeaders']

    @classmethod
    def empty(cls) -> 'HttpHeaders':
        return cls._EMPTY

    #

    @property
    def raw(self) -> ta.Sequence[ta.Tuple[str, str]]:
        return self._raw

    @property
    def all(self) -> ta.Sequence[ta.Tuple[str, str]]:
        return self._all

    #

    @classmethod
    def _decode(cls, o: StrOrBytes) -> str:
        if isinstance(o, bytes):
            return o.decode('latin-1')
        elif isinstance(o, str):
            return o
        else:
            raise TypeError(o)

    @classmethod
    def _as_key(cls, o: StrOrBytes) -> str:
        return cls._decode(o).lower()

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<{", ".join(map(repr, self._dct))}>'

    #

    def __bool__(self) -> bool:
        return len(self._dct) > 0

    #

    def __len__(self) -> int:
        return len(self._dct)

    def __iter__(self) -> ta.Iterator[str]:
        return iter(self._dct)

    def __getitem__(self, key: str) -> ta.Sequence[str]:
        return self._dct[key.lower()]

    def __contains__(self, key: str) -> bool:  # type: ignore[override]
        return check.isinstance(key, str).lower() in self._dct

    #

    _raw_by_key: ta.Mapping[str, ta.Sequence[ta.Tuple[str, str]]]

    @property
    def raw_by_key(self) -> ta.Mapping[str, ta.Sequence[ta.Tuple[str, str]]]:
        try:
            return self._raw_by_key
        except AttributeError:
            pass
        dct: ta.Dict[str, ta.List[ta.Tuple[str, str]]] = {}
        for k, v in self._raw:
            dct.setdefault(self._as_key(k), []).append((k, v))
        return {k: tuple(vs) for k, vs in dct.items()}

    #

    @ta.final
    class _SingleAccessor:
        def __init__(self, o: 'HttpHeaders') -> None:
            self._o = o

        def __getitem__(self, key: str) -> str:
            l = self._o._dct[key.lower()]  # noqa
            if len(l) > 1:
                raise DuplicateHttpHeaderError(key)
            return l[0]

        @ta.overload
        def get(self, key: str, /, default: str) -> str:
            ...

        @ta.overload
        def get(self, key: str, /, default: ta.Optional[str] = None) -> ta.Optional[str]:
            ...

        def get(self, key, /, default=None):
            try:
                return self[key]
            except KeyError:
                return default

    _single: _SingleAccessor

    @property
    def single(self) -> _SingleAccessor:
        try:
            return self._single
        except AttributeError:
            pass
        a = self._single = self._SingleAccessor(self)
        return a

    #

    @ta.final
    class _LowerAccessor:
        def __init__(self, o: 'HttpHeaders') -> None:
            self._o = o

            self._cache: ta.Dict[str, ta.Sequence[str]] = {}

        def __getitem__(self, key: str) -> ta.Sequence[str]:
            key = key.lower()
            try:
                return self._cache[key]
            except KeyError:
                pass
            x = self._o._dct[key]  # noqa
            l = self._cache[key] = tuple(v.lower() for v in x)
            return l

        @ta.overload
        def get(self, key: str, /, default: ta.Sequence[str]) -> ta.Sequence[str]:
            ...

        @ta.overload
        def get(self, key: str, /, default: ta.Optional[str] = None) -> ta.Optional[ta.Sequence[str]]:
            ...

        def get(self, key, /, default=None):
            try:
                return self[key]
            except KeyError:
                return default

    _lower: _LowerAccessor

    @property
    def lower(self) -> _LowerAccessor:
        try:
            return self._lower
        except AttributeError:
            pass
        a = self._lower = self._LowerAccessor(self)
        return a

    #

    def contains_value(self, key: str, value: str, *, ignore_case: bool = False) -> bool:
        try:
            if ignore_case:
                vs = self.lower[key.lower()]
            else:
                vs = self._dct[key.lower()]
        except KeyError:
            return False
        return value in vs

    def update(
            self,
            *items: ta.Tuple[str, ta.Union[str, ta.Callable[[], ta.Optional[str]], None]],
            if_present: ta.Literal['append', 'override', 'skip', 'raise'],
            # preserve_raw: bool = False,  # TODO: less wasteful
    ) -> 'HttpHeaders':
        if not items:
            return self

        v: ta.Any
        if if_present == 'append':
            return HttpHeaders([
                *self._raw,
                *[(k, v) for k, rv in items if (v := (rv() if callable(rv) else rv)) is not None]],
            )

        dct: ta.Dict[str, ta.Sequence[ta.Tuple[str, str]]] = dict(self.raw_by_key)

        for k, v in items:
            if (lk := k.lower()) in dct and if_present != 'override':
                if (v := (v() if callable(v) else v)) is None:
                    continue

                if if_present == 'skip':
                    continue
                elif if_present == 'raise':
                    raise DuplicateHttpHeaderError(k)
                else:
                    raise RuntimeError(f'unknown if_present: {if_present!r}')

            if (v := (v() if callable(v) else v)) is None:
                continue
            dct[lk] = [(k, v)]

        return HttpHeaders([kv for kvs in dct.values() for kv in kvs])


HttpHeaders._EMPTY = HttpHeaders([])  # noqa
