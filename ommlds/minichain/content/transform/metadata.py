from ..content import Content
from ..metadata import ContentOriginal
from ..standard import StandardContent
from ..visitors import ContentTransform


##


class OriginalMetadataStrippingContentTransform(ContentTransform[None]):
    def visit_standard_content(self, c: StandardContent, ctx: None) -> StandardContent:
        return c.discard_metadata(ContentOriginal)


def strip_content_original_metadata(c: Content) -> Content:
    return OriginalMetadataStrippingContentTransform().visit(c, None)
