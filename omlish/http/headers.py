import typing as ta

from .. import cached
from .. import check
from .. import collections as col


StrOrBytes: ta.TypeAlias = str | bytes

CanHttpHeaders: ta.TypeAlias = ta.Union[
    'HttpHeaders',
    ta.Mapping[StrOrBytes, StrOrBytes],
    ta.Mapping[StrOrBytes, ta.Sequence[StrOrBytes]],
    ta.Mapping[StrOrBytes, StrOrBytes | ta.Sequence[StrOrBytes]],
    ta.Sequence[tuple[StrOrBytes, StrOrBytes]],
]


class HttpHeaders:
    def __init__(self, src: CanHttpHeaders) -> None:
        super().__init__()

        if isinstance(src, HttpHeaders):
            check.is_(src, self)
            return

        # TODO: optimized storage, 'use-whats-given'
        lst: list[tuple[bytes, bytes]] = []
        if isinstance(src, ta.Mapping):
            for k, v in src.items():
                if isinstance(v, (str, bytes)):
                    lst.append((self._as_bytes(k), self._as_bytes(v)))
                else:
                    for e in v:
                        lst.append((self._as_bytes(k), self._as_bytes(e)))

        elif isinstance(src, (str, bytes)):  # type: ignore
            raise TypeError(src)

        elif isinstance(src, ta.Sequence):
            for k, v in src:
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

    @cached.function
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({{{", ".join(repr(k) for k in self.single_str_dct)}}})'

    #

    @cached.property
    def multi_dct(self) -> ta.Mapping[bytes, ta.Sequence[bytes]]:
        return col.multi_map(self._lst)

    @cached.property
    def single_dct(self) -> ta.Mapping[bytes, bytes]:
        return {k: v[0] for k, v in self.multi_dct.items() if len(v) == 1}

    @cached.property
    def strict_dct(self) -> ta.Mapping[bytes, bytes]:
        return col.make_map(self._lst, strict=True)

    #

    @cached.property
    def strs(self) -> ta.Sequence[tuple[str, str]]:
        return tuple((k.decode(self.ENCODING), v.decode(self.ENCODING)) for k, v in self._lst)

    @cached.property
    def multi_str_dct(self) -> ta.Mapping[str, ta.Sequence[str]]:
        return col.multi_map(self.strs)

    @cached.property
    def single_str_dct(self) -> ta.Mapping[str, str]:
        return {k: v[0] for k, v in self.multi_str_dct.items() if len(v) == 1}

    @cached.property
    def strict_str_dct(self) -> ta.Mapping[str, str]:
        return col.make_map(self.strs, strict=True)

    #

    def __bool__(self) -> bool:
        return bool(self._lst)

    def __len__(self) -> int:
        return len(self._lst)

    def __iter__(self) -> ta.Iterator[tuple[bytes, bytes]]:
        return iter(self._lst)

    @ta.overload
    def __getitem__(self, item: StrOrBytes) -> ta.Sequence[StrOrBytes]:
        ...

    @ta.overload
    def __getitem__(self, item: int) -> StrOrBytes:
        ...

    @ta.overload
    def __getitem__(self, item: slice) -> ta.Sequence[StrOrBytes]:
        ...

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self._lst[item]
        elif isinstance(item, (str, bytes)):
            return self.multi_dct[self._as_bytes(item)]
        else:
            raise TypeError(item)

    def keys(self) -> ta.Iterable[bytes]:
        return self.multi_dct.keys()

    def items(self) -> ta.Iterable[tuple[bytes, bytes]]:
        return self._lst


def headers(src: CanHttpHeaders) -> HttpHeaders:
    return HttpHeaders(src)
