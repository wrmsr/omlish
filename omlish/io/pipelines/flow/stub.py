import typing as ta

from .types import IoPipelineFlow


##


@ta.final
class StubIoPipelineFlow(IoPipelineFlow):
    def __init__(self, *, auto_read: bool = True) -> None:
        super().__init__()

        self._auto_read = auto_read

    def is_auto_read(self) -> bool:
        return self._auto_read
