import dataclasses as dc
import typing as ta

from ... import check
from ... import collections as col
from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
from .configs import EMPTY_CONFIG_REGISTRY
from .configs import ConfigRegistry
from .errors import UnhandledTypeError
from .options import Option
from .overrides import ReflectOverride


if ta.TYPE_CHECKING:
    from .types import Marshaler
    from .types import MarshalerFactory
    from .types import Unmarshaler
    from .types import UnmarshalerFactory
    from .values import Value


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True, kw_only=True)
class BaseContext(lang.Abstract):
    config_registry: ConfigRegistry = EMPTY_CONFIG_REGISTRY
    options: col.TypeMap[Option] = col.TypeMap()

    def _reflect(self, o: ta.Any) -> rfl.Type:
        def override(o):
            if (ovr := self.config_registry.get_of(o, ReflectOverride)):
                return ovr[-1].rty
            return None

        return rfl.Reflector(override=override).type(o)


@dc.dataclass(frozen=True, kw_only=True)
class MarshalContext(BaseContext, lang.Final):
    factory: ta.Optional['MarshalerFactory'] = None

    def make(self, o: ta.Any) -> 'Marshaler':
        rty = self._reflect(o)
        try:
            return check.not_none(self.factory).make_marshaler(self, rty)
        except mfs.MatchGuardError:
            raise UnhandledTypeError(rty)  # noqa

    def marshal(self, obj: ta.Any, ty: ta.Any | None = None) -> 'Value':
        return self.make(ty if ty is not None else type(obj)).marshal(self, obj)


@dc.dataclass(frozen=True, kw_only=True)
class UnmarshalContext(BaseContext, lang.Final):
    factory: ta.Optional['UnmarshalerFactory'] = None

    def make(self, o: ta.Any) -> 'Unmarshaler':
        rty = self._reflect(o)
        try:
            return check.not_none(self.factory).make_unmarshaler(self, rty)
        except mfs.MatchGuardError:
            raise UnhandledTypeError(rty)  # noqa

    @ta.overload
    def unmarshal(self, v: 'Value', ty: type[T]) -> T:
        ...

    @ta.overload
    def unmarshal(self, v: 'Value', ty: ta.Any) -> ta.Any:
        ...

    def unmarshal(self, v, ty):
        return self.make(ty).unmarshal(self, v)
