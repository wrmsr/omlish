import typing as ta

from omlish.formats import json

from ..code import BlockCodeContent
from ..code import InlineCodeContent
from ..json import JsonContent
from ..metadata import ContentOriginal
from ..standard import StandardContent
from ..text import TextContent
from .visitors import VisitorContentTransform


##


class JsonContentRenderer(VisitorContentTransform[None]):
    def __init__(
            self,
            *,
            backend: json.Backend | None = None,
            mode: ta.Literal['pretty', 'compact', 'normal'] = 'pretty',
            code: ta.Literal['inline', 'block', None] = None,
    ) -> None:
        super().__init__()

        if backend is None:
            backend = json.default_backend()
        self._backend = backend
        self._mode = mode
        self._code = code

    def visit_json_content(self, c: JsonContent, ctx: None) -> StandardContent:
        match self._mode:
            case 'pretty':
                s = self._backend.dumps_pretty(c.v)
            case 'compact':
                s = self._backend.dumps_compact(c.v)
            case 'normal':
                s = self._backend.dumps(c.v)
            case _:
                raise ValueError(self._mode)

        nc: StandardContent
        match self._code:
            case 'inline':
                nc = InlineCodeContent(s, lang='json')
            case 'block':
                nc = BlockCodeContent(s, lang='json')
            case None:
                nc = TextContent(s)
            case _:
                raise ValueError(self._code)

        return nc.with_metadata(ContentOriginal(c))
