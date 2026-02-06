# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import copy
import dataclasses as dc
import datetime
import enum
import functools
import typing as ta

from omlish.lite.dataclasses import dataclass_field_required

from .errors import YamlError
from .errors import YamlErrorOr
from .errors import yaml_error


##


class YamlChars:
    # SEQUENCE_ENTRY character for sequence entry
    SEQUENCE_ENTRY = '-'
    # MAPPING_KEY character for mapping key
    MAPPING_KEY = '?'
    # MAPPING_VALUE character for mapping value
    MAPPING_VALUE = ':'
    # COLLECT_ENTRY character for collect entry
    COLLECT_ENTRY = ','
    # SEQUENCE_START character for sequence start
    SEQUENCE_START = '['
    # SEQUENCE_END character for sequence end
    SEQUENCE_END = ']'
    # MAPPING_START character for mapping start
    MAPPING_START = '{'
    # MAPPING_END character for mapping end
    MAPPING_END = '}'
    # COMMENT character for comment
    COMMENT = '#'
    # ANCHOR character for anchor
    ANCHOR = '&'
    # ALIAS character for alias
    ALIAS = '*'
    # TAG character for tag
    TAG = '!'
    # LITERAL character for literal
    LITERAL = '|'
    # FOLDED character for folded
    FOLDED = '>'
    # SINGLE_QUOTE character for single quote
    SINGLE_QUOTE = '\''
    # DOUBLE_QUOTE character for double quote
    DOUBLE_QUOTE = '"'
    # DIRECTIVE character for directive
    DIRECTIVE = '%'
    # SPACE character for space
    SPACE = ' '
    # LINE_BREAK character for line break
    LINE_BREAK = '\n'


class YamlTokenType(enum.Enum):
    # UNKNOWN reserve for invalid type
    UNKNOWN = enum.auto()
    # DOCUMENT_HEADER type for DocumentHeader token
    DOCUMENT_HEADER = enum.auto()
    # DOCUMENT_END type for DocumentEnd token
    DOCUMENT_END = enum.auto()
    # SEQUENCE_ENTRY type for SequenceEntry token
    SEQUENCE_ENTRY = enum.auto()
    # MAPPING_KEY type for MappingKey token
    MAPPING_KEY = enum.auto()
    # MAPPING_VALUE type for MappingValue token
    MAPPING_VALUE = enum.auto()
    # MERGE_KEY type for MergeKey token
    MERGE_KEY = enum.auto()
    # COLLECT_ENTRY type for CollectEntry token
    COLLECT_ENTRY = enum.auto()
    # SEQUENCE_START type for SequenceStart token
    SEQUENCE_START = enum.auto()
    # SEQUENCE_END type for SequenceEnd token
    SEQUENCE_END = enum.auto()
    # MAPPING_START type for MappingStart token
    MAPPING_START = enum.auto()
    # MAPPING_END type for MappingEnd token
    MAPPING_END = enum.auto()
    # COMMENT type for Comment token
    COMMENT = enum.auto()
    # ANCHOR type for Anchor token
    ANCHOR = enum.auto()
    # ALIAS type for Alias token
    ALIAS = enum.auto()
    # TAG type for Tag token
    TAG = enum.auto()
    # LITERAL type for Literal token
    LITERAL = enum.auto()
    # FOLDED type for Folded token
    FOLDED = enum.auto()
    # SINGLE_QUOTE type for SingleQuote token
    SINGLE_QUOTE = enum.auto()
    # DOUBLE_QUOTE type for DoubleQuote token
    DOUBLE_QUOTE = enum.auto()
    # DIRECTIVE type for Directive token
    DIRECTIVE = enum.auto()
    # SPACE type for Space token
    SPACE = enum.auto()
    # NULL type for Null token
    NULL = enum.auto()
    # IMPLICIT_NULL type for implicit Null token.
    # This is used when explicit keywords such as null or ~ are not specified. It is distinguished during encoding and
    # output as an empty string.
    IMPLICIT_NULL = enum.auto()
    # INFINITY type for Infinity token
    INFINITY = enum.auto()
    # NAN type for Nan token
    NAN = enum.auto()
    # INTEGER type for Integer token
    INTEGER = enum.auto()
    # BINARY_INTEGER type for BinaryInteger token
    BINARY_INTEGER = enum.auto()
    # OCTET_INTEGER type for OctetInteger token
    OCTET_INTEGER = enum.auto()
    # HEX_INTEGER type for HexInteger token
    HEX_INTEGER = enum.auto()
    # FLOAT type for Float token
    FLOAT = enum.auto()
    # STRING type for String token
    STRING = enum.auto()
    # BOOL type for Bool token
    BOOL = enum.auto()
    # INVALID type for invalid token
    INVALID = enum.auto()


