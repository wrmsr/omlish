import functools
import inspect
import types
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .. import reflect as rfl
from .bindings import Binding
from .eagers import Eager
from .elements import Element
from .elements import Elements
from .elements import as_elements
from .keys import Key
from .keys import as_key
from .multis import MapBinding
from .multis import SetBinding
from .multis import is_map_multi_key
from .multis import is_set_multi_key
from .privates import Expose
from .providers import ConstProvider
from .providers import CtorProvider
from .providers import FnProvider
from .providers import LinkProvider
from .providers import Provider
from .scopes import SCOPE_ALIASES
from .scopes import Singleton
from .tags import Id
from .types import Scope
from .types import Unscoped


if ta.TYPE_CHECKING:
    from .impl.inspect import inspect as _inspect
else:
    _inspect = lang.proxy_import('.impl.inspect', __package__)


T = ta.TypeVar('T')


##


_FN_TYPES: tuple[type, ...] = (
    types.FunctionType,
    types.MethodType,

    classmethod,
    staticmethod,

    functools.partial,
    functools.partialmethod,
)


def _is_fn(obj: ta.Any) -> bool:
    return isinstance(obj, _FN_TYPES)


def bind_as_fn(cls: type[T]) -> type[T]:
    check.isinstance(cls, type)
    global _FN_TYPES
    if cls not in _FN_TYPES:
        _FN_TYPES = (*_FN_TYPES, cls)
    return cls


##


_BANNED_BIND_TYPES: tuple[type, ...] = (
    Element,
    Provider,
    Elements,
    Scope,
)


def bind(
        obj: ta.Any,
        *,
        tag: ta.Any = None,

        to_fn: ta.Any = None,
        to_ctor: ta.Any = None,
        to_const: ta.Any = None,
        to_key: ta.Any = None,

        in_: Scope | None = None,
        singleton: bool = False,

        eager: bool = False,
        expose: bool = False,
) -> Element | Elements:
    if obj is None or obj is inspect.Parameter.empty:
        raise TypeError(obj)
    if isinstance(obj, _BANNED_BIND_TYPES):
        raise TypeError(obj)

    ##

    has_to = (
        to_fn is not None or
        to_ctor is not None or
        to_const is not None or
        to_key is not None
    )
    if isinstance(obj, Key):
        key = obj
    elif isinstance(obj, type):
        if not has_to:
            to_ctor = obj
        key = Key(obj)
    elif isinstance(obj, rfl.TYPES) or rfl.is_type(obj):
        key = Key(obj)
    elif _is_fn(obj) and not has_to:
        sig = _inspect.signature(obj)
        ty = rfl.type_(sig.return_annotation)
        to_fn = obj
        key = Key(ty)
    else:
        if to_const is not None:
            raise TypeError('Cannot bind instance with to_const')
        to_const = obj
        key = Key(type(obj))
    del has_to

    ##

    if tag is not None:
        if key.tag is not None:
            raise TypeError('Tag already set')
        key = dc.replace(key, tag=tag)

    ##

    providers: list[Provider] = []
    if to_fn is not None:
        providers.append(FnProvider(to_fn))
    if to_ctor is not None:
        providers.append(CtorProvider(to_ctor))
    if to_const is not None:
        providers.append(ConstProvider(to_const))
    if to_key is not None:
        providers.append(LinkProvider(as_key(to_key)))
    if not providers:
        raise TypeError('Must specify provider')
    if len(providers) > 1:
        raise TypeError('May not specify multiple providers')
    provider, = providers

    ##

    scopes: list[Scope] = []
    if in_ is not None:
        if isinstance(in_, str):
            scopes.append(SCOPE_ALIASES[in_])
        else:
            scopes.append(check.isinstance(in_, Scope))
    if singleton:
        scopes.append(Singleton())
    if len(scopes) > 1:
        raise TypeError('May not specify multiple scopes')
    scope: Scope
    if not scopes:
        scope = Unscoped()
    else:
        scope, = scopes

    ##

    binding = Binding(key, provider, scope)

    ##

    elements: list[Element] = [binding]

    if eager:
        elements.append(Eager(key))
    if expose:
        elements.append(Expose(key))

    if len(elements) == 1:
        return elements[0]
    else:
        return Elements(frozenset(elements))


##


def bind_set_entry_const(
        multi_key: ta.Any,
        obj: ta.Any,
        *,
        tag: ta.Any | None = None,
) -> Elements:
    multi_key = as_key(multi_key)
    check.arg(is_set_multi_key(multi_key))

    if tag is None:
        tag = Id(id(obj), tag=multi_key.tag)
    obj_key: Key = Key(type(obj), tag=tag)

    return as_elements(
        bind(obj_key, to_const=obj),
        SetBinding(multi_key, obj_key),
    )


def bind_map_entry_const(
        multi_key: ta.Any,
        map_key: ta.Any,
        obj: ta.Any,
        *,
        tag: ta.Any | None = None,
) -> Elements:
    multi_key = as_key(multi_key)
    check.arg(is_map_multi_key(multi_key))

    if tag is None:
        tag = Id(id(obj), tag=multi_key.tag)
    obj_key: Key = Key(type(obj), tag=tag)

    return as_elements(
        bind(obj_key, to_const=obj),
        MapBinding(multi_key, map_key, obj_key),
    )
