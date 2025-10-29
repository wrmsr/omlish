# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import abc
import dataclasses as dc
import enum
import io
import typing as ta
import unicodedata

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.dataclasses import dataclass_field_required

from . import tokens
from .errors import EofYamlError
from .errors import YamlError
from .errors import YamlErrorOr
from .errors import yaml_error
from .tokens import YamlNumberType
from .tokens import YamlPosition
from .tokens import YamlToken
from .tokens import YamlTokenType


##


ERR_INVALID_TOKEN_TYPE = yaml_error('invalid token type')
ERR_INVALID_ANCHOR_NAME = yaml_error('invalid anchor name')
ERR_INVALID_ALIAS_NAME = yaml_error('invalid alias name')


class YamlNodeType(enum.Enum):
    # UNKNOWN type identifier for default
    UNKNOWN = enum.auto()
    # DOCUMENT type identifier for document node
    DOCUMENT = enum.auto()
    # NULL type identifier for null node
    NULL = enum.auto()
    # BOOL type identifier for boolean node
    BOOL = enum.auto()
    # INTEGER type identifier for integer node
    INTEGER = enum.auto()
    # FLOAT type identifier for float node
    FLOAT = enum.auto()
    # INFINITY type identifier for infinity node
    INFINITY = enum.auto()
    # NAN type identifier for nan node
    NAN = enum.auto()
    # STRING type identifier for string node
    STRING = enum.auto()
    # MERGE_KEY type identifier for merge key node
    MERGE_KEY = enum.auto()
    # LITERAL type identifier for literal node
    LITERAL = enum.auto()
    # MAPPING type identifier for mapping node
    MAPPING = enum.auto()
    # MAPPING_KEY type identifier for mapping key node
    MAPPING_KEY = enum.auto()
    # MAPPING_VALUE type identifier for mapping value node
    MAPPING_VALUE = enum.auto()
    # SEQUENCE type identifier for sequence node
    SEQUENCE = enum.auto()
    # SEQUENCE_ENTRY type identifier for sequence entry node
    SEQUENCE_ENTRY = enum.auto()
    # ANCHOR type identifier for anchor node
    ANCHOR = enum.auto()
    # ALIAS type identifier for alias node
    ALIAS = enum.auto()
    # DIRECTIVE type identifier for directive node
    DIRECTIVE = enum.auto()
    # TAG type identifier for tag node
    TAG = enum.auto()
    # COMMENT type identifier for comment node
    COMMENT = enum.auto()
    # COMMENT_GROUP type identifier for comment group node
    COMMENT_GROUP = enum.auto()


# String node type identifier to YAML Structure name based on https://yaml.org/spec/1.2/spec.html
YAML_NODE_TYPE_YAML_NAMES: ta.Mapping[YamlNodeType, str] = {
    YamlNodeType.UNKNOWN: 'unknown',
    YamlNodeType.DOCUMENT: 'document',
    YamlNodeType.NULL: 'null',
    YamlNodeType.BOOL: 'boolean',
    YamlNodeType.INTEGER: 'int',
    YamlNodeType.FLOAT: 'float',
    YamlNodeType.INFINITY: 'inf',
    YamlNodeType.NAN: 'nan',
    YamlNodeType.STRING: 'string',
    YamlNodeType.MERGE_KEY: 'merge key',
    YamlNodeType.LITERAL: 'scalar',
    YamlNodeType.MAPPING: 'mapping',
    YamlNodeType.MAPPING_KEY: 'key',
    YamlNodeType.MAPPING_VALUE: 'value',
    YamlNodeType.SEQUENCE: 'sequence',
    YamlNodeType.SEQUENCE_ENTRY: 'value',
    YamlNodeType.ANCHOR: 'anchor',
    YamlNodeType.ALIAS: 'alias',
    YamlNodeType.DIRECTIVE: 'directive',
    YamlNodeType.TAG: 'tag',
    YamlNodeType.COMMENT: 'comment',
    YamlNodeType.COMMENT_GROUP: 'comment',
}


##


# Node type of node
class YamlNode(Abstract):
    # io.Reader

    def __str__(self) -> ta.NoReturn:
        raise TypeError

    @abc.abstractmethod
    def string(self) -> str:
        # FIXME: migrate off - ensure all sprintfy things explicitly call .string()
        raise NotImplementedError

    # get_token returns token instance
    @abc.abstractmethod
    def get_token(self) -> ta.Optional[YamlToken]:
        raise NotImplementedError

    # type returns type of node
    @abc.abstractmethod
    def type(self) -> YamlNodeType:
        raise NotImplementedError

    # add_column add column number to child nodes recursively
    @abc.abstractmethod
    def add_column(self, column: int) -> None:
        raise NotImplementedError

    # set_comment set comment token to node
    @abc.abstractmethod
    def set_comment(self, node: ta.Optional['CommentGroupYamlNode']) -> ta.Optional[YamlError]:
        raise NotImplementedError

    # comment returns comment token instance
    @abc.abstractmethod
    def get_comment(self) -> ta.Optional['CommentGroupYamlNode']:
        raise NotImplementedError

    # get_path returns YAMLPath for the current node
    @abc.abstractmethod
    def get_path(self) -> str:
        raise NotImplementedError

    # set_path set YAMLPath for the current node
    @abc.abstractmethod
    def set_path(self, path: str) -> None:
        raise NotImplementedError

    # marshal_yaml
    @abc.abstractmethod
    def marshal_yaml(self) -> YamlErrorOr[str]:
        raise NotImplementedError

    # already read length
    @abc.abstractmethod
    def read_len(self) -> int:
        raise NotImplementedError

    # append read length
    @abc.abstractmethod
    def append_read_len(self, n: int) -> None:
        raise NotImplementedError

    # clean read length
    @abc.abstractmethod
    def clear_len(self) -> None:
        raise NotImplementedError


# MapKeyNode type for map key node
class MapKeyYamlNode(YamlNode, Abstract):
    @abc.abstractmethod
    def is_merge_key(self) -> bool:
        raise NotImplementedError

    # String node to text without comment
    @abc.abstractmethod
    def string_without_comment(self) -> str:
        raise NotImplementedError


# ScalarNode type for scalar node
class ScalarYamlNode(MapKeyYamlNode, Abstract):
    @abc.abstractmethod
    def get_value(self) -> ta.Any:
        raise NotImplementedError


##


