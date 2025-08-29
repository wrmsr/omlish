import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from .configs import Config


if ta.TYPE_CHECKING:
    from . import types as _types
    from .types import Marshaler
    from .types import MarshalerFactory
    from .types import Unmarshaler
    from .types import UnmarshalerFactory

else:
    _types = lang.proxy_import('.types', __package__)


##


@dc.dataclass(frozen=True, kw_only=True)
class Override(Config, lang.Final):
    marshaler: ta.Optional['Marshaler'] = None
    marshaler_factory: ta.Optional['MarshalerFactory'] = None

    unmarshaler: ta.Optional['Unmarshaler'] = None
    unmarshaler_factory: ta.Optional['UnmarshalerFactory'] = None

    def __post_init__(self) -> None:
        check.isinstance(self.marshaler, (_types.Marshaler, None))
        check.isinstance(self.unmarshaler, (_types.Unmarshaler, None))


@dc.dataclass(frozen=True)
class ReflectOverride(Config, lang.Final):
    rty: rfl.Type
