import typing as ta

from omlish import lang


##


LAZY_DEFS_ATTR = '__dataclass_lazy_defs__'


class _LazyDefs:
    def __init__(self, lazy_globals: lang.LazyGlobals) -> None:
        super().__init__()

        self._lazy_globals = lazy_globals

    def get(self, attr: str) -> ta.Any:
        raise NotImplementedError
