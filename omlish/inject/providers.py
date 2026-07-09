import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from .inspect import KwargsTarget
from .keys import Key


##


class _Missing(lang.NotInstantiable):
    pass


class Provider(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class AsyncFnProvider(Provider):
    fn: ta.Any = dc.xfield(validate=lambda v: callable(v) or isinstance(v, KwargsTarget))


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class FnProvider(Provider):
    fn: ta.Any = dc.xfield(validate=lambda v: callable(v) or isinstance(v, KwargsTarget))


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class CtorProvider(Provider):
    """Functionally identical to `FnProvider`, but limited to simple types to communicate intent."""

    ty: type = dc.xfield(validate=lambda ty: isinstance(ty, type) or rfl.is_simple_generic_alias_type(ty))


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class ConstProvider(Provider):
    v: ta.Any


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class LinkProvider(Provider):
    k: Key = dc.xfield(coerce=check.of_isinstance(Key))
