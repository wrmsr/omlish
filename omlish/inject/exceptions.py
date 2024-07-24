import typing as ta

from .. import dataclasses as dc
from .keys import Key
from .types import Scope

##


@dc.dataclass()
class BaseKeyError(Exception):
    key: Key

    source: ta.Any = None
    name: str | None = None


@dc.dataclass()
class UnboundKeyError(KeyError):
    pass


@dc.dataclass()
class DuplicateKeyError(KeyError):
    pass


@dc.dataclass()
class CyclicDependencyError(KeyError):
    pass


##


@dc.dataclass()
class ScopeError(Exception):
    scope: Scope


@dc.dataclass()
class ScopeAlreadyOpenError(ScopeError):
    pass


@dc.dataclass()
class ScopeNotOpenError(ScopeError):
    pass
