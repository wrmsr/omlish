import dataclasses as dc
import sys
import typing as ta

from omlish import check
from omlish import lang

from .internals import Params


IS_12 = sys.version_info[1] >= 12


class FieldInfo:
    def __init__(self, f: dc.Field) -> None:
        super().__init__()
        self._f = check.isinstance(f, dc.Field)

    @property
    def base(self) -> dc.Field:
        return self._f

    name: ta.Optional[str] = None
    type: ta.Any = None
    default: lang.Maybe[ta.Any] = lang.empty()
    default_factory: lang.Maybe[ta.Any] = lang.empty()
    repr: bool = True
    hash: ta.Optional[bool] = None
    init: bool = True
    compare: bool = True
    metadata: ta.Optional[ta.Mapping[ta.Any, ta.Any]] = None
    kw_only: ta.Optional[bool] = None



class ClassInfo:
    def __init__(self, p: Params) -> None:
        super().__init__()
        self._p = check.isinstance(p, Params)

    @property
    def base(self) -> Params:
        return self._p

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
