import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


FieldHashValue: ta.TypeAlias = ta.Union[
    'FieldHashable',
    'FieldHashObject',
    tuple['FieldHashValue', ...],
    str,
    None,
]


@dc.dataclass(frozen=True)
class FieldHashField(lang.Final):
    name: str
    value: FieldHashValue


@dc.dataclass(frozen=True)
class FieldHashObject(lang.Final):
    name: str
    fields: tuple['FieldHashField', ...]


class FieldHashable(lang.Abstract):
    @abc.abstractmethod
    def _field_hash(self) -> FieldHashValue:
        raise NotImplementedError
