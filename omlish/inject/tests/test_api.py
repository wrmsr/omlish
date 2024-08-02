"""
class Binding(Element, lang.Final):

class Eager(Element, lang.Final):

class Key(lang.Final, ta.Generic[T]):

class SetBinding(Element, lang.Final):
class SetProvider(Provider):

class MapBinding(Element, lang.Final):
class MapProvider(Provider):

class Overrides(Element, lang.Final):

class Expose(Element, lang.Final):
class Private(Element, lang.Final):

class Provider(lang.Abstract):
class FnProvider(Provider):
class CtorProvider(Provider):
class ConstProvider(Provider):
class LinkProvider(Provider):

class ScopeBinding(Element, lang.Final):
class Singleton(Scope, lang.Singleton, lang.Final):
class Thread(Scope, lang.Singleton, lang.Final):

class SeededScope(Scope, lang.Final):
class ScopeSeededProvider(Provider):
"""
import inspect
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..bindings import Binding
from ..eagers import Eager
from ..elements import Element
from ..elements import Elements
from ..keys import Key
from ..keys import as_key
from ..providers import ConstProvider
from ..providers import CtorProvider
from ..providers import FnProvider
from ..providers import LinkProvider
from ..providers import Provider
from ..scopes import Singleton
from ..types import Scope
from ..types import Unscoped


def bind(
        obj: ta.Any,
        *,
        tag: ta.Any = None,

        eager: bool = False,

        in_: Scope | None = None,
        singleton: bool = False,

        to_fn: ta.Any = None,
        to_ctor: ta.Any = None,
        to_const: ta.Any = None,
        to_key: ta.Any = None,
) -> Element | Elements:
    if obj is inspect.Parameter.empty or obj is None:
        raise TypeError(obj)

    if isinstance(obj, Key):
        key = obj
    elif isinstance(obj, rfl.TYPES) or rfl.is_type(obj):
        key = Key(rfl.type_(obj))
    else:
        if to_const is not None:
            raise TypeError('Cannot bind instance with to_const')
        to_const = obj
        key = Key(rfl.type_(type(obj)))

    if tag is not None:
        if key.tag is not None:
            raise TypeError('Tag already set')
        key = dc.replace(key, tag=tag)

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

    scopes: list[Scope] = []
    if in_ is not None:  # TODO: string alises?
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

    binding = Binding(key, provider, scope)

    elements: list[Element] = [binding]

    if eager:
        elements.append(Eager(key))

    if len(elements) == 1:
        return elements[0]
    else:
        return Elements(frozenset(elements))


def test_api():
    assert bind(5) == Binding(Key(rfl.type_(int)), ConstProvider(5))