@dc.dataclass()
class BaseYamlNode(YamlNode, Abstract):
    path: str = ''
    comment: ta.Optional['CommentGroupYamlNode'] = None
    cur_read: int = 0

    def read_len(self) -> int:
        return self.cur_read

    def clear_len(self) -> None:
        self.cur_read = 0

    def append_read_len(self, l: int) -> None:
        self.cur_read += l

    # get_path returns YAMLPath for the current node.
    @ta.final
    def get_path(self: ta.Optional['BaseYamlNode']) -> str:
        if self is None:
            return ''
        return self.path

    # set_path set YAMLPath for the current node.
    @ta.final
    def set_path(self: ta.Optional['BaseYamlNode'], path: str) -> None:
        if self is None:
            return
        self.path = path

    # get_comment returns comment token instance
    def get_comment(self) -> ta.Optional['CommentGroupYamlNode']:
        return self.comment

    # set_comment set comment token
    def set_comment(self, node: ta.Optional['CommentGroupYamlNode']) -> ta.Optional[YamlError]:
        self.comment = node
        return None


def add_comment_string(base: str, node: 'CommentGroupYamlNode') -> str:
    return f'{base} {node.string()}'


##


def read_node(p: str, node: YamlNode) -> YamlErrorOr[int]:
    s = node.string()
    read_len = node.read_len()
    remain = len(s) - read_len
    if remain == 0:
        node.clear_len()
        return EofYamlError()

    size = min(remain, len(p))
    for idx, b in enumerate(s[read_len:read_len + size]):
        p[idx] = b  # type: ignore[index]  # FIXME: lol

    node.append_read_len(size)
    return size


def check_line_break(t: YamlToken) -> bool:
    if t.prev is not None:
        lbc = '\n'
        prev = t.prev
        adjustment = 0
        # if the previous type is sequence entry use the previous type for that
        if prev.type == YamlTokenType.SEQUENCE_ENTRY:
            # as well as switching to previous type count any new lines in origin to account for:
            # -
            #   b: c
            adjustment = t.origin.rstrip(lbc).count(lbc)
            if prev.prev is not None:
                prev = prev.prev

        line_diff = t.position.line - prev.position.line - 1
        if line_diff > 0:
            if prev.type == YamlTokenType.STRING:
                # Remove any line breaks included in multiline string
                adjustment += prev.origin.strip().rstrip(lbc).count(lbc)

            # Due to the way that comment parsing works its assumed that when a null value does not have new line in
            # origin it was squashed therefore difference is ignored.
            # foo:
            #  bar:
            #  # comment
            #  baz: 1
            # becomes
            # foo:
            #  bar: null # comment
            #
            #  baz: 1
            if prev.type in (YamlTokenType.NULL, YamlTokenType.IMPLICIT_NULL):
                return prev.origin.count(lbc) > 0

            if line_diff - adjustment > 0:
                return True

    return False


##


# Null create node for null value
def null(tk: YamlToken) -> 'NullYamlNode':
    return NullYamlNode(
        token=tk,
    )


_BOOL_TRUE_STRS = {'1', 't', 'T', 'true', 'TRUE', 'True'}
_BOOL_FALSE_STRS = {'0', 'f', 'F', 'false', 'FALSE', 'False'}


def _parse_bool(s: str) -> bool:
    if s in _BOOL_TRUE_STRS:
        return True
    if s in _BOOL_FALSE_STRS:
        return False
    raise ValueError(f'"{s}" is not a valid boolean string')


# bool_ create node for boolean value
def bool_(tk: YamlToken) -> 'BoolYamlNode':
    b = _parse_bool(tk.value)
    return BoolYamlNode(
        token=tk,
        value=b,
    )


# integer create node for integer value
def integer(tk: YamlToken) -> 'IntegerYamlNode':
    v: ta.Any = None
    if (num := tokens.to_number(tk.value)) is not None:
        v = num.value

    return IntegerYamlNode(
        token=tk,
        value=v,
    )


# float_ create node for float value
def float_(tk: YamlToken) -> 'FloatYamlNode':
    v: float = 0.
    if (num := tokens.to_number(tk.value)) is not None and num.type == YamlNumberType.FLOAT:
        if isinstance(num.value, float):
            v = num.value

    return FloatYamlNode(
        token=tk,
        value=v,
    )


# infinity create node for .inf or -.inf value
def infinity(tk: YamlToken) -> 'InfinityYamlNode':
    if tk.value in ('.inf', '.Inf', '.INF'):
        value = float('inf')
    elif tk.value in ('-.inf', '-.Inf', '-.INF'):
        value = float('-inf')
    node = InfinityYamlNode(
        token=tk,
        value=value,
    )
    return node


# nan create node for .nan value
def nan(tk: YamlToken) -> 'NanYamlNode':
    return NanYamlNode(
        token=tk,
    )


# string create node for string value
def string(tk: YamlToken) -> 'StringYamlNode':
    return StringYamlNode(
        token=tk,
        value=tk.value,
    )


# comment create node for comment
def comment(tk: ta.Optional[YamlToken]) -> 'CommentYamlNode':
    return CommentYamlNode(
        token=tk,
    )


def comment_group(comments: ta.Iterable[ta.Optional[YamlToken]]) -> 'CommentGroupYamlNode':
    nodes: ta.List[CommentYamlNode] = []
    for c in comments:
        nodes.append(comment(c))

    return CommentGroupYamlNode(
        comments=nodes,
    )


# merge_key create node for merge key ( << )
def merge_key(tk: YamlToken) -> 'MergeKeyYamlNode':
    return MergeKeyYamlNode(
        token=tk,
    )


# mapping create node for map
def mapping(tk: YamlToken, is_flow_style: bool, *values: 'MappingValueYamlNode') -> 'MappingYamlNode':
    node = MappingYamlNode(
        start=tk,
        is_flow_style=is_flow_style,
        values=[],
    )
    node.values.extend(values)
    return node


# mapping_value create node for mapping value
def mapping_value(tk: YamlToken, key: 'MapKeyYamlNode', value: YamlNode) -> 'MappingValueYamlNode':
    return MappingValueYamlNode(
        start=tk,
        key=key,
        value=value,
    )


# mapping_key create node for map key ( '?' ).
def mapping_key(tk: YamlToken) -> 'MappingKeyYamlNode':
    return MappingKeyYamlNode(
        start=tk,
    )


# sequence create node for sequence
def sequence(tk: YamlToken, is_flow_style: bool) -> 'SequenceYamlNode':
    return SequenceYamlNode(
        start=tk,
        is_flow_style=is_flow_style,
        values=[],
    )


def anchor(tk: YamlToken) -> 'AnchorYamlNode':
    return AnchorYamlNode(
        start=tk,
    )


