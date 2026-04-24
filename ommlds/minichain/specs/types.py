import abc
import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from ..configs import Config


##


CanBackendSpec: ta.TypeAlias = ta.Union[
    str,
    'BackendSpec',
]


@dc.dataclass(frozen=True)
class BackendSpec(lang.Sealed):
    @ta.final
    @classmethod
    def of(cls, obj: CanBackendSpec) -> BackendSpec:
        check.is_(cls, BackendSpec, 'Must not access `BackendSpec.of()` through a subclass.')

        if isinstance(obj, BackendSpec):
            return obj

        elif isinstance(obj, str):
            return StringBackendSpec(obj)

        else:
            raise TypeError(obj)

    #

    def as_json(self) -> str:
        try:
            return self._as_json  # type: ignore[attr-defined]
        except AttributeError:
            pass

        as_json = json.dumps_compact(msh.marshal(self, BackendSpec))

        object.__setattr__(self, '_as_json', as_json)
        return as_json


##


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True, field_defaults=msh.FieldOptions(omit_if=operator.not_))
class StringBackendSpec(BackendSpec, lang.Final):
    s: str


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True, field_defaults=msh.FieldOptions(omit_if=operator.not_))
class NameBackendSpec(BackendSpec, lang.Final):
    name: str


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True, field_defaults=msh.FieldOptions(omit_if=operator.not_))
class ModelBackendSpec(BackendSpec, lang.Final):
    name: str


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True)
class ConfigBackendSpec(BackendSpec, lang.Final):
    child: CanBackendSpec
    configs: ta.Sequence[ta.Any]

    def __post_init__(self) -> None:
        check.not_empty(self.configs)


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True)
class RetryBackendSpec(BackendSpec, lang.Final):
    child: CanBackendSpec


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True)
class FirstInWinsBackendSpec(BackendSpec, lang.Final):
    children: ta.Sequence[CanBackendSpec]


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class ResolvedBackendSpec:
    service_cls: ta.Any
    spec: BackendSpec

    ctor: ta.Any
    configs: tuple[Config, ...] | None = None
    children: ResolvedBackendSpec | tuple[ResolvedBackendSpec, ...] | None = None

    def __post_init__(self) -> None:
        check.isinstance(self.spec, BackendSpec)

        check.isinstance(self.configs, (tuple, None))
        check.isinstance(self.children, (ResolvedBackendSpec, tuple, None))


class BackendSpecResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve(self, service_cls: ta.Any, spec: BackendSpec) -> ResolvedBackendSpec:
        raise NotImplementedError


##


class BackendSpecInstantiator(ta.Protocol):
    def __call__(self, rbs: ResolvedBackendSpec, *args: ta.Any, **kwargs: ta.Any) -> ta.Awaitable[ta.Any]:
        ...


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    msh.install_standard_factories_to(cfgs, *msh.standard_polymorphism_factories(
        msh.polymorphism_from_subclasses(
            BackendSpec,
            strip_suffix=True,
            naming=msh.Naming.SNAKE,
        ),
    ))
