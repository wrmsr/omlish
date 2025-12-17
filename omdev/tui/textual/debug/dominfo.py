"""
TODO:
 - walk textual.styles.RulesMap lol
"""
import typing as ta

from textual.dom import DOMNode
from textual.widget import Widget

from omlish import dataclasses as dc

from ..types import trbl_to_dict


##


@dc.dataclass()
class DomNodeInfo:
    """Representation of a Textual DOM node for debugging."""

    # Identity
    oid: int
    oidx: str
    type: str
    dom_id: str | None

    # CSS / Styling
    classes: list[str]
    pseudo_classes: list[str]
    # 'styles' contains the computed values relevant to layout (margin, padding, etc)
    styles: dict[str, ta.Any]

    # Geometry
    # Region: The actual screen space allocated (x, y, w, h)
    region: dict[str, int] | None
    # Virtual Size: The size the widget 'wants' to be (scrollable area)
    virtual_size: dict[str, int] | None
    # Content Size: The size of the content inside the padding
    content_size: dict[str, int] | None

    # Hierarchy
    children: list['DomNodeInfo'] = dc.field(default_factory=list)


def inspect_dom_node(node: DOMNode) -> DomNodeInfo:
    """
    Recursively builds a tree of DomNodeInfo objects from a Textual DOM node.

    Args:
        node: The root node to inspect (usually app.screen or a specific widget).

    Returns:
        DomNodeInfo: The root of the inspected tree.
    """

    # 1. Identity

    oid = id(node)
    oidx = f'{id(node):x}'
    node_type = f'{type(node).__module__}.{type(node).__qualname__}'
    dom_id = node.id

    # 2. Styles

    # We extract specific computed styles relevant to positioning debugging. Textual 'styles' property usually returns
    # the computed/effective style.
    styles_info: dict[str, ta.Any] = {}

    # Extract only if the node supports styles (Most DOMNodes are Widgets, but check just in case)
    if isinstance(node, Widget):
        s = node.styles

        # Layout Rules
        styles_info['display'] = str(s.display)
        styles_info['position'] = str(s.position)  # relative, absolute
        styles_info['dock'] = str(s.dock)
        styles_info['layer'] = s.layer

        # Sizing Rules (The 'constraints' set in CSS)
        styles_info['width_rule'] = str(s.width)   # e.g. '100%', 'auto', '10'
        styles_info['height_rule'] = str(s.height)
        styles_info['min_width'] = str(s.min_width)
        styles_info['max_width'] = str(s.max_width)
        styles_info['box_sizing'] = str(s.box_sizing)  # border-box vs content-box

        # Spacing (Critical for debugging gaps)
        styles_info['margin'] = trbl_to_dict(s.margin)
        styles_info['padding'] = trbl_to_dict(s.padding)
        styles_info['border'] = trbl_to_dict(s.border)

        # Alignment
        styles_info['align'] = f'{s.align_horizontal} {s.align_vertical}'

    # 3. Geometry

    # Region is the absolute coordinates on the screen (or relative to parent layer). This is "What it was forced into".
    region_info: dict[str, int] | None = None
    if (region := getattr(node, 'region', None)) is not None:
        region_info = {
            'x': region.x,
            'y': region.y,
            'width': region.width,
            'height': region.height,
        }

    # Virtual size is the scrollable area. This is often "What it wants to be" (if larger than region).
    virtual_info: dict[str, int] | None = None
    if (virtual_size := getattr(node, 'virtual_size', None)) is not None:
        virtual_info = {
            'width': virtual_size.width,
            'height': virtual_size.height,
        }

    content_info: dict | None = None
    if isinstance(node, Widget):
        # Content region is inner size (region - padding - border)
        content_info = {
            'width': node.content_region.width,
            'height': node.content_region.height,
        }

    # 4. Recursion & Sorting

    # Sort by Y position first, then X position
    sorted_children = sorted(
        node.children,
        key=lambda n: (n.region.y, n.region.x),
    )

    child_nodes = [
        inspect_dom_node(child)
        for child in sorted_children
    ]

    return DomNodeInfo(
        oid=oid,
        oidx=oidx,
        type=node_type,
        dom_id=dom_id,

        classes=list(node.classes),
        pseudo_classes=list(node.pseudo_classes),
        styles=styles_info,

        region=region_info,
        virtual_size=virtual_info,
        content_size=content_info,

        children=child_nodes,
    )