def alias(tk: YamlToken) -> 'AliasYamlNode':
    return AliasYamlNode(
        start=tk,
    )


def document(tk: ta.Optional[YamlToken], body: ta.Optional[YamlNode]) -> 'DocumentYamlNode':
    return DocumentYamlNode(
        start=tk,
        body=body,
    )


def directive(tk: YamlToken) -> 'DirectiveYamlNode':
    return DirectiveYamlNode(
        start=tk,
    )


def literal(tk: YamlToken) -> 'LiteralYamlNode':
    return LiteralYamlNode(
        start=tk,
    )


def tag(tk: YamlToken) -> 'TagYamlNode':
    return TagYamlNode(
        start=tk,
    )


##


# File contains all documents in YAML file
@dc.dataclass()
class YamlFile:
    name: str = ''
    docs: ta.List['DocumentYamlNode'] = dc.field(default_factory=dataclass_field_required('docs'))

    # read implements (io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        for doc in self.docs:
            n = doc.read(p)
            if isinstance(n, EofYamlError):
                continue
            return n
        return EofYamlError()

    # string all documents to text
    def string(self) -> str:
        docs: ta.List[str] = []
        for doc in self.docs:
            docs.append(doc.string())
        if len(docs) > 0:
            return '\n'.join(docs) + '\n'
        else:
            return ''


##


# DocumentNode type of Document
@dc.dataclass()
class DocumentYamlNode(BaseYamlNode):
    start: ta.Optional[YamlToken] = dc.field(default_factory=dataclass_field_required('start'))  # position of DocumentHeader ( `---` )  # noqa
    end: ta.Optional[YamlToken] = None  # position of DocumentEnd ( `...` )
    body: ta.Optional[YamlNode] = dc.field(default_factory=dataclass_field_required('body'))

    # read implements (io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns DocumentNodeType
    def type(self) -> YamlNodeType:
        return YamlNodeType.DOCUMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        return check.not_none(self.body).get_token()

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        if self.body is not None:
            self.body.add_column(col)

    # string document to text
    def string(self) -> str:
        doc: ta.List[str] = []
        if self.start is not None:
            doc.append(self.start.value)
        if self.body is not None:
            doc.append(self.body.string())
        if self.end is not None:
            doc.append(self.end.value)
        return '\n'.join(doc)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# NullNode type of null node
