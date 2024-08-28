import os

from ..testing.pytest import inject as pti


@pti.bind()
class Ci:
    @property
    def is_ci(self) -> bool:
        return 'CI' in os.environ
