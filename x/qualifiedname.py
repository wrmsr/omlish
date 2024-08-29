import collections.abc
import dataclasses as dc
import typing as ta


@dc.dataclass(frozen=True)
class QualifiedName(ta.Sequence[str]):
    parts: ta.Sequence[str]

    def __post_init__(self) -> None:
        if not (
                self.parts and
                all(self.parts) and
                all(isinstance(p, str) for p in self.parts)
        ):
            raise ValueError(self)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}([{", ".join(map(repr, self.parts))}])'

    @property
    def dotted(self) -> str:
        return '.'.join(self.parts)

    def prefixed(self, sz: int) -> ta.Sequence[str | None]:
        if len(self) > sz:
            raise ValueError(self)
        return ((None,) * (sz - len(self))) + tuple(self.parts)

    @property
    def pair(self) -> tuple[str | None, str]:
        return self.prefixed(2)  # noqa

    @property
    def triple(self) -> tuple[str | None, str | None, str]:
        return self.prefixed(3)  # noqa

    @property
    def quad(self) -> tuple[str | None, str | None, str | None, str]:
        return self.prefixed(4)  # noqa

    def __iter__(self) -> ta.Iterator[str]:
        return iter(self.parts)

    def __len__(self) -> int:
        return len(self.parts)

    def __getitem__(self, idx: int) -> str:
        return self.parts[idx]

    @classmethod
    def of_dotted(cls, dotted: str) -> 'QualifiedName':
        return cls(dotted.split('.'))

    @classmethod
    def of(cls, obj: ta.Union['QualifiedName', ta.Iterable[str]]) -> 'QualifiedName':
        if isinstance(obj, QualifiedName):
            return obj
        elif isinstance(obj, str):
            raise TypeError(obj)
        elif isinstance(obj, collections.abc.Iterable):
            return cls(list(obj))
        else:
            raise TypeError(obj)

    @classmethod
    def of_optional(cls, obj: ta.Union['QualifiedName', ta.Iterable[str], None]) -> ta.Optional['QualifiedName']:
        if obj is None:
            return None
        else:
            return cls.of(obj)
