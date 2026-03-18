import abc
import io
import json
import typing as ta

from omlish import check
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


##


def render_field_hash(value: FieldHashValue) -> str:
    def rec(v: FieldHashValue) -> None:
        match v:
            case None:
                out.write('null')

            case str():
                out.write(json.dumps(v))

            case tuple():
                out.write('[')
                for i, e in enumerate(v):
                    if i:
                        out.write(',')
                    rec(e)
                out.write(']')

            case FieldHashObject():
                out.write('{')
                out.write(json.dumps(check.non_empty_str(v.name)))
                out.write(':{')
                for i, f in enumerate(v.fields):
                    if i:
                        out.write(',')
                    out.write(json.dumps(check.non_empty_str(f.name)))
                    out.write(':')
                    rec(f.value)
                out.write('}}')

            case FieldHashable():
                rec(v._field_hash())  # noqa

            case _:
                raise TypeError(v)

    out = io.StringIO()
    rec(value)
    return out.getvalue()
