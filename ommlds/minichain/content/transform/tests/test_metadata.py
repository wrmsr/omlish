import pytest

from ...metadata import ContentOriginal
from ...text import TextContent
from ..metadata import MetadataStrippingContentTransform


@pytest.mark.skip('FIXME')
def test_metadata():
    s = 'hi'
    tc = TextContent(s).update_metadata(ContentOriginal(s))
    xc = MetadataStrippingContentTransform().apply(tc)
    print(xc)
