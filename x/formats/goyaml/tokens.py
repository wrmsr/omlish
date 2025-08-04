# ruff: noqa: UP006 UP007 UP043 UP045
import copy
import dataclasses as dc
import datetime
import enum
import functools
import typing as ta

from .errors import YamlError
from .errors import YamlErrorOr
from .errors import yaml_error


##


class Chars:
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


class Type(enum.Enum):
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


class CharType(enum.Enum):
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


class Indicator(enum.Enum):
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


def reserved_keyword_token(typ: Type, value: str, org: str, pos: 'Position') -> 'Token':
    return Token(
        type=typ,
        char_type=CharType.MISCELLANEOUS,
        indicator=Indicator.NOT,
        value=value,
        origin=org,
        position=pos,
    )


RESERVED_KEYWORD_MAP: ta.Mapping[str, ta.Callable[[str, str, 'Position'], 'Token']] = {
    **{keyword: functools.partial(reserved_keyword_token, Type.NULL) for keyword in RESERVED_NULL_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, Type.BOOL) for keyword in RESERVED_BOOL_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, Type.INFINITY) for keyword in RESERVED_INF_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, Type.NAN) for keyword in RESERVED_NAN_KEYWORDS},
}

# RESERVED_ENC_KEYWORD_MAP contains is the keyword map used at encoding time.
# This is supposed to be a superset of RESERVED_KEYWORD_MAP, and used to quote legacy keywords present in YAML 1.1 or
# lesser for compatibility reasons, even though this library is supposed to be YAML 1.2-compliant.
RESERVED_ENC_KEYWORD_MAP: ta.Mapping[str, ta.Callable[[str, str, 'Position'], 'Token']] = {
    **{keyword: functools.partial(reserved_keyword_token, Type.NULL) for keyword in RESERVED_NULL_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, Type.BOOL) for keyword in RESERVED_BOOL_KEYWORDS},
    **{keyword: functools.partial(reserved_keyword_token, Type.BOOL) for keyword in RESERVED_LEGACY_BOOL_KEYWORDS},
}


##


ReservedTagKeyword: ta.TypeAlias = str


class ReservedTagKeywords:
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
RESERVED_TAG_KEYWORD_MAP: ta.Mapping[ReservedTagKeyword, ta.Callable[[str, str, 'Position'], 'Token']] = {
    ReservedTagKeywords.INTEGER: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.FLOAT: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.NULL: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.SEQUENCE: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.MAPPING: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.STRING: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.BINARY: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.ORDERED_MAP: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.SET: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.TIMESTAMP: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.BOOLEAN: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
    ReservedTagKeywords.MERGE: lambda value, org, pos: Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    ),
}


##


class NumberType(enum.StrEnum):
    DECIMAL = 'decimal'
    BINARY = 'binary'
    OCTET = 'octet'
    HEX = 'hex'
    FLOAT = 'float'


@dc.dataclass(kw_only=True)
class NumberValue:
    type: NumberType
    value: ta.Any
    text: str


def to_number(value: str) -> ta.Optional[NumberValue]:
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


def _to_number(value: str) -> YamlErrorOr[ta.Optional[NumberValue]]:
    if not value:
        return None

    if value.startswith('_'):
        return None

    dot_count = value.count('.')
    if dot_count > 1:
        return None

    is_negative = value.startswith('-')
    normalized = value.lstrip('+').lstrip('-').replace('_', '')

    typ: NumberType
    base = 0

    if normalized.startswith('0x'):
        normalized = normalized.lstrip('0x')
        base = 16
        typ = NumberType.HEX
    elif normalized.startswith('0o'):
        normalized = normalized.lstrip('0o')
        base = 8
        typ = NumberType.OCTET
    elif normalized.startswith('0b'):
        normalized = normalized.lstrip('0b')
        base = 2
        typ = NumberType.BINARY
    elif normalized.startswith('0') and len(normalized) > 1 and dot_count == 0:
        base = 8
        typ = NumberType.OCTET
    elif dot_count == 1:
        typ = NumberType.FLOAT
    else:
        typ = NumberType.DECIMAL
        base = 10

    text = normalized
    if is_negative:
        text = '-' + text

    v: ta.Any
    if typ == NumberType.FLOAT:
        try:
            v = float(text)
        except ValueError as e:
            return YamlError(e)
    else:
        try:
            v = int(text, base)
        except ValueError as e:
            return YamlError(e)

    return NumberValue(
        type=typ,
        value=v,
        text=text,
    )


