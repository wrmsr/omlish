from ..content import Content
from ..metadata import ContentOriginal
from ..standard import StandardContent
from .visitors import VisitorContentTransform


##


class OriginalMetadataStrippingContentTransform(VisitorContentTransform):
    def visit_standard_content(self, c: StandardContent, ctx: None) -> StandardContent:
        return c._with_metadata(discard=[ContentOriginal])  # noqa


def strip_content_original_metadata(c: Content) -> Content:
    return OriginalMetadataStrippingContentTransform().transform(c)
