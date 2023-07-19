import dataclasses as dc
import typing as ta


@dc.dataclass()
class ExField:
    name: str
    type: ta.Any
    default: ta.Any
    default_factory: ta.Any
    repr: bool
    hash: ta.Optional[bool]
    init: bool
    compare: bool
    metadata: ta.Optional[ta.Mapping[ta.Any, ta.Any]]
    kw_only: bool

    # _field_type


@dc.dataclass()
class ExParams:
    init: bool
    repr: bool
    eq: bool
    order: bool
    unsafe_hash: bool
    frozen: bool
    match_args: bool
    kw_only: bool
    slots: bool
    weakref_slot: bool
