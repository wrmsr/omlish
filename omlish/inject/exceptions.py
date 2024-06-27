import typing as ta

from .. import dataclasses as dc
from .keys import Key
from .types import Scope


##


@dc.dataclass()
class KeyException(Exception):
    key: Key

    source: ta.Any = None
    name: ta.Optional[str] = None


@dc.dataclass()
class UnboundKeyException(KeyException):
    pass


@dc.dataclass()
class DuplicateKeyException(KeyException):
    pass


@dc.dataclass()
class CyclicDependencyException(KeyException):
    pass


##


@dc.dataclass()
class ScopeException(Exception):
    scope: Scope


@dc.dataclass()
class ScopeAlreadyOpenException(ScopeException):
    pass


@dc.dataclass()
class ScopeNotOpenException(ScopeException):
    pass