class YamlCharType(enum.Enum):
    # INDICATOR type of indicator character
    INDICATOR = enum.auto()
    # WHITE-SPACE type of white space character
    WHITESPACE = enum.auto()
    # MISCELLANEOUS type of miscellaneous character
    MISCELLANEOUS = enum.auto()
    # ESCAPED type of escaped character
    ESCAPED = enum.auto()
    # INVALID type for an invalid token.
    INVALID = enum.auto()


class YamlIndicator(enum.Enum):
    # NOT not an indicator
    NOT = enum.auto()
    # BLOCK_STRUCTURE indicator for block structure ( '-', '?', ':' )
    BLOCK_STRUCTURE = enum.auto()
    # FLOW_COLLECTION indicator for flow collection ( '[', ']', '{', '}', ',' )
    FLOW_COLLECTION = enum.auto()
    # COMMENT indicator for comment ( '#' )
    COMMENT = enum.auto()
    # NODE_PROPERTY indicator for node property ( '!', '&', '*' )
    NODE_PROPERTY = enum.auto()
    # BLOCK_SCALAR indicator for block scalar ( '|', '>' )
    BLOCK_SCALAR = enum.auto()
    # QUOTED_SCALAR indicator for quoted scalar ( ''', '"' )
    QUOTED_SCALAR = enum.auto()
    # DIRECTIVE indicator for directive ( '%' )
    DIRECTIVE = enum.auto()
    # INVALID_USE_OF_RESERVED indicator for invalid use of reserved keyword ( '@', '`' )
    INVALID_USE_OF_RESERVED = enum.auto()


##


RESERVED_NULL_KEYWORDS = (
    'null',
    'Null',
    'NULL',
    '~',
)


RESERVED_BOOL_KEYWORDS = (
    'true',
    'True',
    'TRUE',
    'false',
    'False',
    'FALSE',
)


# For compatibility with other YAML 1.1 parsers.
# Note that we use these solely for encoding the bool value with quotes. go-yaml should not treat these as reserved
# keywords at parsing time. as go-yaml is supposed to be compliant only with YAML 1.2.
RESERVED_LEGACY_BOOL_KEYWORDS = (
    'y',
    'Y',
    'yes',
    'Yes',
    'YES',
    'n',
    'N',
    'no',
    'No',
    'NO',
    'on',
    'On',
    'ON',
    'off',
    'Off',
    'OFF',
)


RESERVED_INF_KEYWORDS = (
    '.inf',
    '.Inf',
    '.INF',
    '-.inf',
    '-.Inf',
    '-.INF',
)


RESERVED_NAN_KEYWORDS = (
    '.nan',
    '.NaN',
    '.NAN',
)


def reserved_keyword_token(typ: YamlTokenType, value: str, org: str, pos: 'YamlPosition') -> 'YamlToken':
    return YamlToken(
        type=typ,
        char_type=YamlCharType.MISCELLANEOUS,
        indicator=YamlIndicator.NOT,
        value=value,
        origin=org,
        position=pos,
    )


RESERVED_KEYWORD_MAP: ta.Mapping[str, ta.Callable[[str, str, 'YamlPosition'], 'YamlToken']] = {
    **{keyword: functools.partial(reserved_keyword_token, YamlTokenType.NULL) for keyword in RESERVED_NULL_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, YamlTokenType.BOOL) for keyword in RESERVED_BOOL_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, YamlTokenType.INFINITY) for keyword in RESERVED_INF_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, YamlTokenType.NAN) for keyword in RESERVED_NAN_KEYWORDS},
}


