# ruff: noqa: UP045
"""A fixture module whose annotations are all strings, for injection-inspection and marshaling tests."""
from __future__ import annotations

import dataclasses as dc
import typing as ta


##


class Foo:
    pass


class Bar:
    def __init__(self, foo: Foo) -> None:
        super().__init__()

        self.foo = foo


##


@dc.dataclass
class FutPoint:
    x: int
    y: ta.Optional[str] = None


class FutNt(ta.NamedTuple):
    a: int
    b: str
