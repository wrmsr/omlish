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
import typing as ta

from ..elements import Element
from ..elements import Elements


def bind() -> Element | Elements:
    raise NotImplementedError


def test_api():
    pass
