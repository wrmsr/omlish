"""A fixture module whose annotations are all strings, for injection-inspection tests."""
from __future__ import annotations


##


class Foo:
    pass


class Bar:
    def __init__(self, foo: Foo) -> None:
        super().__init__()

        self.foo = foo
