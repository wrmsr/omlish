import typing as ta  # noqa

from ...testing.pytest import inject as pti
from ..dbs import DbSpec


@pti.bind('function')
class Dbs:
    def specs(self) -> list[DbSpec]:
        return []
