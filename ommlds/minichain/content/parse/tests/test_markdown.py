import pytest

from ...blank import BlankContent
from ...code import BlockCodeContent
from ...code import InlineCodeContent
from ...containers import BlocksContent
from ...containers import FlowContent
from ...emphasis import BoldContent
from ...emphasis import BoldItalicContent
from ...emphasis import ItalicContent
from ...itemlist import ItemListContent
from ...link import LinkContent
from ...quote import QuoteContent
from ...section import SectionContent
from ...text import TextContent
from ..markdown import parse_markdown_content
from ..types import UnsupportedMarkdownError


##


class TestBasicText:
    def test_single_paragraph(self):
        result = parse_markdown_content('hello')
        assert result == TextContent('hello')

    def test_two_paragraphs(self):
        result = parse_markdown_content('hello\n\nworld')
        assert result == BlocksContent([
            TextContent('hello'),
            TextContent('world'),
        ])

    def test_softbreak(self):
        result = parse_markdown_content('hello\nworld')
        assert result == FlowContent([TextContent('hello'), TextContent('world')])

    def test_hardbreak(self):
        result = parse_markdown_content('a  \nb')
        assert result == FlowContent([TextContent('a'), BlankContent(), TextContent('b')])


class TestInlineFormatting:
    def test_inline_code(self):
        result = parse_markdown_content('`code`')
        assert result == InlineCodeContent('code')

    def test_bold(self):
        result = parse_markdown_content('**bold**')
        assert result == BoldContent('bold')

    def test_italic(self):
        result = parse_markdown_content('*italic*')
        assert result == ItalicContent('italic')

    def test_bold_italic(self):
        result = parse_markdown_content('***both***')
        assert result == BoldItalicContent('both')

    def test_mixed_inline(self):
        result = parse_markdown_content('hello **world**')
        assert result == FlowContent([TextContent('hello '), BoldContent('world')])

    def test_nested_emphasis_raises(self):
        with pytest.raises(UnsupportedMarkdownError):
            parse_markdown_content('**bold *nested* more**')

    def test_multiple_inline_elements(self):
        result = parse_markdown_content('a `b` *c*')
        assert result == FlowContent([
            TextContent('a '),
            InlineCodeContent('b'),
            TextContent(' '),
            ItalicContent('c'),
        ])


class TestLinks:
    def test_raw_link(self):
        result = parse_markdown_content('https://example.com')
        assert result == TextContent('https://example.com')

    def test_link_with_text(self):
        result = parse_markdown_content('[click here](https://example.com)')
        assert result == LinkContent('https://example.com', title='click here')

    def test_link_with_formatted_text_raises(self):
        with pytest.raises(UnsupportedMarkdownError):
            parse_markdown_content('[**bold**](https://example.com)')

    def test_link_inline_with_text(self):
        result = parse_markdown_content('see [here](https://example.com) for details')
        assert result == FlowContent([
            TextContent('see '),
            LinkContent('https://example.com', title='here'),
            TextContent(' for details'),
        ])


class TestBlockCode:
    def test_fenced_code_with_lang(self):
        result = parse_markdown_content('```python\ncode here\n```')
        assert result == BlockCodeContent('code here\n', lang='python')

    def test_fenced_code_no_lang(self):
        result = parse_markdown_content('```\ncode here\n```')
        assert result == BlockCodeContent('code here\n')

    def test_code_block_indented(self):
        result = parse_markdown_content('    code here\n')
        assert result == BlockCodeContent('code here\n')


class TestStructure:
    def test_heading(self):
        result = parse_markdown_content('# Title\n\nbody')
        assert result == SectionContent(
            TextContent('body'),
            header='Title',
        )

    def test_heading_only(self):
        result = parse_markdown_content('# Title')
        assert result == SectionContent(FlowContent([]), header='Title')

    def test_nested_headings(self):
        result = parse_markdown_content('# H1\n\n## H2\n\nbody')
        assert result == SectionContent(
            SectionContent(
                TextContent('body'),
                header='H2',
            ),
            header='H1',
        )

    def test_blockquote(self):
        result = parse_markdown_content('> quoted text')
        assert result == QuoteContent(TextContent('quoted text'))

    def test_bullet_list(self):
        result = parse_markdown_content('- a\n- b')
        assert result == ItemListContent(
            [TextContent('a'), TextContent('b')],
            style='-',
        )

    def test_ordered_list(self):
        result = parse_markdown_content('1. a\n2. b')
        assert result == ItemListContent(
            [TextContent('a'), TextContent('b')],
            style='#',
        )

    def test_horizontal_rule(self):
        result = parse_markdown_content('---')
        assert result == BlankContent()


class TestErrors:
    def test_image_raises(self):
        with pytest.raises(UnsupportedMarkdownError):
            parse_markdown_content('![alt](url)')

    def test_html_block_raises(self):
        with pytest.raises(UnsupportedMarkdownError):
            parse_markdown_content('<div>foo</div>')


class TestComplex:
    def test_paragraphs_with_code(self):
        src = 'Some text\n\n```python\nprint("hi")\n```\n\nMore text'
        result = parse_markdown_content(src)
        assert result == BlocksContent([
            TextContent('Some text'),
            BlockCodeContent('print("hi")\n', lang='python'),
            TextContent('More text'),
        ])

    def test_list_with_formatting(self):
        src = '- **bold item**\n- *italic item*'
        result = parse_markdown_content(src)
        assert result == ItemListContent(
            [
                BoldContent('bold item'),
                ItalicContent('italic item'),
            ],
            style='-',
        )

    def test_multiple_sections(self):
        src = '# First\n\nfoo\n\n# Second\n\nbar'
        result = parse_markdown_content(src)
        assert result == BlocksContent([
            SectionContent(TextContent('foo'), header='First'),
            SectionContent(TextContent('bar'), header='Second'),
        ])

    def test_section_with_multiple_blocks(self):
        src = '# Title\n\npara 1\n\npara 2'
        result = parse_markdown_content(src)
        assert result == SectionContent(
            BlocksContent([
                TextContent('para 1'),
                TextContent('para 2'),
            ]),
            header='Title',
        )
