from ....content.code import InlineCodeContent
from ....content.containers import BlocksContent
from ....content.containers import ConcatContent
from ....content.containers import FlowContent
from ....content.itemlist import ItemListContent
from ....content.text import TextContent
from ..containers import JoinContainerContentsTransform
from ..containers import UnnestContainersTransform


def test_flow_content_simple_unnest():
    a = TextContent('a')
    b = TextContent('b')
    c = TextContent('c')

    # FlowContent([FlowContent([a, b]), c]) -> FlowContent([a, b, c])
    nested = FlowContent([FlowContent([a, b]), c])
    result = UnnestContainersTransform[None]().transform(nested, None)

    assert isinstance(result, FlowContent)
    assert list(result.l) == [a, b, c]


def test_flow_content_deep_nesting():
    a = TextContent('a')

    # FlowContent([FlowContent([FlowContent([a])])]) -> FlowContent([a])
    deeply_nested = FlowContent([FlowContent([FlowContent([a])])])
    result = UnnestContainersTransform[None]().transform(deeply_nested, None)

    assert isinstance(result, FlowContent)
    assert list(result.l) == [a]


def test_flow_content_multiple_nested():
    a = TextContent('a')
    b = TextContent('b')
    c = TextContent('c')

    # FlowContent([FlowContent([a]), FlowContent([b]), c]) -> FlowContent([a, b, c])
    nested = FlowContent([FlowContent([a]), FlowContent([b]), c])
    result = UnnestContainersTransform[None]().transform(nested, None)

    assert isinstance(result, FlowContent)
    assert list(result.l) == [a, b, c]


def test_flow_content_different_types_preserved():
    a = TextContent('a')
    b = TextContent('b')
    c = TextContent('c')

    # FlowContent([ConcatContent([a, b]), c]) -> unchanged
    mixed = FlowContent([ConcatContent([a, b]), c])
    result = UnnestContainersTransform[None]().transform(mixed, None)

    assert isinstance(result, FlowContent)
    assert len(result.l) == 2
    assert isinstance(result.l[0], ConcatContent)
    assert list(result.l[0].l) == [a, b]
    assert result.l[1] is c


def test_concat_content_unnest():
    a = TextContent('a')
    b = TextContent('b')

    # ConcatContent([ConcatContent([a]), b]) -> ConcatContent([a, b])
    nested = ConcatContent([ConcatContent([a]), b])
    result = UnnestContainersTransform[None]().transform(nested, None)

    assert isinstance(result, ConcatContent)
    assert list(result.l) == [a, b]


def test_blocks_content_unnest():
    a = TextContent('a')
    b = TextContent('b')

    # BlocksContent([BlocksContent([a]), b]) -> BlocksContent([a, b])
    nested = BlocksContent([BlocksContent([a]), b])
    result = UnnestContainersTransform[None]().transform(nested, None)

    assert isinstance(result, BlocksContent)
    assert list(result.l) == [a, b]


def test_item_list_content_not_unnested():
    a = TextContent('a')
    b = TextContent('b')

    # ItemListContent is SequenceContent but NOT ContainerContent, should not be unnested
    nested = ItemListContent([ItemListContent([a]), b])
    result = UnnestContainersTransform[None]().transform(nested, None)

    assert isinstance(result, ItemListContent)
    assert len(result.l) == 2
    assert isinstance(result.l[0], ItemListContent)
    assert list(result.l[0].l) == [a]
    assert result.l[1] is b


def test_no_change_when_no_nesting():
    a = TextContent('a')
    b = TextContent('b')

    # FlowContent([a, b]) -> unchanged
    flat = FlowContent([a, b])
    result = UnnestContainersTransform[None]().transform(flat, None)

    assert isinstance(result, FlowContent)
    assert list(result.l) == [a, b]
    assert result is flat  # Should be identity if no changes


def test_empty_nested_container():
    a = TextContent('a')

    # FlowContent([FlowContent([]), a]) -> FlowContent([a])
    nested = FlowContent([FlowContent([]), a])
    result = UnnestContainersTransform[None]().transform(nested, None)

    assert isinstance(result, FlowContent)
    assert list(result.l) == [a]


