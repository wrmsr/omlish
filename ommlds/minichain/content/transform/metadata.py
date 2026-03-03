import typing as ta

from ..content import Content
from ..metadata import ContentOriginal
from ..standard import StandardContent
from .visitors import VisitorContentTransform


C = ta.TypeVar('C')


##


class OriginalMetadataStrippingContentTransform(VisitorContentTransform[C]):
    def visit_standard_content(self, c: StandardContent, ctx: C) -> StandardContent:
        return c.with_metadata(discard=[ContentOriginal])


def strip_content_original_metadata(c: Content) -> Content:
    return OriginalMetadataStrippingContentTransform[None]().transform(c, None)
