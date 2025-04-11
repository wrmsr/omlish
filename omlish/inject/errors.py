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
class UnboundKeyError(BaseKeyError):
    pass


@dc.dataclass()
class ConflictingKeyError(BaseKeyError):
    pass


@dc.dataclass()
class CyclicDependencyError(BaseKeyError):
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
