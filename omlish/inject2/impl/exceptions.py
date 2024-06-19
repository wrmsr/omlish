import typing as ta

from .. import dataclasses as dc
from .types import Key


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
