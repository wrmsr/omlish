import abc
import inspect
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.formats import json5
from omlish.manifests.globals import GlobalManifestLoader

from ..configs import Config
from ..models.configs import ModelName
from ..registries.globals import get_global_registry
from ..registries.registry import Registry
from ..services import is_stream_service_cls
from .manifests import BackendStringsManifest
from .types import BackendSpec
from .types import BackendSpecResolver
from .types import ConfigBackendSpec
from .types import FirstInWinsBackendSpec
from .types import ModelBackendSpec
from .types import NameBackendSpec
from .types import ResolvedBackendSpec
from .types import RetryBackendSpec
from .types import StringBackendSpec


with lang.auto_proxy_import(globals()):
    from ..wrappers import firstinwins
    from ..wrappers import retry

BackendSpecT = ta.TypeVar('BackendSpecT', bound=BackendSpec)


##


class BackendSpecTypeResolver(lang.Abstract, ta.Generic[BackendSpecT]):
    @dc.dataclass(frozen=True, kw_only=True)
    class ResolveContext:
        service_cls: ta.Any

        rec: ta.Callable[[BackendSpec], ResolvedBackendSpec]

        registry: Registry
        registry_type: Registry.Type

    @abc.abstractmethod
    def resolve(self, ctx: ResolveContext, spec: BackendSpecT) -> ResolvedBackendSpec:
        raise NotImplementedError


#


class StringBackendSpecTypeResolver(BackendSpecTypeResolver[StringBackendSpec]):
    def resolve(self, ctx: BackendSpecTypeResolver.ResolveContext, spec: StringBackendSpec) -> ResolvedBackendSpec:
        s = check.non_empty_str(spec.s.strip())

        if s.startswith('{'):
            rs_spec = msh.unmarshal(json5.loads(s), BackendSpec)
        elif s in ctx.registry_type.entries:
            rs_spec = NameBackendSpec(s)
        else:
            # TODO: parsing lol
            rs_spec = ModelBackendSpec(s)

        return ctx.rec(rs_spec)


#


class NameBackendSpecTypeResolver(BackendSpecTypeResolver[NameBackendSpec]):
    def resolve(self, ctx: BackendSpecTypeResolver.ResolveContext, spec: NameBackendSpec) -> ResolvedBackendSpec:
        cls = ctx.registry_type.lookup(spec.name)

        return ResolvedBackendSpec(
            ctx.service_cls,
            spec,

            cls,
        )


#


class ModelBackendSpecTypeResolver(BackendSpecTypeResolver[ModelBackendSpec]):
    def resolve(self, ctx: BackendSpecTypeResolver.ResolveContext, spec: ModelBackendSpec) -> ResolvedBackendSpec:
        mam = self._model_alias_map(ctx.registry_type)
        bsm = check.single(mam[spec.name])

        return ctx.rec(
            ConfigBackendSpec(
                NameBackendSpec(
                    bsm.backend_name,
                ),
                (ModelName(spec.name),),
            ),
        )

    @lang.cached_function
    def _model_alias_map(self, rt: Registry.Type) -> ta.Mapping[str, ta.Sequence[BackendStringsManifest]]:
        return col.multi_map(
            (an, bsm)
            for bsm in GlobalManifestLoader.load_values_of(BackendStringsManifest)
            if rt.name in bsm.service_cls_names
            if (mnc := bsm.model_names) is not None
            for an in mnc.resolved
        )


#


