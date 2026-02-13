# @omlish-lite
# ruff: noqa: PYI034 UP006 UP007
"""
TODO:
 - handle secrets (but they're strs..)
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


class HttpHeaders(ta.Mapping[str, ta.Sequence[str]]):
    def __init__(self, src: CanHttpHeaders) -> None:
        super().__init__()

        if isinstance(src, HttpHeaders):
            check.is_(src, self)
            return

        raw: ta.List[ta.Tuple[str, str]] = []

        if isinstance(src, http.client.HTTPMessage):
            raw = list(src.items())

        elif isinstance(src, ta.Mapping):
            for k, v in src.items():
                if isinstance(v, (str, bytes)):
                    raw.append((self._decode(k), self._decode(v)))
                else:
                    for e in v:
                        raw.append((self._decode(k), self._decode(e)))

        elif isinstance(src, (str, bytes)):  # type: ignore
            raise TypeError(src)

        elif isinstance(src, collections.abc.Sequence):
            for t in src:
                if isinstance(t, (str, bytes)):
                    raise TypeError(t)

                k, v = t
                raw.append((self._decode(k), self._decode(v)))

        else:
            raise TypeError(src)

        self._raw = raw

        self._all = tuple((self._as_key(k), v) for k, v in self._raw)

        dct: ta.Dict[str, ta.List[str]] = {}
        for k, v in self._all:
            dct.setdefault(k, []).append(v)
        self._dct = {k: tuple(v) for k, v in dct.items()}

    def __new__(cls, obj: CanHttpHeaders) -> 'HttpHeaders':
        if isinstance(obj, HttpHeaders):
            return obj

        return super().__new__(cls)

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
        return f'{self.__class__.__name__}({self._raw!r})'

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

    _single: _SingleAccessor

    @property
    def single(self) -> _SingleAccessor:
        try:
            return self._single
        except AttributeError:
            pass
        a = self._single = self._SingleAccessor(self)
        return a


def http_headers(src: CanHttpHeaders) -> HttpHeaders:
    return HttpHeaders(src)