##


# This is a subset of the formats permitted by the regular expression defined at http:#yaml.org/type/timestamp.html.
# Note that time.Parse cannot handle: "2001-12-14 21:59:43.10 -5" from the examples.
TIMESTAMP_FORMATS = (
    '%Y-%m-%dT%H:%M:%S.%fZ',  # RFC3339Nano
    '%Y-%m-%dt%H:%M:%S.%fZ',  # RFC3339Nano with lower-case "t"
    '%Y-%m-%d %H:%M:%S',      # DateTime
    '%Y-%m-%d',               # DateOnly

    # Not in examples, but to preserve backward compatibility by quoting time values
    '%H:%M',
)

def _is_timestamp(value: str) -> bool:
    for format_str in TIMESTAMP_FORMATS:
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
            if i+1 < len(value) and value[i+1] == ' ':
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
def new(value: str, org: str, pos: 'Position') -> 'Token':
    fn = RESERVED_KEYWORD_MAP.get(value)
    if fn is not None:
        return fn(value, org, pos)

    if (num := to_number(value)) is not None:
        tk = Token(
            type=Type.INTEGER,
            char_type=CharType.MISCELLANEOUS,
            indicator=Indicator.NOT,
            value=value,
            origin=org,
            position=pos,
        )
        if num.type == NumberType.FLOAT:
            tk.type = Type.FLOAT
        elif num.type == NumberType.BINARY:
            tk.type = Type.BINARY_INTEGER
        elif num.type == NumberType.OCTET:
            tk.type = Type.OCTET_INTEGER
        elif num.type == NumberType.HEX:
            tk.type = Type.HEX_INTEGER
        return tk

    return new_string(value, org, pos)


# Position type for position in YAML document
@dc.dataclass(kw_only=True)
class Position:
    line: int
    column: int
    offset: int
    indent_num: int
    indent_level: int

    # String position to text
    def __str__(self) -> str:
        return f'[level:{self.indent_level:d},line:{self.line:d},column:{self.column:d},offset:{self.offset:d}]'


# Token type for token
@dc.dataclass(kw_only=True)
class Token:
    # Type is a token type.
    type: Type
    # CharType is a character type.
    char_type: CharType
    # Indicator is an indicator type.
    indicator: Indicator
    # Value is a string extracted with only meaningful characters, with spaces and such removed.
    value: str
    # Origin is a string that stores the original text as-is.
    origin: str
    # Error keeps error message for InvalidToken.
    error: ta.Optional[YamlError] = None
    # Position is a token position.
    position: Position
    # Next is a next token reference.
    next: ta.Optional['Token'] = dc.field(default=None, repr=False)
    # Prev is a previous token reference.
    prev: ta.Optional['Token'] = dc.field(default=None, repr=False)

    # previous_type previous token type
    def previous_type(self) -> Type:
        if self.prev is not None:
            return self.prev.type

        return Type.UNKNOWN

    # next_type next token type
    def next_type(self) -> Type:
        if self.next is not None:
            return self.next.type

        return Type.UNKNOWN

    # add_column append column number to current position of column
    @classmethod
    def add_column(cls, t: ta.Optional['Token'], col: int) -> None:
        if t is None:
            return

        t.position.column += col

    # clone copy token ( preserve Prev/Next reference )
    @classmethod
    def clone(cls, t: ta.Optional['Token']) -> ta.Optional['Token']:
        if t is None:
            return None

        copied = copy.copy(t)
        if t.position is not None:
            pos = copy.copy(t.position)
            copied.position = pos

        return copied


