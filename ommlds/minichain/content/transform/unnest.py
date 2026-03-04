import typing as ta

from ..containers import ContainerContent
from ..content import Content
from .visitors import VisitorContentTransform


C = ta.TypeVar('C')


##


class UnnestContainersTransform(VisitorContentTransform[C]):
    """
    Flattens redundant same-type container nesting.

    Examples:
        FlowContent([FlowContent([a, b]), c]) -> FlowContent([a, b, c])
        ConcatContent([ConcatContent([x])]) -> ConcatContent([x])
    """

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