# RESERVED_ENC_KEYWORD_MAP contains is the keyword map used at encoding time.
# This is supposed to be a superset of RESERVED_KEYWORD_MAP, and used to quote legacy keywords present in YAML 1.1 or
# lesser for compatibility reasons, even though this library is supposed to be YAML 1.2-compliant.
RESERVED_ENC_KEYWORD_MAP: ta.Mapping[str, ta.Callable[[str, str, 'YamlPosition'], 'YamlToken']] = {
    **{keyword: functools.partial(reserved_keyword_token, YamlTokenType.NULL) for keyword in RESERVED_NULL_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, YamlTokenType.BOOL) for keyword in RESERVED_BOOL_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, YamlTokenType.BOOL) for keyword in RESERVED_LEGACY_BOOL_KEYWORDS},  # noqa
}


##


YamlReservedTagKeyword = str  # ta.TypeAlias  # omlish-amalg-typing-no-move


class YamlReservedTagKeywords:
    # INTEGER `!!int` tag
    INTEGER = '!!int'
    # FLOAT `!!float` tag
    FLOAT = '!!float'
    # NULL `!!null` tag
    NULL = '!!null'
    # SEQUENCE `!!seq` tag
    SEQUENCE = '!!seq'
    # MAPPING `!!map` tag
    MAPPING = '!!map'
    # STRING `!!str` tag
    STRING = '!!str'
    # BINARY `!!binary` tag
    BINARY = '!!binary'
    # ORDERED_MAP `!!omap` tag
    ORDERED_MAP = '!!omap'
    # SET `!!set` tag
    SET = '!!set'
    # TIMESTAMP `!!timestamp` tag
    TIMESTAMP = '!!timestamp'
    # BOOLEAN `!!bool` tag
    BOOLEAN = '!!bool'
    # MERGE `!!merge` tag
    MERGE = '!!merge'


