import collections.abc
import typing as ta

from omlish import check

from ..containers import BlocksContent
from ..containers import ConcatContent
from ..containers import ContainerContent
from ..containers import FlowContent
from ..content import Content
from ..metadata import with_content_original
from ..text import TextContent
from .visitors import VisitorContentTransform


##


class LiftToStandardContentTransform(VisitorContentTransform):
    def __init__(
            self,
            *,
            container_mode: ta.Literal['flow', 'concat', 'blocks'] = 'flow',
    ) -> None:
        super().__init__()

        self._container_mode = container_mode

    def visit_str(self, s: str, ctx: None) -> Content:
        return with_content_original(TextContent(s), original=s)

    def visit_sequence(self, c: ta.Sequence[Content], ctx: None) -> ContainerContent:
        cc = check.isinstance(super().visit_sequence(c, ctx), collections.abc.Sequence)

        nc: ContainerContent
        match self._container_mode:
            case 'flow':
                nc = FlowContent(cc)
            case 'concat':
                nc = ConcatContent(cc)
            case 'blocks':
                nc = BlocksContent(cc)
            case _:
                raise ValueError(self._container_mode)

        return with_content_original(nc, original=c)