class ConfigBackendSpecTypeResolver(BackendSpecTypeResolver[ConfigBackendSpec]):
    def resolve(self, ctx: BackendSpecTypeResolver.ResolveContext, spec: ConfigBackendSpec) -> ResolvedBackendSpec:
        rbs = ctx.rec(BackendSpec.of(spec.child))

        configs: ta.Sequence[Config]

        if all(isinstance(c, Config) for c in spec.configs):
            configs = spec.configs

        else:
            # TODO: if can't inspect, use ctx.reflect_type?
            cfg_rty = self._inspect_cls_config_arg(rbs.ctor)  # noqa

            configs = []
            for c in spec.configs:
                if not isinstance(c, Config):
                    c = msh.unmarshal(c, cfg_rty)

                configs.append(c)

        return dc.replace(
            rbs,
            configs=(
                *(rbs.configs or ()),
                *configs,
            ),
        )

    @lang.cached_function
    def _inspect_cls_config_arg(self, cls: ta.Any) -> rfl.Type:
        sig = inspect.signature(cls)  # noqa
        cfgs_arg = next(iter(sig.parameters.values()))
        check.state(cfgs_arg.kind == inspect.Parameter.VAR_POSITIONAL)
        check.is_not(cfgs_arg.annotation, inspect.Parameter.empty)
        check.is_not(cfgs_arg.annotation, Config)
        return rfl.typeof(cfgs_arg.annotation)


#


class RetryBackendSpecTypeResolver(BackendSpecTypeResolver[RetryBackendSpec]):
    def resolve(self, ctx: BackendSpecTypeResolver.ResolveContext, spec: RetryBackendSpec) -> ResolvedBackendSpec:
        return ResolvedBackendSpec(
            ctx.service_cls,
            spec,

            retry.RetryStreamService if is_stream_service_cls(ctx.service_cls) else retry.RetryService,
            children=ctx.rec(BackendSpec.of(spec.child)),
        )


#


class FirstInWinsBackendSpecTypeResolver(BackendSpecTypeResolver[FirstInWinsBackendSpec]):
    def resolve(self, ctx: BackendSpecTypeResolver.ResolveContext, spec: FirstInWinsBackendSpec) -> ResolvedBackendSpec:  # noqa
        if is_stream_service_cls(ctx.service_cls):
            raise NotImplementedError

        else:
            return ResolvedBackendSpec(
                ctx.service_cls,
                spec,

                firstinwins.AsyncioFirstInWinsService,
                children=tuple(
                    ctx.rec(BackendSpec.of(child))
                    for child in spec.children
                ),
            )


##


class TypeMapBackendSpecResolver(BackendSpecResolver):
    def __init__(
            self,
            type_resolvers: ta.Mapping[type[BackendSpec], BackendSpecTypeResolver],
            *,
            registry: Registry | None = None,
    ) -> None:
        super().__init__()

        self._type_resolvers = type_resolvers

        if registry is None:
            registry = get_global_registry()
        self._registry = check.not_none(registry)

    def resolve(self, service_cls: ta.Any, spec: BackendSpec) -> ResolvedBackendSpec:
        def rec(rec_spec: BackendSpec) -> ResolvedBackendSpec:
            tr = self._type_resolvers[type(rec_spec)]

            return tr.resolve(ctx, rec_spec)

        ctx = BackendSpecTypeResolver.ResolveContext(
            service_cls=service_cls,

            rec=rec,

            registry=self._registry,
            registry_type=self._registry.get_type(service_cls),
        )

        return rec(spec)


##


DEFAULT_BACKEND_SPEC_TYPE_RESOLVERS: ta.Mapping[type[BackendSpec], BackendSpecTypeResolver] = {
    StringBackendSpec: StringBackendSpecTypeResolver(),
    NameBackendSpec: NameBackendSpecTypeResolver(),
    ModelBackendSpec: ModelBackendSpecTypeResolver(),
    ConfigBackendSpec: ConfigBackendSpecTypeResolver(),
    RetryBackendSpec: RetryBackendSpecTypeResolver(),
    FirstInWinsBackendSpec: FirstInWinsBackendSpecTypeResolver(),
}


DEFAULT_BACKEND_SPEC_RESOLVER: BackendSpecResolver = TypeMapBackendSpecResolver(DEFAULT_BACKEND_SPEC_TYPE_RESOLVERS)
