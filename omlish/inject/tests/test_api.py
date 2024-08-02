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

from ... import reflect as rfl
from ..bindings import Binding
from ..elements import Element
from ..elements import Elements
from ..keys import Key
from ..keys import as_key
from ..providers import ConstProvider
from ..types import Scope


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

    raise NotImplementedError


def test_api():
    assert bind(5) == Binding(Key(rfl.type_(int)), ConstProvider(5))