##


# Tokens type of token collection
class Tokens(ta.List[Token]):
    def invalid_token(self) -> ta.Optional[Token]:
        for tt in self:
            if tt.type == Type.INVALID:
                return tt
        return None

    def _add(self, tk: Token) -> None:
        if not self:
            self.append(tk)
        else:
            last = self[-1]
            last.next = tk
            tk.prev = last
            self.append(tk)

    # add append new some tokens
    def add(self, *tks: Token) -> None:
        for tk in tks:
            self._add(tk)


##


# new_string create token for String
def new_string(value: str, org: str, pos: Position) -> Token:
    return Token(
        type=Type.STRING,
        char_type=CharType.MISCELLANEOUS,
        indicator=Indicator.NOT,
        value=value,
        origin=org,
        position=pos,
    )


# new_sequence_entry create token for SequenceEntry
def new_sequence_entry(org: str, pos: Position) -> Token:
    return Token(
        type=Type.SEQUENCE_ENTRY,
        char_type=CharType.INDICATOR,
        indicator=Indicator.BLOCK_STRUCTURE,
        value=Chars.SEQUENCE_ENTRY,
        origin=org,
        position=pos,
    )


# new_mapping_key create token for MappingKey
def new_mapping_key(pos: Position) -> Token:
    return Token(
        type=Type.MAPPING_KEY,
        char_type=CharType.INDICATOR,
        indicator=Indicator.BLOCK_STRUCTURE,
        value=Chars.MAPPING_KEY,
        origin=Chars.MAPPING_KEY,
        position=pos,
    )


# new_mapping_value create token for MappingValue
def new_mapping_value(pos: Position) -> Token:
    return Token(
        type=Type.MAPPING_VALUE,
        char_type=CharType.INDICATOR,
        indicator=Indicator.BLOCK_STRUCTURE,
        value=Chars.MAPPING_VALUE,
        origin=Chars.MAPPING_VALUE,
        position=pos,
    )


# new_collect_entry create token for CollectEntry
def new_collect_entry(org: str, pos: Position) -> Token:
    return Token(
        type=Type.COLLECT_ENTRY,
        char_type=CharType.INDICATOR,
        indicator=Indicator.FLOW_COLLECTION,
        value=Chars.COLLECT_ENTRY,
        origin=org,
        position=pos,
    )


# new_sequence_start create token for SequenceStart
def new_sequence_start(org: str, pos: Position) -> Token:
    return Token(
        type=Type.SEQUENCE_START,
        char_type=CharType.INDICATOR,
        indicator=Indicator.FLOW_COLLECTION,
        value=Chars.SEQUENCE_START,
        origin=org,
        position=pos,
    )


# new_sequence_end create token for SequenceEnd
def new_sequence_end(org: str, pos: Position) -> Token:
    return Token(
        type=Type.SEQUENCE_END,
        char_type=CharType.INDICATOR,
        indicator=Indicator.FLOW_COLLECTION,
        value=Chars.SEQUENCE_END,
        origin=org,
        position=pos,
    )


# new_mapping_start create token for MappingStart
def new_mapping_start(org: str, pos: Position) -> Token:
    return Token(
        type=Type.MAPPING_START,
        char_type=CharType.INDICATOR,
        indicator=Indicator.FLOW_COLLECTION,
        value=Chars.MAPPING_START,
        origin=org,
        position=pos,
    )


# new_mapping_end create token for MappingEnd
def new_mapping_end(org: str, pos: Position) -> Token:
    return Token(
        type=Type.MAPPING_END,
        char_type=CharType.INDICATOR,
        indicator=Indicator.FLOW_COLLECTION,
        value=Chars.MAPPING_END,
        origin=org,
        position=pos,
    )


# new_comment create token for Comment
def new_comment(value: str, org: str, pos: Position) -> Token:
    return Token(
        type=Type.COMMENT,
        char_type=CharType.INDICATOR,
        indicator=Indicator.COMMENT,
        value=value,
        origin=org,
        position=pos,
    )


