from ....content.containers import BlocksContent
from ....content.containers import ConcatContent
from ....content.containers import FlowContent
from ....content.content import Content
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


def test_join_simple():
    a: Content = FlowContent([TextContent('a'), TextContent('b')])
    b: Content = JoinContainerContentsTransform[None]().transform(a, None)
    print(b)
