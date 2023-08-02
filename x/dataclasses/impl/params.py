import dataclasses as dc
import typing as ta

from omlish import lang

from .internals import Params
from .internals import PARAMS_ATTR


def get_params(obj: ta.Any) -> Params:
    if dc.is_dataclass(obj):
        return getattr(obj, PARAMS_ATTR)
    raise TypeError(obj)


@dc.dataclass(frozen=True)
class ExtraFieldParams(lang.Final):
    coerce: ta.Optional[ta.Union[bool, ta.Callable[[ta.Any], ta.Any]]] = None


@dc.dataclass(frozen=True)
class Params12(lang.Final):
    match_args: bool = True
    kw_only: bool = False
    slots: bool = False
    weakref_slot: bool = False


@dc.dataclass(frozen=True)
class ExtraParams(lang.Final):
    metadata: ta.Optional[ta.Mapping[ta.Any, ta.Any]] = None