@dc.dataclass()
class NullYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns NullType
    def type(self) -> YamlNodeType:
        return YamlNodeType.NULL

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns nil value
    def get_value(self) -> ta.Any:
        return None

    # String returns `null` text
    def string(self) -> str:
        if self.token.type == YamlTokenType.IMPLICIT_NULL:
            if self.comment is not None:
                return self.comment.string()
            return ''
        if self.comment is not None:
            return add_comment_string('null', self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return 'null'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# IntegerNode type of integer node
@dc.dataclass()
class IntegerYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: ta.Any = dc.field(default_factory=dataclass_field_required('value'))  # int64 or uint64 value

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns IntegerType
    def type(self) -> YamlNodeType:
        return YamlNodeType.INTEGER

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns int64 value
    def get_value(self) -> ta.Any:
        return self.value

    # String int64 to text
    def string(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# FloatNode type of float node
@dc.dataclass()
class FloatYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    precision: int = 0
    value: float = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns FloatType
    def type(self) -> YamlNodeType:
        return YamlNodeType.FLOAT

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns float64 value
    def get_value(self) -> ta.Any:
        return self.value

    # String float64 to text
    def string(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


def _go_is_print(char_ord):
    """
    Approximates Go's unicode.IsPrint logic. A rune is printable if it is a letter, mark, number, punctuation, symbol,
    or ASCII space. (Corresponds to Unicode categories L, M, N, P, S, plus U+0020 SPACE).
    """

    if char_ord == 0x20:  # ASCII space
        return True
    # Check if the character is in categories L, M, N, P, S (Graphic characters)
    category = unicodedata.category(chr(char_ord))
    if category.startswith(('L', 'M', 'N', 'P', 'S')):
        return True
    return False


def strconv_quote(s: str) -> str:
    """
    Produces a double-quoted string literal with Go-style escapes, similar to Go's strconv.Quote.
    """

    res = ['"']
    for char_val in s:
        char_ord = ord(char_val)

        if char_val == '"':
            res.append('\\"')
        elif char_val == '\\':
            res.append('\\\\')
        elif char_val == '\a':
            res.append('\\a')
        elif char_val == '\b':
            res.append('\\b')
        elif char_val == '\f':
            res.append('\\f')
        elif char_val == '\n':
            res.append('\\n')
        elif char_val == '\r':
            res.append('\\r')
        elif char_val == '\t':
            res.append('\\t')
        elif char_val == '\v':
            res.append('\\v')
        elif char_ord < 0x20 or char_ord == 0x7F:  # C0 controls and DEL
            res.append(f'\\x{char_ord:02x}')
        elif 0x20 <= char_ord < 0x7F:  # Printable ASCII (already handled \, ")
            res.append(char_val)
        # Unicode characters (char_ord >= 0x80) and C1 controls (0x80-0x9F)
        elif _go_is_print(char_ord):
            res.append(char_val)
        elif char_ord <= 0xFFFF:
            res.append(f'\\u{char_ord:04x}')
        else:
            res.append(f'\\U{char_ord:08x}')

    res.append('"')
    return ''.join(res)


##


# StringNode type of string node
@dc.dataclass()
class StringYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: str = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns StringType
    def type(self) -> YamlNodeType:
        return YamlNodeType.STRING

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns string value
    def get_value(self) -> ta.Any:
        return self.value

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False

    # string string value to text with quote or literal header if required
    def string(self) -> str:
        if self.token.type == YamlTokenType.SINGLE_QUOTE:
            quoted = escape_single_quote(self.value)
            if self.comment is not None:
                return add_comment_string(quoted, self.comment)
            return quoted
        elif self.token.type == YamlTokenType.DOUBLE_QUOTE:
            quoted = strconv_quote(self.value)
            if self.comment is not None:
                return add_comment_string(quoted, self.comment)
            return quoted

        lbc = tokens.detect_line_break_char(self.value)
        if lbc in self.value:
            # This block assumes that the line breaks in this inside scalar content and the Outside scalar content are
            # the same. It works mostly, but inconsistencies occur if line break characters are mixed.
            header = tokens.literal_block_header(self.value)
            space = ' ' * (self.token.position.column - 1)
            indent = ' ' * self.token.position.indent_num
            values: ta.List[str] = []
            for v in self.value.split(lbc):
                values.append(f'{space}{indent}{v}')
            block = lbc.join(values).rstrip(f'{lbc}{indent}{space}').rstrip(f'{indent}{space}')
            return f'{header}{lbc}{block}'
        elif len(self.value) > 0 and (self.value[0] == '{' or self.value[0] == '['):
            return f"'{self.value}'"
        if self.comment is not None:
            return add_comment_string(self.value, self.comment)
        return self.value

    def string_without_comment(self) -> str:
        if self.token.type == YamlTokenType.SINGLE_QUOTE:
            quoted = f"'{self.value}'"
            return quoted
        elif self.token.type == YamlTokenType.DOUBLE_QUOTE:
            quoted = strconv_quote(self.value)
            return quoted

        lbc = tokens.detect_line_break_char(self.value)
        if lbc in self.value:
            # This block assumes that the line breaks in this inside scalar content and the Outside scalar content are
            # the same. It works mostly, but inconsistencies occur if line break characters are mixed.
            header = tokens.literal_block_header(self.value)
            space = ' ' * (self.token.position.column - 1)
            indent = ' ' * self.token.position.indent_num
            values: ta.List[str] = []
            for v in self.value.split(lbc):
                values.append(f'{space}{indent}{v}')
            block = lbc.join(values).rstrip(f'{lbc}{indent}{space}').rstrip(f'  {space}')
            return f'{header}{lbc}{block}'
        elif len(self.value) > 0 and (self.value[0] == '{' or self.value[0] == '['):
            return f"'{self.value}'"
        return self.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


# escape_single_quote escapes s to a single quoted scalar.
# https://yaml.org/spec/1.2.2/#732-single-quoted-style
def escape_single_quote(s: str) -> str:
    sb = io.StringIO()
    # growLen = len(s) + # s includes also one ' from the doubled pair
    #     2 + # opening and closing '
    #     strings.Count(s, "'") # ' added by ReplaceAll
    # sb.Grow(growLen)
    sb.write("'")
    sb.write(s.replace("'", "''"))
    sb.write("'")
    return sb.getvalue()


##


# LiteralNode type of literal node
@dc.dataclass()
class LiteralYamlNode(ScalarYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional['StringYamlNode'] = None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns LiteralType
    def type(self) -> YamlNodeType:
        return YamlNodeType.LITERAL

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # get_value returns string value
    def get_value(self) -> ta.Any:
        return self.string()

    # String literal to text
    def string(self) -> str:
        origin = check.not_none(check.not_none(self.value).get_token()).origin
        lit = origin.rstrip(' ').rstrip('\n')
        if self.comment is not None:
            return f'{self.start.value} {self.comment.string()}\n{lit}'
        return f'{self.start.value}\n{lit}'

    def string_without_comment(self) -> str:
        return self.string()

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# MergeKeyNode type of merge key node
@dc.dataclass()
class MergeKeyYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns MergeKeyType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MERGE_KEY

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # get_value returns '<<' value
    def get_value(self) -> ta.Any:
        return self.token.value

    # String returns '<<' value
    def string(self) -> str:
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return str(self)

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return True


##


# BoolNode type of boolean node
@dc.dataclass()
class BoolYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: bool = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns BoolType
    def type(self) -> YamlNodeType:
        return YamlNodeType.BOOL

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns boolean value
    def get_value(self) -> ta.Any:
        return self.value

    # String boolean to text
    def string(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# InfinityNode type of infinity node
@dc.dataclass()
class InfinityYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))
    value: float = dc.field(default_factory=dataclass_field_required('value'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns InfinityType
    def type(self) -> YamlNodeType:
        return YamlNodeType.INFINITY

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns math.Inf(0) or math.Inf(-1)
    def get_value(self) -> ta.Any:
        return self.value

    # String infinity to text
    def string(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# NanNode type of nan node
@dc.dataclass()
class NanYamlNode(ScalarYamlNode, BaseYamlNode):
    token: YamlToken = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns NanType
    def type(self) -> YamlNodeType:
        return YamlNodeType.NAN

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # get_value returns math.NaN()
    def get_value(self) -> ta.Any:
        return float('nan')

    # String returns .nan
    def string(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# MapNode interface of MappingValueNode / MappingNode
class MapYamlNode(Abstract):
    @abc.abstractmethod
    def map_range(self) -> 'MapYamlNodeIter':
        raise NotImplementedError


START_RANGE_INDEX = -1


# MapNodeIter is an iterator for ranging over a MapNode
@dc.dataclass()
class MapYamlNodeIter:
    values: ta.List['MappingValueYamlNode']
    idx: int

    # next advances the map iterator and reports whether there is another entry.
    # It returns false when the iterator is exhausted.
    def next(self) -> bool:
        self.idx += 1
        nxt = self.idx < len(self.values)
        return nxt

    # key returns the key of the iterator's current map node entry.
    def key(self) -> MapKeyYamlNode:
        return self.values[self.idx].key

    # value returns the value of the iterator's current map node entry.
    def value(self) -> YamlNode:
        return self.values[self.idx].value

    # key_value returns the MappingValueNode of the iterator's current map node entry.
    def key_value(self) -> 'MappingValueYamlNode':
        return self.values[self.idx]


#


# MappingNode type of mapping node
@dc.dataclass()
class MappingYamlNode(BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    end: ta.Optional[YamlToken] = None
    is_flow_style: bool = dc.field(default_factory=dataclass_field_required('is_flow_style'))
    values: ta.List['MappingValueYamlNode'] = dc.field(default_factory=dataclass_field_required('values'))
    foot_comment: ta.Optional['CommentGroupYamlNode'] = None

    def start_pos(self) -> YamlPosition:
        if len(self.values) == 0:
            return self.start.position
        return check.not_none(self.values[0].key.get_token()).position

    # merge merge key/value of map.
    def merge(self, target: 'MappingYamlNode') -> None:
        key_to_map_value_map: ta.Dict[str, MappingValueYamlNode] = {}
        for value in self.values:
            key = value.key.string()
            key_to_map_value_map[key] = value
        column = self.start_pos().column - target.start_pos().column
        target.add_column(column)
        for value in target.values:
            map_value = key_to_map_value_map.get(value.key.string())
            if map_value is not None:
                map_value.value = value.value
            else:
                self.values.append(value)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        for value in self.values:
            value.set_is_flow_style(is_flow)

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns MappingType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MAPPING

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        YamlToken.add_column(self.end, col)
        for value in self.values:
            value.add_column(col)

    def flow_style_string(self, comment_mode: bool) -> str:
        values: ta.List[str] = []
        for value in self.values:
            values.append(value.string().lstrip(' '))
        map_text = f'{{{", ".join(values)}}}'
        if comment_mode and self.comment is not None:
            return add_comment_string(map_text, self.comment)
        return map_text

    def block_style_string(self, comment_mode: bool) -> str:
        values: ta.List[str] = []
        for value0 in self.values:
            values.append(value0.string())
        map_text = '\n'.join(values)
        if comment_mode and self.comment is not None:
            value1 = values[0]
            space_num = 0
            for i in range(len(value1)):
                if value1[i] != ' ':
                    break
                space_num += 1
            comment = self.comment.string_with_space(space_num)
            return f'{comment}\n{map_text}'
        return map_text

    # String mapping values to text
    def string(self) -> str:
        if len(self.values) == 0:
            if self.comment is not None:
                return add_comment_string('{}', self.comment)
            return '{}'

        comment_mode = True
        if self.is_flow_style or len(self.values) == 0:
            return self.flow_style_string(comment_mode)

        return self.block_style_string(comment_mode)

    # map_range implements MapNode protocol
    def map_range(self) -> MapYamlNodeIter:
        return MapYamlNodeIter(
            idx=START_RANGE_INDEX,
            values=self.values,
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# MappingKeyNode type of tag node
@dc.dataclass()
class MappingKeyYamlNode(MapKeyYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional[YamlNode] = None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns MappingKeyType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MAPPING_KEY

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # String tag to text
    def string(self) -> str:
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return f'{self.start.value} {check.not_none(self.value).string()}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyYamlNode):
            return False
        return key.is_merge_key()


##


# MappingValueNode type of mapping value
@dc.dataclass()
class MappingValueYamlNode(BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))  # delimiter token ':'.
    collect_entry: ta.Optional[YamlToken] = None  # collect entry token ','.
    key: MapKeyYamlNode = dc.field(default_factory=dataclass_field_required('key'))
    value: YamlNode = dc.field(default_factory=dataclass_field_required('value'))
    foot_comment: ta.Optional['CommentGroupYamlNode'] = None
    is_flow_style: bool = False

    # Replace replace value node.
    def replace(self, value: YamlNode) -> ta.Optional[YamlError]:
        column = check.not_none(self.value.get_token()).position.column - check.not_none(value.get_token()).position.column  # noqa
        value.add_column(column)
        self.value = value
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns MappingValueType
    def type(self) -> YamlNodeType:
        return YamlNodeType.MAPPING_VALUE

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.key is not None:
            self.key.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        if isinstance(self.value, MappingYamlNode):
            self.value.set_is_flow_style(is_flow)
        elif isinstance(self.value, MappingValueYamlNode):
            self.value.set_is_flow_style(is_flow)
        elif isinstance(self.value, SequenceYamlNode):
            self.value.set_is_flow_style(is_flow)

    # String mapping value to text
    def string(self) -> str:
        text: str
        if self.comment is not None:
            text = f'{self.comment.string_with_space(check.not_none(self.key.get_token()).position.column - 1)}\n{self.to_string()}'  # noqa
        else:
            text = self.to_string()

        if self.foot_comment is not None:
            text += f'\n{self.foot_comment.string_with_space(check.not_none(self.key.get_token()).position.column - 1)}'

        return text

    def to_string(self) -> str:
        space = ' ' * (check.not_none(self.key.get_token()).position.column - 1)
        if check_line_break(check.not_none(self.key.get_token())):
            space = f'\n{space}'

        key_indent_level = check.not_none(self.key.get_token()).position.indent_level
        value_indent_level = check.not_none(self.value.get_token()).position.indent_level
        key_comment = self.key.get_comment()

        if isinstance(self.value, ScalarYamlNode):
            value = self.value.string()
            if value == '':
                # implicit null value.
                return f'{space}{self.key.string()}:'
            return f'{space}{self.key.string()}: {value}'

        elif key_indent_level < value_indent_level and not self.is_flow_style:
            if key_comment is not None:
                return f'{space}{self.key.string_without_comment()}: {key_comment.string()}\n{self.value.string()}'

            return f'{space}{self.key.string()}:\n{self.value.string()}'

        elif isinstance(self.value, MappingYamlNode) and (self.value.is_flow_style or len(self.value.values) == 0):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, SequenceYamlNode) and (self.value.is_flow_style or len(self.value.values) == 0):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, AnchorYamlNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, AliasYamlNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, TagYamlNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        if key_comment is not None:
            return f'{space}{self.key.string_without_comment()}: {key_comment.string()}\n{self.value.string()}'

        if isinstance(self.value, MappingYamlNode) and self.value.comment is not None:
            return f'{space}{self.key.string()}: {self.value.string().lstrip(" ")}'

        return f'{space}{self.key.string()}:\n{self.value.string()}'

    # map_range implements MapNode protocol
    def map_range(self) -> MapYamlNodeIter:
        return MapYamlNodeIter(
            idx=START_RANGE_INDEX,
            values=[self],
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# ArrayNode interface of SequenceNode
class ArrayYamlNode(YamlNode, Abstract):
    @abc.abstractmethod
    def array_range(self) -> ta.Optional['ArrayYamlNodeIter']:
        raise NotImplementedError


# ArrayNodeIter is an iterator for ranging over a ArrayNode
@dc.dataclass()
class ArrayYamlNodeIter:
    values: ta.List[YamlNode]
    idx: int

    # next advances the array iterator and reports whether there is another entry.
    # It returns false when the iterator is exhausted.
    def next(self) -> bool:
        self.idx += 1
        nxt = self.idx < len(self.values)
        return nxt

    # Value returns the value of the iterator's current array entry.
    def value(self) -> YamlNode:
        return self.values[self.idx]

    # len returns length of array
    def len(self) -> int:
        return len(self.values)


##


# SequenceNode type of sequence node
@dc.dataclass()
class SequenceYamlNode(BaseYamlNode, ArrayYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    end: ta.Optional[YamlToken] = None
    is_flow_style: bool = dc.field(default_factory=dataclass_field_required('is_flow_style'))
    values: ta.List[ta.Optional[YamlNode]] = dc.field(default_factory=dataclass_field_required('values'))
    value_head_comments: ta.List[ta.Optional['CommentGroupYamlNode']] = dc.field(default_factory=list)
    entries: ta.List['SequenceEntryYamlNode'] = dc.field(default_factory=list)
    foot_comment: ta.Optional['CommentGroupYamlNode'] = None

    # replace replace value node.
    def replace(self, idx: int, value: YamlNode) -> ta.Optional[YamlError]:
        if len(self.values) <= idx:
            return yaml_error(f'invalid index for sequence: sequence length is {len(self.values):d}, but specified {idx:d} index')  # noqa

        column = check.not_none(check.not_none(self.values[idx]).get_token()).position.column - check.not_none(value.get_token()).position.column  # noqa
        value.add_column(column)
        self.values[idx] = value
        return None

    # merge merge sequence value.
    def merge(self, target: 'SequenceYamlNode') -> None:
        column = self.start.position.column - target.start.position.column
        target.add_column(column)
        self.values.extend(target.values)
        if len(target.value_head_comments) == 0:
            self.value_head_comments.extend([None] * len(target.values))
            return

        self.value_head_comments.extend(target.value_head_comments)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        for value in self.values:
            if isinstance(value, MappingYamlNode):
                value.set_is_flow_style(is_flow)
            elif isinstance(value, MappingValueYamlNode):
                value.set_is_flow_style(is_flow)
            elif isinstance(value, SequenceYamlNode):
                value.set_is_flow_style(is_flow)

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns SequenceType
    def type(self) -> YamlNodeType:
        return YamlNodeType.SEQUENCE

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        YamlToken.add_column(self.end, col)
        for value in self.values:
            check.not_none(value).add_column(col)

    def flow_style_string(self) -> str:
        values: ta.List[str] = []
        for value in self.values:
            values.append(check.not_none(value).string())

        return f'[{", ".join(values)}]'

    def block_style_string(self) -> str:
        space = ' ' * (self.start.position.column - 1)
        values: ta.List[str] = []
        if self.comment is not None:
            values.append(self.comment.string_with_space(self.start.position.column - 1))

        for idx, value in enumerate(self.values):
            if value is None:
                continue

            value_str = value.string()
            new_line_prefix = ''
            if value_str.startswith('\n'):
                value_str = value_str[1:]
                new_line_prefix = '\n'

            splitted_values = value_str.split('\n')
            trimmed_first_value = splitted_values[0].lstrip(' ')
            diff_length = len(splitted_values[0]) - len(trimmed_first_value)
            if (
                    (len(splitted_values) > 1 and value.type() == YamlNodeType.STRING) or
                    value.type() == YamlNodeType.LITERAL
            ):
                # If multi-line string, the space characters for indent have already been added, so delete them.
                prefix = space + '  '
                for i in range(1, len(splitted_values)):
                    splitted_values[i] = splitted_values[i].lstrip(prefix)

            new_values: ta.List[str] = [trimmed_first_value]
            for i in range(1, len(splitted_values)):
                if len(splitted_values[i]) <= diff_length:
                    # this line is \n or white space only
                    new_values.append('')
                    continue

                trimmed = splitted_values[i][diff_length:]
                new_values.append(f'{space}  {trimmed}')

            new_value = '\n'.join(new_values)
            if len(self.value_head_comments) == len(self.values) and self.value_head_comments[idx] is not None:
                values.append(
                    f'{new_line_prefix}'
                    f'{check.not_none(self.value_head_comments[idx]).string_with_space(self.start.position.column - 1)}',  # noqa
                )
                new_line_prefix = ''

            values.append(f'{new_line_prefix}{space}- {new_value}')

        if self.foot_comment is not None:
            values.append(self.foot_comment.string_with_space(self.start.position.column - 1))

        return '\n'.join(values)

    # String sequence to text
    def string(self) -> str:
        if self.is_flow_style or len(self.values) == 0:
            return self.flow_style_string()
        return self.block_style_string()

    # array_range implements ArrayNode protocol
    def array_range(self) -> ta.Optional[ArrayYamlNodeIter]:
        return ArrayYamlNodeIter(
            idx=START_RANGE_INDEX,
            values=ta.cast('ta.List[YamlNode]', self.values),
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# SequenceEntryNode is the sequence entry.
@dc.dataclass()
class SequenceEntryYamlNode(BaseYamlNode):
    head_comment: ta.Optional['CommentGroupYamlNode'] = dc.field(default_factory=dataclass_field_required('head_commend'))  # head comment.  # noqa
    line_comment: ta.Optional['CommentGroupYamlNode'] = None  # line comment e.g.) - # comment.
    start: ta.Optional[YamlToken] = dc.field(default_factory=dataclass_field_required('start'))  # entry token.
    value: YamlNode = dc.field(default_factory=dataclass_field_required('value'))  # value node.

    # String node to text
    def string(self) -> str:
        return ''  # TODO

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        return self.start

    # type returns type of node
    def type(self) -> YamlNodeType:
        return YamlNodeType.SEQUENCE_ENTRY

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)

    # set_comment set line comment.
    def set_comment(self, node: ta.Optional['CommentGroupYamlNode']) -> ta.Optional[YamlError]:
        self.line_comment = node
        return None

    # comment returns comment token instance
    def get_comment(self) -> ta.Optional['CommentGroupYamlNode']:
        return self.line_comment

    # marshal_yaml
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)


# sequence_entry creates SequenceEntryNode instance.
def sequence_entry(
        start: ta.Optional[YamlToken],
        value: YamlNode,
        head_comment: ta.Optional['CommentGroupYamlNode'],
) -> SequenceEntryYamlNode:
    return SequenceEntryYamlNode(
        head_comment=head_comment,
        start=start,
        value=value,
    )


# SequenceMergeValue creates SequenceMergeValueNode instance.
def sequence_merge_value(*values: MapYamlNode) -> 'SequenceMergeValueYamlNode':
    return SequenceMergeValueYamlNode(
        values=list(values),
    )


##


# SequenceMergeValueNode is used to convert the Sequence node specified for the merge key into a MapNode format.
@dc.dataclass()
class SequenceMergeValueYamlNode(MapYamlNode):
    values: ta.List[MapYamlNode] = dc.field(default_factory=dataclass_field_required('values'))

    # map_range returns MapNodeIter instance.
    def map_range(self) -> MapYamlNodeIter:
        ret = MapYamlNodeIter(values=[], idx=START_RANGE_INDEX)
        for value in self.values:
            it = value.map_range()
            ret.values.extend(it.values)
        return ret


##


# AnchorNode type of anchor node
@dc.dataclass()
class AnchorYamlNode(ScalarYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    name: ta.Optional[YamlNode] = None
    value: ta.Optional[YamlNode] = None

    def string_without_comment(self) -> str:
        return check.not_none(self.value).string()

    def set_name(self, name: str) -> ta.Optional[YamlError]:
        if self.name is None:
            return ERR_INVALID_ANCHOR_NAME
        s = self.name
        if not isinstance(s, StringYamlNode):
            return ERR_INVALID_ANCHOR_NAME
        s.value = name
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns AnchorType
    def type(self) -> YamlNodeType:
        return YamlNodeType.ANCHOR

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    def get_value(self) -> ta.Any:
        return check.not_none(check.not_none(self.value).get_token()).value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.name is not None:
            self.name.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # String anchor to text
    def string(self) -> str:
        anchor = '&' + check.not_none(self.name).string()
        value = check.not_none(self.value).string()
        if isinstance(self.value, SequenceYamlNode) and not self.value.is_flow_style:
            return f'{anchor}\n{value}'
        elif isinstance(self.value, MappingYamlNode) and not self.value.is_flow_style:
            return f'{anchor}\n{value}'
        if value == '':
            # implicit null value.
            return anchor
        return f'{anchor} {value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyYamlNode):
            return False
        return key.is_merge_key()


##


# AliasNode type of alias node
@dc.dataclass()
class AliasYamlNode(ScalarYamlNode, BaseYamlNode):
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional[YamlNode] = None

    def string_without_comment(self) -> str:
        return check.not_none(self.value).string()

    def set_name(self, name: str) -> ta.Optional[YamlError]:
        if self.value is None:
            return ERR_INVALID_ALIAS_NAME
        if not isinstance(self.value, StringYamlNode):
            return ERR_INVALID_ALIAS_NAME
        self.value.value = name
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns AliasType
    def type(self) -> YamlNodeType:
        return YamlNodeType.ALIAS

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    def get_value(self) -> ta.Any:
        return check.not_none(check.not_none(self.value).get_token()).value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # String alias to text
    def string(self) -> str:
        return f'*{check.not_none(self.value).string()}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# DirectiveNode type of directive node
@dc.dataclass()
class DirectiveYamlNode(BaseYamlNode):
    # Start is '%' token.
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    # Name is directive name e.g.) "YAML" or "TAG".
    name: ta.Optional[YamlNode] = None
    # Values is directive values e.g.) "1.2" or "!!" and "tag:clarkevans.com,2002:app/".
    values: ta.List[YamlNode] = dc.field(default_factory=list)

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns DirectiveType
    def type(self) -> YamlNodeType:
        return YamlNodeType.DIRECTIVE

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        if self.name is not None:
            self.name.add_column(col)
        for value in self.values:
            value.add_column(col)

    # String directive to text
    def string(self) -> str:
        values: ta.List[str] = []
        for val in self.values:
            values.append(val.string())
        return ' '.join(['%' + check.not_none(self.name).string(), *values])

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# TagNode type of tag node
@dc.dataclass()
class TagYamlNode(ScalarYamlNode, BaseYamlNode, ArrayYamlNode):
    directive: ta.Optional[DirectiveYamlNode] = None
    start: YamlToken = dc.field(default_factory=dataclass_field_required('start'))
    value: ta.Optional[YamlNode] = None

    def get_value(self) -> ta.Any:
        if not isinstance(self.value, ScalarYamlNode):
            return None
        return self.value.get_value()

    def string_without_comment(self) -> str:
        return check.not_none(self.value).string()

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns TagType
    def type(self) -> YamlNodeType:
        return YamlNodeType.TAG

    # get_token returns token instance
    def get_token(self) -> YamlToken:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.start, col)
        if self.value is not None:
            self.value.add_column(col)

    # String tag to text
    def string(self) -> str:
        value = check.not_none(self.value).string()
        if isinstance(self.value, SequenceYamlNode) and not self.value.is_flow_style:
            return f'{self.start.value}\n{value}'
        elif isinstance(self.value, MappingYamlNode) and not self.value.is_flow_style:
            return f'{self.start.value}\n{value}'

        return f'{self.start.value} {value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyYamlNode):
            return False
        return key.is_merge_key()

    def array_range(self) -> ta.Optional[ArrayYamlNodeIter]:
        arr = self.value
        if not isinstance(arr, ArrayYamlNode):
            return None
        return arr.array_range()


##


# CommentNode type of comment node
@dc.dataclass()
class CommentYamlNode(BaseYamlNode):
    token: ta.Optional[YamlToken] = dc.field(default_factory=dataclass_field_required('token'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns CommentType
    def type(self) -> YamlNodeType:
        return YamlNodeType.COMMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        YamlToken.add_column(self.token, col)

    # String comment to text
    def string(self) -> str:
        return f'#{check.not_none(self.token).value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# CommentGroupNode type of comment node
@dc.dataclass()
class CommentGroupYamlNode(BaseYamlNode):
    comments: ta.List[CommentYamlNode] = dc.field(default_factory=dataclass_field_required('comments'))

    # read implements(io.Reader).Read
    def read(self, p: str) -> YamlErrorOr[int]:
        return read_node(p, self)

    # type returns CommentType
    def type(self) -> YamlNodeType:
        return YamlNodeType.COMMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[YamlToken]:
        if len(self.comments) > 0:
            return self.comments[0].token
        return None

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        for comment in self.comments:
            comment.add_column(col)

    # String comment to text
    def string(self) -> str:
        values: ta.List[str] = []
        for comment in self.comments:
            values.append(comment.string())
        return '\n'.join(values)

    def string_with_space(self, col: int) -> str:
        values: ta.List[str] = []
        space = ' ' * col
        for comment in self.comments:
            spc = space
            if check_line_break(check.not_none(comment.token)):
                spc = f'\n{spc}'
            values.append(spc + comment.string())
        return '\n'.join(values)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> YamlErrorOr[str]:
        return self.string()


##


# Visitor has Visit method that is invokded for each node encountered by walk.
# If the result visitor w is not nil, walk visits each of the children of node with the visitor w,
# followed by a call of w.visit(nil).
class Visitor(Abstract):
    @abc.abstractmethod
    def visit(self, node: YamlNode) -> ta.Optional['Visitor']:
        raise NotImplementedError


# walk traverses an AST in depth-first order: It starts by calling v.visit(node); node must not be nil.
# If the visitor w returned by v.visit(node) is not nil,
# walk is invoked recursively with visitor w for each of the non-nil children of node,
# followed by a call of w.visit(nil).
def walk(v: Visitor, node: YamlNode) -> None:
    if (v_ := v.visit(node)) is None:
        return
    v = v_

    n = node
    if isinstance(n, (CommentYamlNode, NullYamlNode)):
        walk_comment(v, n)
    if isinstance(n, IntegerYamlNode):
        walk_comment(v, n)
    if isinstance(n, FloatYamlNode):
        walk_comment(v, n)
    if isinstance(n, StringYamlNode):
        walk_comment(v, n)
    if isinstance(n, MergeKeyYamlNode):
        walk_comment(v, n)
    if isinstance(n, BoolYamlNode):
        walk_comment(v, n)
    if isinstance(n, InfinityYamlNode):
        walk_comment(v, n)
    if isinstance(n, NanYamlNode):
        walk_comment(v, n)
    if isinstance(n, LiteralYamlNode):
        walk_comment(v, n)
        walk(v, check.not_none(n.value))
    if isinstance(n, DirectiveYamlNode):
        walk_comment(v, n)
        walk(v, check.not_none(n.name))
        for value0 in n.values:
            walk(v, value0)
    if isinstance(n, TagYamlNode):
        walk_comment(v, n)
        walk(v, check.not_none(n.value))
    if isinstance(n, DocumentYamlNode):
        walk_comment(v, n)
        walk(v, check.not_none(n.body))
    if isinstance(n, MappingYamlNode):
        walk_comment(v, n)
        for value1 in n.values:
            walk(v, value1)
    if isinstance(n, MappingKeyYamlNode):
        walk_comment(v, n)
        walk(v, check.not_none(n.value))
    if isinstance(n, MappingValueYamlNode):
        walk_comment(v, n)
        walk(v, n.key)
        walk(v, n.value)
    if isinstance(n, SequenceYamlNode):
        walk_comment(v, n)
        for value2 in n.values:
            walk(v, check.not_none(value2))
    if isinstance(n, AnchorYamlNode):
        walk_comment(v, n)
        walk(v, check.not_none(n.name))
        walk(v, check.not_none(n.value))
    if isinstance(n, AliasYamlNode):
        walk_comment(v, n)
        walk(v, check.not_none(n.value))


def walk_comment(v: Visitor, base: ta.Optional[BaseYamlNode]) -> None:
    if base is None:
        return
    if base.comment is None:
        return
    walk(v, base.comment)


#


@dc.dataclass()
class FilterWalker(Visitor):
    typ: YamlNodeType = dc.field(default_factory=dataclass_field_required('typ'))
    results: ta.List[YamlNode] = dc.field(default_factory=list)

    def visit(self, n: YamlNode) -> Visitor:
        if self.typ == n.type():
            self.results.append(n)
        return self


#


@dc.dataclass()
class ParentFinder:
    target: YamlNode

    def walk(self, parent: YamlNode, node: ta.Optional[YamlNode]) -> ta.Optional[YamlNode]:
        if self.target == node:
            return parent

        n = node
        if isinstance(n, CommentYamlNode):
            return None
        if isinstance(n, NullYamlNode):
            return None
        if isinstance(n, IntegerYamlNode):
            return None
        if isinstance(n, FloatYamlNode):
            return None
        if isinstance(n, StringYamlNode):
            return None
        if isinstance(n, MergeKeyYamlNode):
            return None
        if isinstance(n, BoolYamlNode):
            return None
        if isinstance(n, InfinityYamlNode):
            return None
        if isinstance(n, NanYamlNode):
            return None
        if isinstance(n, LiteralYamlNode):
            return self.walk(n, n.value)
        if isinstance(n, DirectiveYamlNode):
            if (found := self.walk(n, n.name)) is not None:
                return found
            for value0 in n.values:
                if (found := self.walk(n, value0)) is not None:
                    return found
        if isinstance(n, TagYamlNode):
            return self.walk(n, n.value)
        if isinstance(n, DocumentYamlNode):
            return self.walk(n, n.body)
        if isinstance(n, MappingYamlNode):
            for value1 in n.values:
                if (found := self.walk(n, value1)) is not None:
                    return found
        if isinstance(n, MappingKeyYamlNode):
            return self.walk(n, n.value)
        if isinstance(n, MappingValueYamlNode):
            if (found := self.walk(n, n.key)) is not None:
                return found
            return self.walk(n, n.value)
        if isinstance(n, SequenceYamlNode):
            for value2 in n.values:
                if (found := self.walk(n, value2)) is not None:
                    return found
        if isinstance(n, AnchorYamlNode):
            if (found := self.walk(n, n.name)) is not None:
                return found
            return self.walk(n, n.value)
        if isinstance(n, AliasYamlNode):
            return self.walk(n, n.value)
        return None


# Parent get parent node from child node.
def parent(root: YamlNode, child: YamlNode) -> ta.Optional[YamlNode]:
    finder = ParentFinder(target=child)
    return finder.walk(root, root)


#


# Filter returns a list of nodes that match the given type.
def filter_(typ: YamlNodeType, node: YamlNode) -> ta.List[YamlNode]:
    walker = FilterWalker(typ=typ)
    walk(walker, node)
    return walker.results


# FilterFile returns a list of nodes that match the given type.
def filter_file(typ: YamlNodeType, file: YamlFile) -> ta.List[YamlNode]:
    results: ta.List[YamlNode] = []
    for doc in file.docs:
        walker = FilterWalker(typ=typ)
        walk(walker, doc)
        results.extend(walker.results)
    return results


#


@dc.dataclass()
class InvalidMergeTypeYamlError(YamlError):
    dst: YamlNode
    src: YamlNode

    @property
    def message(self) -> str:
        return f'cannot merge {self.src.type()} into {self.dst.type()}'


# Merge merge document, map, sequence node.
def merge(dst: YamlNode, src: YamlNode) -> ta.Optional[YamlError]:
    if isinstance(src, DocumentYamlNode):
        doc: DocumentYamlNode = src
        src = check.not_none(doc.body)

    err = InvalidMergeTypeYamlError(dst=dst, src=src)
    if dst.type() == YamlNodeType.DOCUMENT:
        node0: DocumentYamlNode = check.isinstance(dst, DocumentYamlNode)
        return merge(check.not_none(node0.body), src)
    if dst.type() == YamlNodeType.MAPPING:
        node1: MappingYamlNode = check.isinstance(dst, MappingYamlNode)
        if not isinstance(src, MappingYamlNode):
            return err
        target0: MappingYamlNode = src
        node1.merge(target0)
        return None
    if dst.type() == YamlNodeType.SEQUENCE:
        node2: SequenceYamlNode = check.isinstance(dst, SequenceYamlNode)
        if not isinstance(src, SequenceYamlNode):
            return err
        target1: SequenceYamlNode = src
        node2.merge(target1)
        return None
    return err
