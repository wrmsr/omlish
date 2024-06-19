from ... import lang
from .reflect import ClassInfo


class Processor(lang.Abstract):
    def __init__(self, info: ClassInfo) -> None:
        super().__init__()
        self._cls = info.cls
        self._info = info

    @lang.cached_function
    def process(self) -> None:
        self._process()

    def _process(self) -> None:
        raise NotImplementedError
