from ...content import Content
from ...metadata import ContentOriginal
from ...text import TextContent
from ..metadata import strip_content_original_metadata


def test_metadata():
    s = 'hi'
    c: Content = TextContent(s).with_metadata(ContentOriginal(s))

    xc = strip_content_original_metadata(c)
    print(xc)
