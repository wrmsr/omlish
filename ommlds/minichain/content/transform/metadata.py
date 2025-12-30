from ..standard import StandardContent
from ..visitors import ContentTransform


##


class MetadataStrippingContentTransform(ContentTransform[None]):
    def visit_standard_content(self, c: StandardContent, ctx: None) -> StandardContent:
        raise NotImplementedError
