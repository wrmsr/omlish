# flake8: noqa
# type: ignore
from __future__ import annotations

from ... import api as dataclasses


class Foo:
    pass


@dataclasses.dataclass
class Bar:
    foo: Foo
