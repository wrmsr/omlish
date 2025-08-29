import typing as ta
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from .registries import RegistryItem


if ta.TYPE_CHECKING:
    from .types import Marshaler
    from .types import MarshalerFactory
    from .types import Unmarshaler
    from .types import UnmarshalerFactory

    from . import types as _types

else:
    _types = lang.proxy_import('.types', __package__)


##


@dc.dataclass(frozen=True, kw_only=True)
class Override(RegistryItem, lang.Final):
    marshaler: ta.Optional['Marshaler'] = dc.xfield(None, validate=lambda v: isinstance(v, (_types.Marshaler, type(None))))  # noqa
    marshaler_factory: ta.Optional['MarshalerFactory'] = None

    unmarshaler: ta.Optional['Unmarshaler'] = dc.xfield(None, validate=lambda v: isinstance(v, (_types.Unmarshaler, type(None))))  # noqa
    unmarshaler_factory: ta.Optional['UnmarshalerFactory'] = None


@dc.dataclass(frozen=True)
class ReflectOverride(RegistryItem, lang.Final):
    rty: rfl.Type
