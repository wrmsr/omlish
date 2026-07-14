import typing as ta

from ..core import IoPipelineService
from .types import IoPipelineFlow


##


@ta.final
class StubIoPipelineFlowService(IoPipelineFlow, IoPipelineService):
    def __init__(self, *, auto_read: bool = True) -> None:
        super().__init__()

        self._auto_read = auto_read

    def is_auto_read(self) -> bool:
        return self._auto_read
