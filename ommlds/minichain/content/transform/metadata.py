from ..standard import StandardContent
from .base import ContentTransform


##


class MetadataStrippingContentTransform(ContentTransform):
    @ContentTransform.apply.register
    def apply_standard_content(self, c: StandardContent) -> StandardContent:
        # return c.with
        raise NotImplementedError
