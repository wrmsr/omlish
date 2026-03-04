"""
TODO:
 - use StandardContentVisitor
"""
import typing as ta

from omlish import check

from ..containers import ConcatContent
from ..containers import ContainerContent
from ..containers import FlowContent
from ..content import Content
from ..metadata import with_content_original
from ..standard import StandardContent
from ..text import TextContent  # noqa
from ..visitors import StandardContentVisitor
from .visitors import VisitorContentTransform


C = ta.TypeVar('C')


##


class UnnestContainersTransform(StandardContentVisitor[C, Content], VisitorContentTransform[C]):
    def visit_container_content(self, container: ContainerContent, ctx: C) -> Content:
        # First, recursively transform children via superclass
        nc = super().visit_container_content(container, ctx)
        if not isinstance(nc, ContainerContent):
            return nc

        # Now flatten any immediate children of the exact same type
        container_type = type(nc)
        children = nc.child_content()

        # Check if any children need unnesting
        if not any(isinstance(child, container_type) for child in children):
            return nc

        # Flatten same-type children
        flattened: list[Content] = []
        for child in children:
            if isinstance(child, container_type):
                # Extract the nested container's children
                flattened.extend(child.child_content())
            else:
                flattened.append(child)

        return nc.replace_child_content(flattened)


##


class UnwrapContainersTransform(StandardContentVisitor[C, Content], VisitorContentTransform[C]):
    def visit_container_content(self, container: ContainerContent, ctx: C) -> Content:
        # First, recursively transform children via superclass
        nc = super().visit_container_content(container, ctx)
        if not isinstance(nc, ContainerContent):
            return nc

        children = nc.child_content()
        if len(children) != 1:
            return nc

        single_child = check.isinstance(check.single(children), StandardContent)
        return with_content_original(single_child, original=nc)


##


class JoinContainerContentsTransform(StandardContentVisitor[C, Content], VisitorContentTransform[C]):
    def visit_flow_content(self, c: FlowContent, ctx: C) -> Content:
        nc = super().visit_flow_content(c, ctx)
        if not isinstance(nc, ContainerContent):
            return nc

        children = nc.child_content()
        if len(children) < 2:
            return nc

        if not any(
            isinstance(children[i], TextContent) and
            isinstance(children[i + 1], TextContent)
            for i in range(len(children) - 1)
        ):
            pass

        raise NotImplementedError

    def visit_concat_content(self, c: ConcatContent, ctx: C) -> Content:
        return super().visit_concat_content(c, ctx)
