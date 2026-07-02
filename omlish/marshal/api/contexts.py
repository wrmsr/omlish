"""
TODO:
 - caches?
  - generalized BaseContext cache?
  - or at least config / metadata caches?
   - auto-invalidated by ConfigRegistry.token
"""
import abc
import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from .configs import ConfigRegistry
from .configs import Configs
from .errors import UnhandledTypeError
from .internalstate import InternalState
from .options import _EMPTY_OPTIONS
from .options import Options
from .reflect import ReflectOverride


if ta.TYPE_CHECKING:
    from .types import Marshaler
    from .types import MarshalerFactory
    from .types import Unmarshaler
    from .types import UnmarshalerFactory
    from .values import Value


T = ta.TypeVar('T')


type Context = BoundContext | FactoryContext
type BoundContext = MarshalContext | UnmarshalContext
type FactoryContext = MarshalFactoryContext | UnmarshalFactoryContext


##


# @lang.cached_function
# def _reflect2_smoke_api() -> ta.Any:
#     # A dedicated, process-wide reflect2 Api for the migration smoke test (see BaseContext._reflect). It runs in the
#     # 'unbound' policy so genuinely-unresolvable forward references (e.g. lite recursive aliases like packaging's
#     # RequiresMarkerList) degrade to UnboundType leaves rather than raising - the global reflect2 Api stays strict.
#     from ... import reflect2 as rfl2
#
#     return rfl2.Api(unresolved_forward_ref_policy='unbound')


##


@dc.dataclass(frozen=True, kw_only=True)
class BaseContext(lang.Abstract, lang.Sealed):
    @property
    @abc.abstractmethod
    def configs(self) -> Configs:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def internal_state(self) -> InternalState:
        raise NotImplementedError

    @property
    def internal_state_by_config(self) -> InternalState.ByConfig:
        try:
            return self._internal_state_by_config  # type: ignore[attr-defined]
        except AttributeError:
            pass
        ret = self.internal_state.by_config(check.isinstance(self.configs, ConfigRegistry))
        object.__setattr__(self, '_internal_state_by_config', ret)
        return ret

    def _reflect(self, o: ta.Any) -> rfl.Type:
        def override(o):
            if (ovr := self.configs.get(o).get(ReflectOverride)) is not None:
                return ovr.rty
            return None

        # # Smoke-test reflect2 against the raw runtime types marshal is handed. Skip inputs marshal itself won't
        # # reflect raw: already-reflected old-system types (`make_marshaler` is re-entered with these, relying on the
        # # old Reflector's idempotency over its own TypeInfos), and types short-circuited by a ReflectOverride (which
        # # the old Reflector replaces wholesale, never recursing into their - possibly unreflectable - structure).
        # if not isinstance(o, rfl.TypeInfo) and override(o) is None:
        #     _reflect2_smoke_api().reflect_type(o)

        return rfl.Reflector(override=override).typeof(o)


# Regrettable, but we want to forbid non-factory contexts from having different configs than their factory context.

del BaseContext.configs  # noqa
del BaseContext.internal_state  # noqa
BaseContext.__abstractmethods__ -= {'configs', 'internal_state'}


##


class _PreReflectFactory(lang.Abstract):
    """Internal hook primarily for ReflectOverride."""

    @abc.abstractmethod
    def _pre_reflect(self, ctx: BaseContext) -> None:
        raise NotImplementedError


@dc.dataclass(frozen=True, kw_only=True)
class MarshalFactoryContext(BaseContext, lang.Final):
    configs: Configs = dc.field(default_factory=ConfigRegistry)
    internal_state: InternalState = dc.field(default_factory=InternalState)

    marshaler_factory: MarshalerFactory | None = None

    def make_marshaler(self, o: ta.Any) -> Marshaler:
        fac = check.not_none(self.marshaler_factory)

        if isinstance(fac, _PreReflectFactory):
            fac._pre_reflect(self)  # noqa

        rty = self._reflect(o)

        if (m := fac.make_marshaler(self, rty)) is None:
            raise UnhandledTypeError(rty)  # noqa

        return m()


@dc.dataclass(frozen=True, kw_only=True)
class UnmarshalFactoryContext(BaseContext, lang.Final):
    configs: Configs = dc.field(default_factory=ConfigRegistry)
    internal_state: InternalState = dc.field(default_factory=InternalState)

    unmarshaler_factory: UnmarshalerFactory | None = None

    def make_unmarshaler(self, o: ta.Any) -> Unmarshaler:
        fac = check.not_none(self.unmarshaler_factory)

        if isinstance(fac, _PreReflectFactory):
            fac._pre_reflect(self)  # noqa

        rty = self._reflect(o)

        if (m := fac.make_unmarshaler(self, rty)) is None:
            raise UnhandledTypeError(rty)  # noqa

        return m()


##


@dc.dataclass(frozen=True, kw_only=True)
class MarshalContext(BaseContext, lang.Final):
    options: Options = _EMPTY_OPTIONS

    marshal_factory_context: MarshalFactoryContext

    @property
    def configs(self) -> Configs:
        return self.marshal_factory_context.configs

    @property
    def internal_state(self) -> InternalState:
        return self.marshal_factory_context.internal_state

    def marshal(self, obj: ta.Any, ty: ta.Any | None = None) -> Value:
        return self.marshal_factory_context.make_marshaler(ty if ty is not None else type(obj)).marshal(self, obj)


@dc.dataclass(frozen=True, kw_only=True)
class UnmarshalContext(BaseContext, lang.Final):
    options: Options = _EMPTY_OPTIONS

    unmarshal_factory_context: UnmarshalFactoryContext

    @property
    def configs(self) -> Configs:
        return self.unmarshal_factory_context.configs

    @property
    def internal_state(self) -> InternalState:
        return self.unmarshal_factory_context.internal_state

    @ta.overload
    def unmarshal(self, v: Value, ty: type[T]) -> T: ...

    @ta.overload
    def unmarshal(self, v: Value, ty: ta.Any) -> ta.Any: ...

    def unmarshal(self, v, ty):
        return self.unmarshal_factory_context.make_unmarshaler(ty).unmarshal(self, v)
