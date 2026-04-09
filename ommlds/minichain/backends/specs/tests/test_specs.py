import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang


##


CanBackendSpec: ta.TypeAlias = ta.Union[
    str,
    'BackendSpec',
]


@dc.dataclass(frozen=True)
class BackendSpec(lang.Sealed):
    @ta.final
    @classmethod
    def of(cls, obj: CanBackendSpec) -> BackendSpec:
        check.is_(cls, BackendSpec, 'Must not access `BackendSpec.of()` through a subclass.')

        if isinstance(obj, BackendSpec):
            return obj

        elif isinstance(obj, str):
            return StringBackendSpec(obj)

        else:
            raise TypeError(obj)


@dc.dataclass(frozen=True)
class StringBackendSpec(BackendSpec, lang.Final):
    s: str


@dc.dataclass(frozen=True)
class RetryBackendSpec(BackendSpec, lang.Final):
    child: CanBackendSpec


@dc.dataclass(frozen=True)
class FirstInWinsBackendSpec(BackendSpec, lang.Final):
    children: ta.Sequence[CanBackendSpec]
