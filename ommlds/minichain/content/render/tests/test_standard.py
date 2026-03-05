from ...containers import BlocksContent
from ...containers import FlowContent
from ...content import Content
from ...text import TextContent
from ..standard import StandardContentRenderer


def test_simple():
    c: Content
    for c in [
        FlowContent([TextContent('hi'), TextContent('there')]),
        BlocksContent([FlowContent([TextContent('hi'), TextContent('there')]), 'bye']),
    ]:
        print()
        print(c)
        s = StandardContentRenderer().render(c)
        print('=' * 40)
        print(s)
        print('=' * 40)