def test_mixed_nesting_levels():
    a = TextContent('a')
    b = TextContent('b')
    c = TextContent('c')
    d = TextContent('d')

    # FlowContent([a, FlowContent([b, FlowContent([c])]), d]) -> FlowContent([a, b, c, d])
    nested = FlowContent([a, FlowContent([b, FlowContent([c])]), d])
    result = UnnestContainersTransform[None]().transform(nested, None)

    assert isinstance(result, FlowContent)
    assert list(result.l) == [a, b, c, d]


def test_join_flow_simple():
    # FlowContent with adjacent TextContent -> joined with space-separated stripped text
    flow = FlowContent([TextContent('hello  '), TextContent('  world')])
    result = JoinContainerContentsTransform[None]().transform(flow, None)

    assert isinstance(result, FlowContent)
    assert len(result.l) == 1
    assert isinstance(result.l[0], TextContent)
    assert result.l[0].s == 'hello world'


def test_join_flow_multiple_spans():
    # Multiple spans of TextContent separated by non-TextContent
    flow = FlowContent([
        TextContent('hello  '),
        TextContent('  world'),
        InlineCodeContent('code'),
        TextContent('foo  '),
        TextContent('  bar  '),
        TextContent('  baz'),
    ])
    result = JoinContainerContentsTransform[None]().transform(flow, None)

    assert isinstance(result, FlowContent)
    assert len(result.l) == 3
    assert isinstance(result.l[0], TextContent)
    assert result.l[0].s == 'hello world'
    assert isinstance(result.l[1], InlineCodeContent)
    assert isinstance(result.l[2], TextContent)
    assert result.l[2].s == 'foo bar baz'


def test_join_flow_no_adjacent():
    # No adjacent TextContent -> no changes
    flow = FlowContent([
        TextContent('hello'),
        InlineCodeContent('code1'),
        TextContent('world'),
        InlineCodeContent('code2'),
    ])
    result = JoinContainerContentsTransform[None]().transform(flow, None)

    assert isinstance(result, FlowContent)
    assert result is flow  # Should be identity
    assert len(result.l) == 4


def test_join_concat_simple():
    # ConcatContent with adjacent TextContent -> joined with direct concatenation
    concat = ConcatContent([TextContent('hello  '), TextContent('  world')])
    result = JoinContainerContentsTransform[None]().transform(concat, None)

    assert isinstance(result, ConcatContent)
    assert len(result.l) == 1
    assert isinstance(result.l[0], TextContent)
    assert result.l[0].s == 'hello    world'  # Whitespace preserved


def test_join_concat_multiple_spans():

    # Multiple spans of TextContent separated by non-TextContent
    concat = ConcatContent([
        TextContent('hello  '),
        TextContent('  world'),
        InlineCodeContent('code'),
        TextContent('foo  '),
        TextContent('  bar'),
    ])
    result = JoinContainerContentsTransform[None]().transform(concat, None)

    assert isinstance(result, ConcatContent)
    assert len(result.l) == 3
    assert isinstance(result.l[0], TextContent)
    assert result.l[0].s == 'hello    world'  # Whitespace preserved
    assert isinstance(result.l[1], InlineCodeContent)
    assert isinstance(result.l[2], TextContent)
    assert result.l[2].s == 'foo    bar'  # Whitespace preserved


def test_join_single_child():
    # Single TextContent -> no changes
    flow = FlowContent([TextContent('hello')])
    result = JoinContainerContentsTransform[None]().transform(flow, None)

    assert result is flow  # Should be identity


def test_join_empty_text():
    # Adjacent TextContent including empty strings
    flow = FlowContent([
        TextContent('hello'),
        TextContent(''),
        TextContent('world'),
    ])
    result = JoinContainerContentsTransform[None]().transform(flow, None)

    assert isinstance(result, FlowContent)
    assert len(result.l) == 1
    assert isinstance(result.l[0], TextContent)
    # Empty string becomes '' after strip, but join still adds space between elements
    assert result.l[0].s == 'hello  world'


def test_join_all_text():
    # All children are TextContent -> single joined result
    concat = ConcatContent([
        TextContent('a'),
        TextContent('b'),
        TextContent('c'),
    ])
    result = JoinContainerContentsTransform[None]().transform(concat, None)

    assert isinstance(result, ConcatContent)
    assert len(result.l) == 1
    assert isinstance(result.l[0], TextContent)
    assert result.l[0].s == 'abc'