# RESERVED_TAG_KEYWORD_MAP map for reserved tag keywords
YAML_RESERVED_TAG_KEYWORD_MAP: ta.Mapping[YamlReservedTagKeyword, ta.Callable[[str, str, 'YamlPosition'], 'YamlToken']] = {  # noqa
    YamlReservedTagKeywords.INTEGER: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.FLOAT: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.NULL: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.SEQUENCE: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.MAPPING: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.STRING: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.BINARY: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.ORDERED_MAP: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.SET: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.TIMESTAMP: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.BOOLEAN: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    YamlReservedTagKeywords.MERGE: lambda value, org, pos: YamlToken(
        type=YamlTokenType.TAG,
        char_type=YamlCharType.INDICATOR,
        indicator=YamlIndicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
}


##


class YamlNumberType(enum.Enum):
    DECIMAL = 'decimal'
    BINARY = 'binary'
    OCTET = 'octet'
    HEX = 'hex'
    FLOAT = 'float'


@dc.dataclass()
class YamlNumberValue:
    type: YamlNumberType
    value: ta.Any
    text: str


def to_number(value: str) -> ta.Optional[YamlNumberValue]:
    num = _to_number(value)
    if isinstance(num, YamlError):
        return None

    return num


def _is_number(value: str) -> bool:
    num = _to_number(value)
    if isinstance(num, YamlError):
        # var numErr *strconv.NumError
        # if errors.As(err, &numErr) && errors.Is(numErr.Err, strconv.ErrRange) {
        #     return true

        return False

    return num is not None


def _to_number(value: str) -> YamlErrorOr[ta.Optional[YamlNumberValue]]:
    if not value:
        return None

    if value.startswith('_'):
        return None

    dot_count = value.count('.')
    if dot_count > 1:
        return None

    is_negative = value.startswith('-')
    normalized = value.lstrip('+').lstrip('-').replace('_', '')

    typ: YamlNumberType
    base = 0

    if normalized.startswith('0x'):
        normalized = normalized.lstrip('0x')
        base = 16
        typ = YamlNumberType.HEX
    elif normalized.startswith('0o'):
        normalized = normalized.lstrip('0o')
        base = 8
        typ = YamlNumberType.OCTET
    elif normalized.startswith('0b'):
        normalized = normalized.lstrip('0b')
        base = 2
        typ = YamlNumberType.BINARY
    elif normalized.startswith('0') and len(normalized) > 1 and dot_count == 0:
        base = 8
        typ = YamlNumberType.OCTET
    elif dot_count == 1:
        typ = YamlNumberType.FLOAT
    else:
        typ = YamlNumberType.DECIMAL
        base = 10

    text = normalized
    if is_negative:
        text = '-' + text

    v: ta.Any
    if typ == YamlNumberType.FLOAT:
        try:
            v = float(text)
        except ValueError as e:
            return yaml_error(e)
    else:
        try:
            v = int(text, base)
        except ValueError as e:
            return yaml_error(e)

    return YamlNumberValue(
        type=typ,
        value=v,
        text=text,
    )


##


# This is a subset of the formats permitted by the regular expression defined at http:#yaml.org/type/timestamp.html.
# Note that time.Parse cannot handle: "2001-12-14 21:59:43.10 -5" from the examples.
YAML_TIMESTAMP_FORMATS = (
    '%Y-%m-%dT%H:%M:%S.%fZ',  # RFC3339Nano
    '%Y-%m-%dt%H:%M:%S.%fZ',  # RFC3339Nano with lower-case "t"
    '%Y-%m-%d %H:%M:%S',      # DateTime
    '%Y-%m-%d',               # DateOnly

    # Not in examples, but to preserve backward compatibility by quoting time values
    '%H:%M',
)


def _is_timestamp(value: str) -> bool:
    for format_str in YAML_TIMESTAMP_FORMATS:
        try:
            datetime.datetime.strptime(value, format_str)  # noqa
            return True
        except ValueError:
            continue
    return False


##


# is_need_quoted checks whether the value needs quote for passed string or not
def is_need_quoted(value: str) -> bool:
    if not value:
        return True

    if value in RESERVED_ENC_KEYWORD_MAP:
        return True

    if _is_number(value):
        return True

    if value == '-':
        return True

    if value[0] in ('*', '&', '[', '{', '}', ']', ',', '!', '|', '>', '%', '\'', '"', '@', ' ', '`'):
        return True

    if value[-1] in (':', ' '):
        return True

    if _is_timestamp(value):
        return True

    for i, c in enumerate(value):
        if c in ('#', '\\'):
            return True
        elif c in (':', '-'):
            if i + 1 < len(value) and value[i + 1] == ' ':
                return True

    return False


# literal_block_header detect literal block scalar header
def literal_block_header(value: str) -> str:
    lbc = detect_line_break_char(value)

    if lbc not in value:
        return ''
    elif value.endswith(lbc + lbc):
        return '|+'
    elif value.endswith(lbc):
        return '|'
    else:
        return '|-'


##


# new create reserved keyword token or number token and other string token.
def new_yaml_token(value: str, org: str, pos: 'YamlPosition') -> 'YamlToken':
    fn = RESERVED_KEYWORD_MAP.get(value)
    if fn is not None:
        return fn(value, org, pos)

    if (num := to_number(value)) is not None:
        tk = YamlToken(
            type=YamlTokenType.INTEGER,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value=value,
            origin=org,
            position=pos,
        )
        if num.type == YamlNumberType.FLOAT:
            tk.type = YamlTokenType.FLOAT
        elif num.type == YamlNumberType.BINARY:
            tk.type = YamlTokenType.BINARY_INTEGER
        elif num.type == YamlNumberType.OCTET:
            tk.type = YamlTokenType.OCTET_INTEGER
        elif num.type == YamlNumberType.HEX:
            tk.type = YamlTokenType.HEX_INTEGER
        return tk

    return YamlTokenMakers.new_string(value, org, pos)


# Position type for position in YAML document
@dc.dataclass()
class YamlPosition:
    line: int
    column: int
    offset: int
    indent_num: int
    indent_level: int

    # String position to text
    def __str__(self) -> str:
        return f'[level:{self.indent_level:d},line:{self.line:d},column:{self.column:d},offset:{self.offset:d}]'


# Token type for token
@dc.dataclass()
@ta.final
class YamlToken:
    # Type is a token type.
    type: YamlTokenType
    # CharType is a character type.
    char_type: YamlCharType
    # Indicator is an indicator type.
    indicator: YamlIndicator
    # Value is a string extracted with only meaningful characters, with spaces and such removed.
    value: str
    # Origin is a string that stores the original text as-is.
    origin: str
    # Error keeps error message for InvalidToken.
    error: ta.Optional[YamlError] = None
    # Position is a token position.
    position: YamlPosition = dc.field(default_factory=dataclass_field_required('position'))
    # Next is a next token reference.
    next: ta.Optional['YamlToken'] = dc.field(default=None, repr=False)
    # Prev is a previous token reference.
    prev: ta.Optional['YamlToken'] = dc.field(default=None, repr=False)

    # previous_type previous token type
    def previous_type(self) -> YamlTokenType:
        if self.prev is not None:
            return self.prev.type

        return YamlTokenType.UNKNOWN

    # next_type next token type
    def next_type(self) -> YamlTokenType:
        if self.next is not None:
            return self.next.type

        return YamlTokenType.UNKNOWN

    # add_column append column number to current position of column
    @classmethod
    def add_column(cls, t: ta.Optional['YamlToken'], col: int) -> None:
        if t is None:
            return

        t.position.column += col

    # clone copy token ( preserve Prev/Next reference )
    @classmethod
    def clone(cls, t: ta.Optional['YamlToken']) -> ta.Optional['YamlToken']:
        if t is None:
            return None

        copied = copy.copy(t)
        if t.position is not None:
            pos = copy.copy(t.position)
            copied.position = pos

        return copied


##


# Tokens type of token collection
class YamlTokens(ta.List[YamlToken]):
    def invalid_token(self) -> ta.Optional[YamlToken]:
        for tt in self:
            if tt.type == YamlTokenType.INVALID:
                return tt
        return None

    def _add(self, tk: YamlToken) -> None:
        if not self:
            self.append(tk)
        else:
            last = self[-1]
            last.next = tk
            tk.prev = last
            self.append(tk)

    # add append new some tokens
    def add(self, *tks: YamlToken) -> None:
        for tk in tks:
            self._add(tk)


##


class YamlTokenMakers:  # noqa
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    # new_string create token for String
    @staticmethod
    def new_string(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.STRING,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value=value,
            origin=org,
            position=pos,
        )

    # new_sequence_entry create token for SequenceEntry
    @staticmethod
    def new_sequence_entry(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SEQUENCE_ENTRY,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_STRUCTURE,
            value=YamlChars.SEQUENCE_ENTRY,
            origin=org,
            position=pos,
        )

    # new_mapping_key create token for MappingKey
    @staticmethod
    def new_mapping_key(pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_KEY,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_STRUCTURE,
            value=YamlChars.MAPPING_KEY,
            origin=YamlChars.MAPPING_KEY,
            position=pos,
        )

    # new_mapping_value create token for MappingValue
    @staticmethod
    def new_mapping_value(pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_VALUE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_STRUCTURE,
            value=YamlChars.MAPPING_VALUE,
            origin=YamlChars.MAPPING_VALUE,
            position=pos,
        )

    # new_collect_entry create token for CollectEntry
    @staticmethod
    def new_collect_entry(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.COLLECT_ENTRY,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.COLLECT_ENTRY,
            origin=org,
            position=pos,
        )

    # new_sequence_start create token for SequenceStart
    @staticmethod
    def new_sequence_start(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SEQUENCE_START,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.SEQUENCE_START,
            origin=org,
            position=pos,
        )

    # new_sequence_end create token for SequenceEnd
    @staticmethod
    def new_sequence_end(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SEQUENCE_END,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.SEQUENCE_END,
            origin=org,
            position=pos,
        )

    # new_mapping_start create token for MappingStart
    @staticmethod
    def new_mapping_start(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_START,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.MAPPING_START,
            origin=org,
            position=pos,
        )

    # new_mapping_end create token for MappingEnd
    @staticmethod
    def new_mapping_end(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MAPPING_END,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.FLOW_COLLECTION,
            value=YamlChars.MAPPING_END,
            origin=org,
            position=pos,
        )

    # new_comment create token for Comment
    @staticmethod
    def new_comment(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.COMMENT,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.COMMENT,
            value=value,
            origin=org,
            position=pos,
        )

    # new_anchor create token for Anchor
    @staticmethod
    def new_anchor(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.ANCHOR,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.NODE_PROPERTY,
            value=YamlChars.ANCHOR,
            origin=org,
            position=pos,
        )

    # new_alias create token for Alias
    @staticmethod
    def new_alias(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.ALIAS,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.NODE_PROPERTY,
            value=YamlChars.ALIAS,
            origin=org,
            position=pos,
        )

    # new_tag create token for Tag
    @staticmethod
    def new_tag(value: str, org: str, pos: YamlPosition) -> YamlToken:
        fn = YAML_RESERVED_TAG_KEYWORD_MAP.get(value)
        if fn is not None:
            return fn(value, org, pos)

        return YamlToken(
            type=YamlTokenType.TAG,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.NODE_PROPERTY,
            value=value,
            origin=org,
            position=pos,
        )

    # new_literal create token for Literal
    @staticmethod
    def new_literal(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.LITERAL,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_folded create token for Folded
    @staticmethod
    def new_folded(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.FOLDED,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.BLOCK_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_single_quote create token for SingleQuote
    @staticmethod
    def new_single_quote(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SINGLE_QUOTE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.QUOTED_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_double_quote create token for DoubleQuote
    @staticmethod
    def new_double_quote(value: str, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DOUBLE_QUOTE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.QUOTED_SCALAR,
            value=value,
            origin=org,
            position=pos,
        )

    # new_directive create token for Directive
    @staticmethod
    def new_directive(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DIRECTIVE,
            char_type=YamlCharType.INDICATOR,
            indicator=YamlIndicator.DIRECTIVE,
            value=YamlChars.DIRECTIVE,
            origin=org,
            position=pos,
        )

    # new_space create token for Space
    @staticmethod
    def new_space(pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.SPACE,
            char_type=YamlCharType.WHITESPACE,
            indicator=YamlIndicator.NOT,
            value=YamlChars.SPACE,
            origin=YamlChars.SPACE,
            position=pos,
        )

    # new_merge_key create token for MergeKey
    @staticmethod
    def new_merge_key(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.MERGE_KEY,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value='<<',
            origin=org,
            position=pos,
        )

    # new_document_header create token for DocumentHeader
    @staticmethod
    def new_document_header(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DOCUMENT_HEADER,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value='---',
            origin=org,
            position=pos,
        )

    # new_document_end create token for DocumentEnd
    @staticmethod
    def new_document_end(org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.DOCUMENT_END,
            char_type=YamlCharType.MISCELLANEOUS,
            indicator=YamlIndicator.NOT,
            value='...',
            origin=org,
            position=pos,
        )

    @staticmethod
    def new_invalid(err: YamlError, org: str, pos: YamlPosition) -> YamlToken:
        return YamlToken(
            type=YamlTokenType.INVALID,
            char_type=YamlCharType.INVALID,
            indicator=YamlIndicator.NOT,
            value=org,
            origin=org,
            error=err,
            position=pos,
        )


##


# detect_line_break_char detect line break character in only one inside scalar content scope.
def detect_line_break_char(src: str) -> str:
    nc = src.count('\n')
    rc = src.count('\r')
    rnc = src.count('\r\n')
    if nc == rnc and rc == rnc:
        return '\r\n'
    elif rc > nc:
        return '\r'
    else:
        return '\n'
