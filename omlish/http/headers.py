# @omlish-lite
# ruff: noqa: UP006 UP007
"""
TODO:
 - handle secrets (but they're strs..)
"""
import http.client
import typing as ta

from ..lite.cached import cached_nullary
from ..lite.cached import cached_property
from ..lite.check import check


StrOrBytes = ta.Union[str, bytes]  # ta.TypeAlias


##


CanHttpHeaders = ta.Union[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    'HttpHeaders',

    http.client.HTTPMessage,

    ta.Mapping[str, str],
    ta.Mapping[str, ta.Sequence[str]],
    ta.Mapping[str, ta.Union[str, ta.Sequence[str]]],

    ta.Mapping[bytes, bytes],
    ta.Mapping[bytes, ta.Sequence[bytes]],
    ta.Mapping[bytes, ta.Union[bytes, ta.Sequence[bytes]]],

    ta.Mapping[StrOrBytes, StrOrBytes],
    ta.Mapping[StrOrBytes, ta.Sequence[StrOrBytes]],
    ta.Mapping[StrOrBytes, ta.Union[StrOrBytes, ta.Sequence[StrOrBytes]]],

    ta.Sequence[ta.Tuple[str, str]],
    ta.Sequence[ta.Tuple[bytes, bytes]],
    ta.Sequence[ta.Tuple[StrOrBytes, StrOrBytes]],
]


class DuplicateHttpHeaderError(Exception):
    pass


class HttpHeaders:
    def __init__(self, src: CanHttpHeaders) -> None:
        super().__init__()

        if isinstance(src, HttpHeaders):
            check.is_(src, self)
            return

        # TODO: optimized storage, 'use-whats-given'
        lst: ta.List[ta.Tuple[bytes, bytes]] = []
        if isinstance(src, http.client.HTTPMessage):
            lst = [(self._as_bytes(k), self._as_bytes(v)) for k, v in src.items()]

        elif isinstance(src, ta.Mapping):
            for k, v in src.items():
                if isinstance(v, (str, bytes)):
                    lst.append((self._as_bytes(k), self._as_bytes(v)))
                else:
                    for e in v:
                        lst.append((self._as_bytes(k), self._as_bytes(e)))

        elif isinstance(src, (str, bytes)):  # type: ignore
            raise TypeError(src)

        elif isinstance(src, ta.Sequence):
            for t in src:
                if isinstance(t, (str, bytes)):
                    raise TypeError(t)

                k, v = t
                lst.append((self._as_bytes(k), self._as_bytes(v)))

        else:
            raise TypeError(src)

        self._lst = lst

    def __new__(cls, obj: CanHttpHeaders) -> 'HttpHeaders':
        if isinstance(obj, HttpHeaders):
            return obj

        return super().__new__(cls)

    #

    # https://github.com/pgjones/hypercorn/commit/13f385be7277f407a9a361c958820515e16e217e
    ENCODING: ta.ClassVar[str] = 'latin1'

    @classmethod
    def _as_bytes(cls, o: StrOrBytes) -> bytes:
        if isinstance(o, bytes):
            return o
        elif isinstance(o, str):
            return o.encode(cls.ENCODING)
        else:
            raise TypeError(o)

    #

    @cached_nullary
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({{{", ".join(repr(k) for k in self.single_str_dct)}}})'

    #

    @property
    def raw(self) -> ta.Sequence[ta.Tuple[bytes, bytes]]:
        return self._lst

    @classmethod
    def _as_key(cls, o: StrOrBytes) -> bytes:
        return cls._as_bytes(o).lower()

    @cached_property
    def normalized(self) -> ta.Sequence[ta.Tuple[bytes, bytes]]:
        return [(self._as_key(k), v) for k, v in self._lst]

    #

    @cached_property
    def multi_dct(self) -> ta.Mapping[bytes, ta.Sequence[bytes]]:
        d: ta.Dict[bytes, ta.List[bytes]] = {}
        for k, v in self.normalized:
            try:
                l = d[k]
            except KeyError:
                l = d[k] = []
            l.append(v)
        return d

    @cached_property
    def single_dct(self) -> ta.Mapping[bytes, bytes]:
        return {k: v[0] for k, v in self.multi_dct.items() if len(v) == 1}

    @cached_property
    def strict_dct(self) -> ta.Mapping[bytes, bytes]:
        d: ta.Dict[bytes, bytes] = {}
        for k, v in self.normalized:
            if k in d:
                if True:
                    raise DuplicateHttpHeaderError(k)
            else:
                d[k] = v
        return d

    #

    @cached_property
    def strs(self) -> ta.Sequence[ta.Tuple[str, str]]:
        return tuple((k.decode(self.ENCODING), v.decode(self.ENCODING)) for k, v in self.normalized)

    @cached_property
    def multi_str_dct(self) -> ta.Mapping[str, ta.Sequence[str]]:
        d: ta.Dict[str, ta.List[str]] = {}
        for k, v in self.strs:
            try:
                l = d[k]
            except KeyError:
                l = d[k] = []
            l.append(v)
        return d

    @cached_property
    def single_str_dct(self) -> ta.Mapping[str, str]:
        return {k: v[0] for k, v in self.multi_str_dct.items() if len(v) == 1}

    @cached_property
    def strict_str_dct(self) -> ta.Mapping[str, str]:
        d: ta.Dict[str, str] = {}
        for k, v in self.strs:
            if k in d:
                if True:
                    raise DuplicateHttpHeaderError(k)
            else:
                d[k] = v
        return d

    #

    def __bool__(self) -> bool:
        return bool(self._lst)

    def __len__(self) -> int:
        return len(self._lst)

    def __iter__(self) -> ta.Iterator[ta.Tuple[bytes, bytes]]:
        return iter(self._lst)

    @ta.overload
    def __getitem__(self, item: str) -> ta.Sequence[str]:
        ...

    @ta.overload
    def __getitem__(self, item: bytes) -> ta.Sequence[bytes]:
        ...

    @ta.overload
    def __getitem__(self, item: int) -> ta.Tuple[StrOrBytes, StrOrBytes]:
        ...

    @ta.overload
    def __getitem__(self, item: slice) -> ta.Sequence[ta.Tuple[StrOrBytes, StrOrBytes]]:
        ...

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self._lst[item]
        elif isinstance(item, str):
            return self.multi_str_dct[item.lower()]
        elif isinstance(item, bytes):
            return self.multi_dct[self._as_key(item)]
        else:
            raise TypeError(item)

    def keys(self) -> ta.Iterable[bytes]:
        return self.multi_dct.keys()

    def items(self) -> ta.Iterable[ta.Tuple[bytes, bytes]]:
        return self._lst

    #

    def update(
            self,
            *items: ta.Tuple[bytes, bytes],  # FIXME: all arg types
            override: bool = False,
    ) -> 'HttpHeaders':
        if override:
            nks = {k.lower() for k, v in items}
            src = [(k, v) for k, v in self.items() if k.lower() not in nks]
        else:
            src = list(self.items())
        return HttpHeaders([
            *src,
            *items,
        ])


def headers(src: CanHttpHeaders) -> HttpHeaders:
    return HttpHeaders(src)
