# type: ignore
# ruff: noqa
# flake8: noqa
from __future__ import annotations

from .... import dataclasses


class Foo:
    pass


@dataclasses.dataclass
class Bar:
    foo: Foo
