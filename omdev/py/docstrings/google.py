"""Google-style docstring parsing."""
import collections
import enum
import inspect
import re
import typing as ta

from .common import EXAMPLES_KEYWORDS
from .common import PARAM_KEYWORDS
from .common import RAISES_KEYWORDS
from .common import RETURNS_KEYWORDS
from .common import YIELDS_KEYWORDS
from .common import Docstring
from .common import DocstringExample
from .common import DocstringMeta
from .common import DocstringParam
from .common import DocstringRaises
from .common import DocstringReturns
from .common import DocstringStyle
from .common import ParseError


##


class SectionType(enum.IntEnum):
    """Types of sections."""

    SINGULAR = 0
    """For sections like examples."""

    MULTIPLE = 1
    """For sections like params."""

    SINGULAR_OR_MULTIPLE = 2
    """For sections like returns or yields."""


class Section(ta.NamedTuple):
    """A docstring section."""

    title: str
    key: str
    type: SectionType


_GOOGLE_TYPED_ARG_PAT = re.compile(r'\s*(.+?)\s*\(\s*(.*\S+)\s*\)')
_GOOGLE_ARG_DESC_PAT = re.compile(r'.*\. Defaults to (.+)\.')
_MULTIPLE_PATTERN = re.compile(r'(\s*[^:\s]+:)|([^:]*\]:.*)')

DEFAULT_SECTIONS = [
    Section('Arguments', 'param', SectionType.MULTIPLE),
    Section('Args', 'param', SectionType.MULTIPLE),
    Section('Parameters', 'param', SectionType.MULTIPLE),
    Section('Params', 'param', SectionType.MULTIPLE),
    Section('Raises', 'raises', SectionType.MULTIPLE),
    Section('Exceptions', 'raises', SectionType.MULTIPLE),
    Section('Except', 'raises', SectionType.MULTIPLE),
    Section('Attributes', 'attribute', SectionType.MULTIPLE),
    Section('Example', 'examples', SectionType.SINGULAR),
    Section('Examples', 'examples', SectionType.SINGULAR),
    Section('Returns', 'returns', SectionType.SINGULAR_OR_MULTIPLE),
    Section('Yields', 'yields', SectionType.SINGULAR_OR_MULTIPLE),
]


