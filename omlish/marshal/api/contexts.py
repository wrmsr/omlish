import dataclasses as dc
import typing as ta

from ... import check
from ... import collections as col
from ... import lang
from ... import reflect as rfl
from .configs import EMPTY_CONFIG_REGISTRY
from .configs import Configs
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
class BaseContext(lang.Abstract, lang.Sealed):
    configs: Configs = EMPTY_CONFIG_REGISTRY
    options: col.TypeMap[Option] = col.TypeMap()

    def _reflect(self, o: ta.Any) -> rfl.Type:
        def override(o):
            if (ovr := self.configs.get_of(o, ReflectOverride)):
                return ovr[-1].rty
            return None

        return rfl.Reflector(override=override).type(o)


#


@dc.dataclass(frozen=True, kw_only=True)
class MarshalFactoryContext(BaseContext, lang.Final):
    marshaler_factory: ta.Optional['MarshalerFactory'] = None

    def make_marshaler(self, o: ta.Any) -> 'Marshaler':
        rty = self._reflect(o)
        fac = check.not_none(self.marshaler_factory)
        if (m := fac.make_marshaler(self, rty)) is None:
            raise UnhandledTypeError(rty)  # noqa
        return m()


@dc.dataclass(frozen=True, kw_only=True)
class UnmarshalFactoryContext(BaseContext, lang.Final):
    unmarshaler_factory: ta.Optional['UnmarshalerFactory'] = None

    def make_unmarshaler(self, o: ta.Any) -> 'Unmarshaler':
        rty = self._reflect(o)
        fac = check.not_none(self.unmarshaler_factory)
        if (m := fac.make_unmarshaler(self, rty)) is None:
            raise UnhandledTypeError(rty)  # noqa
        return m()


#


@dc.dataclass(frozen=True, kw_only=True)
class MarshalContext(BaseContext, lang.Final):
    marshal_factory_context: MarshalFactoryContext

    def marshal(self, obj: ta.Any, ty: ta.Any | None = None) -> 'Value':
        return self.marshal_factory_context.make_marshaler(ty if ty is not None else type(obj)).marshal(self, obj)


@dc.dataclass(frozen=True, kw_only=True)
class UnmarshalContext(BaseContext, lang.Final):
    unmarshal_factory_context: UnmarshalFactoryContext

    @ta.overload
    def unmarshal(self, v: 'Value', ty: type[T]) -> T:
        ...

    @ta.overload
    def unmarshal(self, v: 'Value', ty: ta.Any) -> ta.Any:
        ...

    def unmarshal(self, v, ty):
        return self.unmarshal_factory_context.make_unmarshaler(ty).unmarshal(self, v)
