import io
import typing as ta

from omlish import dataclasses as dc
from omlish.text import templating as tpl

from ..containers import BlocksContent
from ..content import Content
from ..placeholders import PlaceholderContents
from ..text import TextContent
from ..transform.containers import JoinContainerContentsTransform
from ..transform.containers import UnnestContainersTransform
from ..transform.containers import UnwrapContainersTransform
from ..transform.lift import LiftToStandardContentTransform
from ..transform.materialize.namespaces import NamespaceContentMaterializer
from ..transform.materialize.placeholders import PlaceholderContentMaterializer
from ..transform.materialize.resources import ResourceContentMaterializer
from ..transform.materialize.templates import TemplateContentMaterializer
from ..transform.recursive import RecursiveContentTransform
from ..visitors import ContentVisitor
from .types import ContentStrRenderer


##


class StandardContentRenderer(ContentStrRenderer):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config:
        block_sep: str = '\n\n'

    @dc.dataclass(frozen=True, kw_only=True)
    class Context:
        placeholder_contents: PlaceholderContents | None = None
        templater_context: tpl.Templater.Context | None = None

    def __init__(self, config: Config | None = None) -> None:
        super().__init__()

        if config is None:
            config = self.Config()
        self._config = config

    class _Visitor(ContentVisitor[None, None]):
        def __init__(
                self,
                o: 'StandardContentRenderer',
                w: ta.Callable[[str], None],
        ) -> None:
            super().__init__()

            self.o = o
            self.w = w

        def visit_str(self, c: str, ctx: None) -> None:
            self.w(c)

        def visit_text_content(self, c: TextContent, ctx: None) -> None:
            self.w(c.s)

        def visit_blocks_content(self, c: BlocksContent, ctx: None) -> None:
            for i, x in enumerate(c.l):
                if i > 0:
                    self.w(self.o._config.block_sep)  # noqa
                self.visit(x, None)

    def _transform(self, c: Content, ctx: Context) -> Content:
        c = RecursiveContentTransform(
            LiftToStandardContentTransform(),
            NamespaceContentMaterializer(),
            PlaceholderContentMaterializer(ctx.placeholder_contents),
            ResourceContentMaterializer(),
            TemplateContentMaterializer(ctx.templater_context),
        ).transform(c)

        c = UnnestContainersTransform().transform(c)
        c = JoinContainerContentsTransform().transform(c)
        c = UnwrapContainersTransform().transform(c)

        return c

    def render(self, c: Content, ctx: Context | None = None) -> str:
        if ctx is None:
            ctx = self.Context()

        c = self._transform(c, ctx)

        out = io.StringIO()
        v = self._Visitor(self, ta.cast(ta.Any, out.write))
        v.visit(c, None)
        return out.getvalue()


##


def render_content_str(
        c: Content,
        *,
        placeholder_contents: PlaceholderContents | None = None,
        templater_context: tpl.Templater.Context | None = None,
) -> str:
    return StandardContentRenderer().render(
        c,
        StandardContentRenderer.Context(
            placeholder_contents=placeholder_contents,
            templater_context=templater_context,
        ),
    )