# new_anchor create token for Anchor
def new_anchor(org: str, pos: Position) -> Token:
    return Token(
        type=Type.ANCHOR,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=Chars.ANCHOR,
        origin=org,
        position=pos,
    )


# new_alias create token for Alias
def new_alias(org: str, pos: Position) -> Token:
    return Token(
        type=Type.ALIAS,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=Chars.ALIAS,
        origin=org,
        position=pos,
    )


# new_tag create token for Tag
def new_tag(value: str, org: str, pos: Position) -> Token:
    fn = RESERVED_TAG_KEYWORD_MAP.get(value)
    if fn is not None:
        return fn(value, org, pos)

    return Token(
        type=Type.TAG,
        char_type=CharType.INDICATOR,
        indicator=Indicator.NODE_PROPERTY,
        value=value,
        origin=org,
        position=pos,
    )


# new_literal create token for Literal
def new_literal(value: str, org: str, pos: Position) -> Token:
    return Token(
        type=Type.LITERAL,
        char_type=CharType.INDICATOR,
        indicator=Indicator.BLOCK_SCALAR,
        value=value,
        origin=org,
        position=pos,
    )


# new_folded create token for Folded
def new_folded(value: str, org: str, pos: Position) -> Token:
    return Token(
        type=Type.FOLDED,
        char_type=CharType.INDICATOR,
        indicator=Indicator.BLOCK_SCALAR,
        value=value,
        origin=org,
        position=pos,
    )


# new_single_quote create token for SingleQuote
def new_single_quote(value: str, org: str, pos: Position) -> Token:
    return Token(
        type=Type.SINGLE_QUOTE,
        char_type=CharType.INDICATOR,
        indicator=Indicator.QUOTED_SCALAR,
        value=value,
        origin=org,
        position=pos,
    )


# new_double_quote create token for DoubleQuote
def new_double_quote(value: str, org: str, pos: Position) -> Token:
    return Token(
        type=Type.DOUBLE_QUOTE,
        char_type=CharType.INDICATOR,
        indicator=Indicator.QUOTED_SCALAR,
        value=value,
        origin=org,
        position=pos,
    )


# new_directive create token for Directive
def new_directive(org: str, pos: Position) -> Token:
    return Token(
        type=Type.DIRECTIVE,
        char_type=CharType.INDICATOR,
        indicator=Indicator.DIRECTIVE,
        value=Chars.DIRECTIVE,
        origin=org,
        position=pos,
    )


# new_space create token for Space
def new_space(pos: Position) -> Token:
    return Token(
        type=Type.SPACE,
        char_type=CharType.WHITESPACE,
        indicator=Indicator.NOT,
        value=Chars.SPACE,
        origin=Chars.SPACE,
        position=pos,
    )


# new_merge_key create token for MergeKey
def new_merge_key(org: str, pos: Position) -> Token:
    return Token(
        type=Type.MERGE_KEY,
        char_type=CharType.MISCELLANEOUS,
        indicator=Indicator.NOT,
        value='<<',
        origin=org,
        position=pos,
    )


# new_document_header create token for DocumentHeader
def new_document_header(org: str, pos: Position) -> Token:
    return Token(
        type=Type.DOCUMENT_HEADER,
        char_type=CharType.MISCELLANEOUS,
        indicator=Indicator.NOT,
        value='---',
        origin=org,
        position=pos,
    )


# new_document_end create token for DocumentEnd
def new_document_end(org: str, pos: Position) -> Token:
    return Token(
        type=Type.DOCUMENT_END,
        char_type=CharType.MISCELLANEOUS,
        indicator=Indicator.NOT,
        value='...',
        origin=org,
        position=pos,
    )


def new_invalid(err: YamlError, org: str, pos: Position) -> Token:
    return Token(
        type=Type.INVALID,
        char_type=CharType.INVALID,
        indicator=Indicator.NOT,
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
