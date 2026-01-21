from ..content import Content
from ..metadata import ContentOriginal
from ..standard import StandardContent
from .visitors import VisitorContentTransform


##


class OriginalMetadataStrippingContentTransform(VisitorContentTransform[None]):
    def visit_standard_content(self, c: StandardContent, ctx: None) -> StandardContent:
        return c.with_metadata(discard=[ContentOriginal])


def strip_content_original_metadata(c: Content) -> Content:
    return OriginalMetadataStrippingContentTransform().transform(c, None)
