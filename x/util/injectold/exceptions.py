import dataclasses as dc
import typing as ta

from .types import Key


@dc.dataclass(frozen=True)
class KeyException(Exception):
    key: Key

    source: ta.Any = None
    name: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class UnboundKeyException(KeyException):
    pass


@dc.dataclass(frozen=True)
class DuplicateKeyException(KeyException):
    pass