class GoogleParser:
    """Parser for Google-style docstrings."""

    def __init__(
            self,
            sections: list[Section] | None = None,
            *,
            title_colon: bool = True,
            meta_separators: ta.Sequence[str] = ':-',
    ) -> None:
        """
        Setup sections.

        :param sections: Recognized sections or None to defaults.
        :param title_colon: require colon after section title.
        """

        super().__init__()

        if not sections:
            sections = DEFAULT_SECTIONS
        self.sections = {s.title: s for s in sections}
        self.title_colon = title_colon
        self.meta_separators = meta_separators
        self._setup()

    def _setup(self) -> None:
        if self.title_colon:
            colon = ':'
        else:
            colon = ''

        self.titles_re = re.compile(
            '^(' +
            '|'.join(f'({t})' for t in self.sections) +
            ')' +
            colon +
            '[ \t\r\f\v]*$',
            flags=re.MULTILINE,
        )

    def _build_meta(self, text: str, title: str) -> DocstringMeta:
        """
        Build docstring element.

        :param text: docstring element text
        :param title: title of section containing element
        :return:
        """

        section = self.sections[title]

        if (
            (
                section.type == SectionType.SINGULAR_OR_MULTIPLE
                and not _MULTIPLE_PATTERN.match(text)
            ) or
            section.type == SectionType.SINGULAR
        ):
            return self._build_single_meta(section, text)

        seps = self.meta_separators
        for sep in seps:
            if sep not in text:
                continue

            # Split spec and description
            before, desc = text.split(sep, 1)
            if desc:
                desc = desc[1:] if desc[0] == ' ' else desc
                if '\n' in desc:
                    first_line, rest = desc.split('\n', 1)
                    desc = first_line + '\n' + inspect.cleandoc(rest)
                desc = desc.strip('\n')

            return self._build_multi_meta(section, before, desc)

        raise ParseError(f'Expected some separator {seps!r} in {text!r}.')

    @staticmethod
    def _build_single_meta(section: Section, desc: str) -> DocstringMeta:
        if section.key in RETURNS_KEYWORDS | YIELDS_KEYWORDS:
            return DocstringReturns(
                args=[section.key],
                description=desc,
                type_name=None,
                is_generator=section.key in YIELDS_KEYWORDS,
            )

        if section.key in RAISES_KEYWORDS:
            return DocstringRaises(
                args=[section.key],
                description=desc,
                type_name=None,
            )

        if section.key in EXAMPLES_KEYWORDS:
            return DocstringExample(
                args=[section.key],
                snippet=None,
                description=desc,
            )

        if section.key in PARAM_KEYWORDS:
            raise ParseError('Expected parameter name.')

        return DocstringMeta(args=[section.key], description=desc)

    @staticmethod
    def _build_multi_meta(
            section: Section,
            before: str,
            desc: str,
    ) -> DocstringMeta:
        if section.key in PARAM_KEYWORDS:
            match = _GOOGLE_TYPED_ARG_PAT.match(before)
            if match:
                arg_name, type_name = match.group(1, 2)
                if type_name.endswith(', optional'):
                    is_optional = True
                    type_name = type_name[:-10]
                elif type_name.endswith('?'):
                    is_optional = True
                    type_name = type_name[:-1]
                else:
                    is_optional = False
            else:
                arg_name, type_name = before, None
                is_optional = None

            match = _GOOGLE_ARG_DESC_PAT.match(desc)
            default = match.group(1) if match else None

            return DocstringParam(
                args=[section.key, before],
                description=desc,
                arg_name=arg_name,
                type_name=type_name,
                is_optional=is_optional,
                default=default,
            )
        if section.key in RETURNS_KEYWORDS | YIELDS_KEYWORDS:
            return DocstringReturns(
                args=[section.key, before],
                description=desc,
                type_name=before,
                is_generator=section.key in YIELDS_KEYWORDS,
            )
        if section.key in RAISES_KEYWORDS:
            return DocstringRaises(
                args=[section.key, before], description=desc, type_name=before,
            )
        return DocstringMeta(args=[section.key, before], description=desc)

    def add_section(self, section: Section) -> None:
        """
        Add or replace a section.

        :param section: The new section.
        """

        self.sections[section.title] = section
        self._setup()

    def parse(self, text: str) -> Docstring:
        """
        Parse the Google-style docstring into its components.

        :returns: parsed docstring
        """

        ret = Docstring(style=DocstringStyle.GOOGLE)
        if not text:
            return ret

        # Clean according to PEP-0257
        text = inspect.cleandoc(text)

        # Find first title and split on its position
        match = self.titles_re.search(text)
        if match:
            desc_chunk = text[: match.start()]
            meta_chunk = text[match.start():]
        else:
            desc_chunk = text
            meta_chunk = ''

        # Break description into short and long parts
        parts = desc_chunk.split('\n', 1)
        ret.short_description = parts[0] or None
        if len(parts) > 1:
            long_desc_chunk = parts[1] or ''
            ret.blank_after_short_description = long_desc_chunk.startswith('\n')
            ret.blank_after_long_description = long_desc_chunk.endswith('\n\n')
            ret.long_description = long_desc_chunk.strip() or None

        # Split by sections determined by titles
        matches = list(self.titles_re.finditer(meta_chunk))
        if not matches:
            return ret

        splits = []
        for j in range(len(matches) - 1):
            splits.append((matches[j].end(), matches[j + 1].start()))

        splits.append((matches[-1].end(), len(meta_chunk)))

        chunks = collections.OrderedDict()  # type: ta.MutableMapping[str,str]
        for j, (start, end) in enumerate(splits):
            title = matches[j].group(1)
            if title not in self.sections:
                continue

            # Clear Any Unknown Meta
            # Ref: https://github.com/rr-/docstring_parser/issues/29
            meta_details = meta_chunk[start:end]
            unknown_meta = re.search(r'\n\S', meta_details)
            if unknown_meta is not None:
                meta_details = meta_details[: unknown_meta.start()]

            chunks[title] = meta_details.strip('\n')

        if not chunks:
            return ret

        # Add elements from each chunk
        for title, chunk in chunks.items():
            # Determine indent
            indent_match = re.search(r'^\s*', chunk)
            if not indent_match:
                raise ParseError(f'Can\'t infer indent from "{chunk}"')

            indent = indent_match.group()

            # Check for singular elements
            if self.sections[title].type in [
                SectionType.SINGULAR,
                SectionType.SINGULAR_OR_MULTIPLE,
            ]:
                part = inspect.cleandoc(chunk)
                ret.meta.append(self._build_meta(part, title))
                continue

            # Split based on lines which have exactly that indent
            _re = '^' + indent + r'(?=\S)'

            c_matches = list(re.finditer(_re, chunk, flags=re.MULTILINE))
            if not c_matches:
                raise ParseError(f'No specification for "{title}": "{chunk}"')

            c_splits = []
            for j in range(len(c_matches) - 1):
                c_splits.append((c_matches[j].end(), c_matches[j + 1].start()))
            c_splits.append((c_matches[-1].end(), len(chunk)))

            for start, end in c_splits:
                part = chunk[start:end].strip('\n')
                ret.meta.append(self._build_meta(part, title))

        return ret


def parse(text: str) -> Docstring:
    """
    Parse the Google-style docstring into its components.

    :returns: parsed docstring
    """

    return GoogleParser().parse(text)
