import dataclasses as dc
import typing as ta

from omlish import lang

from .internals import FieldType


@dc.dataclass()
class ExField:
    name: ta.Optional[str] = None
    type: ta.Any = None
    default: lang.Maybe[ta.Any] = lang.empty()
    default_factory: lang.Maybe[ta.Any] = lang.empty()
    repr: bool = True
    hash: ta.Optional[bool] = None
    init: bool = True
    compare: bool = True
    metadata: ta.Optional[ta.Mapping[ta.Any, ta.Any]] = None
    kw_only: lang.Maybe[ta.Any] = lang.empty()

    field_type: FieldType = FieldType.INSTANCE


@dc.dataclass()
class ExParams:
    init: bool = True
    repr: bool = True
    eq: bool = True
    order: bool = False
    unsafe_hash: bool = False
    frozen: bool = False
    match_args: bool = True
    kw_only: bool = False
    slots: bool = False
    weakref_slot: bool = False
