"""
TODO:
 - ConfigBackendSpec, drop the configs kwargs
"""
import abc
import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...configs import Config


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


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True, field_defaults=msh.FieldOptions(omit_if=operator.not_))
class StringBackendSpec(BackendSpec, lang.Final):
    s: str


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True, field_defaults=msh.FieldOptions(omit_if=operator.not_))
class NameBackendSpec(BackendSpec, lang.Final):
    name: str
    configs: ta.Sequence[ta.Any] | None = None


@dc.dataclass(frozen=True)
@msh.update_object_options(unwrap_if_single_field=True, field_defaults=msh.FieldOptions(omit_if=operator.not_))
class ModelBackendSpec(BackendSpec, lang.Final):
    name: str
    configs: ta.Sequence[ta.Any] | None = None


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
    configs: ta.Sequence[Config] | None = None
    children: ResolvedBackendSpec | ta.Sequence[ResolvedBackendSpec] | None = None


class BackendSpecResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve(self, service_cls: ta.Any, spec: BackendSpec) -> ResolvedBackendSpec:
        raise NotImplementedError


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
