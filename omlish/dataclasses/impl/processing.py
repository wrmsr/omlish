import typing as ta

from ... import lang


if ta.TYPE_CHECKING:
    from .reflect import ClassInfo


class Processor(lang.Abstract):
    def __init__(self, info: 'ClassInfo') -> None:
        super().__init__()
        self._cls = info.cls
        self._info = info

    def check(self) -> None:
        pass

    @lang.cached_function
    def process(self) -> None:
        self._process()

    def _process(self) -> None:
        raise NotImplementedError
