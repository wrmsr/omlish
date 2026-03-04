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
from ..metadata import ContentOriginal
from ..standard import StandardContent
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
        return single_child.with_metadata(ContentOriginal(nc))


##


class JoinContainerContentsTransform(StandardContentVisitor[C, Content], VisitorContentTransform[C]):
    def visit_flow_content(self, c: FlowContent, ctx: C) -> Content:
        return super().visit_flow_content(c, ctx)

    def visit_concat_content(self, c: ConcatContent, ctx: C) -> Content:
        return super().visit_concat_content(c, ctx)
