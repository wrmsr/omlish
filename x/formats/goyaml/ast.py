# ruff: noqa: UP006 UP007 UP043 UP045
import abc
import dataclasses as dc
import enum
import io
import typing as ta
import unicodedata

from . import tokens


##


ERR_INVALID_TOKEN_TYPE  = 'invalid token type'  # noqa
ERR_INVALID_ANCHOR_NAME = 'invalid anchor name'
ERR_INVALID_ALIAS_NAME  = 'invalid alias name'


class NodeType(enum.Enum):
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
NODE_TYPE_YAML_NAMES: ta.Mapping[NodeType, str] = {
    NodeType.UNKNOWN: 'unknown',
    NodeType.DOCUMENT: 'document',
    NodeType.NULL: 'null',
    NodeType.BOOL: 'boolean',
    NodeType.INTEGER: 'int',
    NodeType.FLOAT: 'float',
    NodeType.INFINITY: 'inf',
    NodeType.NAN: 'nan',
    NodeType.STRING: 'string',
    NodeType.MERGE_KEY: 'merge key',
    NodeType.LITERAL: 'scalar',
    NodeType.MAPPING: 'mapping',
    NodeType.MAPPING_KEY: 'key',
    NodeType.MAPPING_VALUE: 'value',
    NodeType.SEQUENCE: 'sequence',
    NodeType.SEQUENCE_ENTRY: 'value',
    NodeType.ANCHOR: 'anchor',
    NodeType.ALIAS: 'alias',
    NodeType.DIRECTIVE: 'directive',
    NodeType.TAG: 'tag',
    NodeType.COMMENT: 'comment',
    NodeType.COMMENT_GROUP: 'comment',
}


##


# Node type of node
class Node(abc.ABC):
    # io.Reader

    # String node to text
    def __str__(self) -> str:
        raise TypeError

    def string(self) -> str:
        # FIXME: migrate off - ensure all sprintfy things explicitly call .string()
        return self.__str__()

    # get_token returns token instance
    @abc.abstractmethod
    def get_token(self) -> ta.Optional[tokens.Token]:
        raise NotImplementedError

    # type returns type of node
    @abc.abstractmethod
    def type(self) -> NodeType:
        raise NotImplementedError

    # add_column add column number to child nodes recursively
    @abc.abstractmethod
    def add_column(self, column: int) -> None:
        raise NotImplementedError

    # set_comment set comment token to node
    @abc.abstractmethod
    def set_comment(self, node: 'CommentGroupNode') -> ta.Optional[str]:
        raise NotImplementedError

    # comment returns comment token instance
    @abc.abstractmethod
    def get_comment(self) -> ta.Optional['CommentGroupNode']:
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
    def marshal_yaml(self) -> ta.Tuple[bytes, ta.Optional[str]]:
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
class MapKeyNode(Node, abc.ABC):
    @abc.abstractmethod
    def is_merge_key(self) -> bool:
        raise NotImplementedError

    # String node to text without comment
    @abc.abstractmethod
    def string_without_comment(self) -> str:
        raise NotImplementedError


# ScalarNode type for scalar node
class ScalarNode(MapKeyNode, abc.ABC):
    @abc.abstractmethod
    def get_value(self) -> ta.Any:
        raise NotImplementedError


##


@dc.dataclass(kw_only=True)
class BaseNode(Node, abc.ABC):
    path: str = ''
    comment: ta.Optional['CommentGroupNode'] = None
    read: int = 0

    def read_len(self) -> int:
        return self.read

    def clear_len(self) -> None:
        self.read = 0

    def append_read_len(self, l: int) -> None:
        self.read += l

    # get_path returns YAMLPath for the current node.
    def get_path(self) -> str:
        if self is None:
            return ''
        return self.path

    # set_path set YAMLPath for the current node.
    def set_path(self, path: str) -> None:
        if self is None:
            return
        self.path = path

    # get_comment returns comment token instance
    def get_comment(self) -> ta.Optional['CommentGroupNode']:
        return self.comment

    # set_comment set comment token
    def set_comment(self, node: ta.Optional['CommentGroupNode']) -> None:
        self.comment = node


def add_comment_string(base: str, node: 'CommentGroupNode') -> str:
    return f'{base} {node.string()}'


##


def read_node(p: str, node: Node) -> ta.Tuple[int, ta.Optional[str]]:
    s = node.string()
    read_len = node.read_len()
    remain = len(s) - read_len
    if remain == 0:
        node.clear_len()
        return 0, 'eof'

    size = min(remain, len(p))
    for idx, b in enumerate(s[read_len : read_len+size]):
        p[idx] = b  # FIXME: lol

    node.append_read_len(size)
    return size, None


def check_line_break(t: tokens.Token) -> bool:
    if t.prev is not None:
        lbc = '\n'
        prev = t.prev
        adjustment = 0
        # if the previous type is sequence entry use the previous type for that
        if prev.type == tokens.Type.SEQUENCE_ENTRY:
            # as well as switching to previous type count any new lines in origin to account for:
            # -
            #   b: c
            adjustment = t.origin.rstrip(lbc).count(lbc)
            if prev.prev is not None:
                prev = prev.prev

        line_diff = t.position.line - prev.position.line - 1
        if line_diff > 0:
            if prev.type == tokens.Type.STRING:
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
            if prev.type in (tokens.Type.NULL, tokens.Type.IMPLICIT_NULL):
                return prev.origin.count(lbc) > 0

            if line_diff-adjustment > 0:
                return True

    return False


##


# Null create node for null value
def null(tk: tokens.Token) -> 'NullNode':
    return NullNode(
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
def bool_(tk: tokens.Token) -> 'BoolNode':
    b = _parse_bool(tk.value)
    return BoolNode(
        token=tk,
        value=b,
    )


# integer create node for integer value
def integer(tk: tokens.Token) -> 'IntegerNode':
    v: ta.Any = None
    if (num := tokens.to_number(tk.value)) is not None:
        v = num.value

    return IntegerNode(
        token=tk,
        value=v,
    )


# float_ create node for float value
def float_(tk: tokens.Token) -> 'FloatNode':
    v: float = 0.
    if (num := tokens.to_number(tk.value)) is not None and num.type == tokens.NumberType.FLOAT:
        if isinstance(num.value, float):
            v = num.value

    return FloatNode(
        token=tk,
        value=v,
    )


# infinity create node for .inf or -.inf value
def infinity(tk: tokens.Token) -> 'InfinityNode':
    node = InfinityNode(
        token=tk,
    )
    if tk.value in ('.inf', '.Inf', '.INF'):
        node.value = float('inf')
    elif tk.value in ('-.inf', '-.Inf', '-.INF'):
        node.value = float('-inf')
    return node


# nan create node for .nan value
def nan(tk: tokens.Token) -> 'NanNode':
    return NanNode(
        token=tk,
    )


# string create node for string value
def string(tk: tokens.Token) -> 'StringNode':
    return StringNode(
        token=tk,
        value=tk.value,
    )


# comment create node for comment
def comment(tk: ta.Optional[tokens.Token]) -> 'CommentNode':
    return CommentNode(
        token=tk,
    )


def comment_group(comments: ta.Iterable[ta.Optional[tokens.Token]]) -> 'CommentGroupNode':
    nodes: ta.List[CommentNode] = []
    for c in comments:
        nodes.append(comment(c))

    return CommentGroupNode(
        comments=nodes,
    )


# merge_key create node for merge key ( << )
def merge_key(tk: tokens.Token) -> 'MergeKeyNode':
    return MergeKeyNode(
        token=tk,
    )


# mapping create node for map
def mapping(tk: tokens.Token, is_flow_style: bool, *values: 'MappingValueNode') -> 'MappingNode':
    node = MappingNode(
        start=tk,
        is_flow_style=is_flow_style,
        values=[],
    )
    node.values.extend(values)
    return node


# mapping_value create node for mapping value
def mapping_value(tk: tokens.Token, key: 'MapKeyNode', value: Node) -> 'MappingValueNode':
    return MappingValueNode(
        start=tk,
        key=key,
        value=value,
    )


# mapping_key create node for map key ( '?' ).
def mapping_key(tk: tokens.Token) -> 'MappingKeyNode':
    return MappingKeyNode(
        start=tk,
    )


# sequence create node for sequence
def sequence(tk: tokens.Token, is_flow_style: bool) -> 'SequenceNode':
    return SequenceNode(
        start=tk,
        is_flow_style=is_flow_style,
        values=[],
    )


def anchor(tk: tokens.Token) -> 'AnchorNode':
    return AnchorNode(
        start=tk,
    )


def alias(tk: tokens.Token) -> 'AliasNode':
    return AliasNode(
        start=tk,
    )


def document(tk: tokens.Token, body: ta.Optional[Node]) -> 'DocumentNode':
    return DocumentNode(
        start=tk,
        body=body,
    )


def directive(tk: tokens.Token) -> 'DirectiveNode':
    return DirectiveNode(
        start=tk,
    )


def literal(tk: tokens.Token) -> 'LiteralNode':
    return LiteralNode(
        start=tk,
    )


def tag(tk: tokens.Token) -> 'TagNode':
    return TagNode(
        start=tk,
    )


##


# File contains all documents in YAML file
@dc.dataclass(kw_only=True)
class File:
    name: str = ''
    docs: ta.List['DocumentNode']

    # read implements (io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        for doc in self.docs:
            n, err = doc.read(p)
            if err == 'eof':
                continue
            return n, None
        return 0, 'eof'

    # string all documents to text
    def __str__(self) -> str:
        docs: ta.List[str] = []
        for doc in self.docs:
            docs.append(doc.string())
        if len(docs) > 0:
            return '\n'.join(docs) + '\n'
        else:
            return ''


##


# DocumentNode type of Document
@dc.dataclass(kw_only=True)
class DocumentNode(BaseNode):
    start: tokens.Token  # position of DocumentHeader ( `---` )
    end: ta.Optional[tokens.Token] = None  # position of DocumentEnd ( `...` )
    body: ta.Optional[Node]

    # read implements (io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns DocumentNodeType
    def type(self) -> NodeType:
        return NodeType.DOCUMENT

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.body.get_token()

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        if self.body is not None:
            self.body.add_column(col)

    # string document to text
    def __str__(self) -> str:
        doc: ta.List[str] = []
        if self.start is not None:
            doc.append(self.start.value)
        if self.body is not None:
            doc.append(self.body.string())
        if self.end is not None:
            doc.append(self.end.value)
        return '\n'.join(doc)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None


##


# NullNode type of null node
@dc.dataclass(kw_only=True)
class NullNode(ScalarNode, BaseNode):
    token: tokens.Token

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns NullType
    def type(self) -> NodeType:
        return NodeType.NULL

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.token.add_column(col)

    # get_value returns nil value
    def get_value(self) -> ta.Any:
        return None

    # String returns `null` text
    def __str__(self) -> str:
        if self.token.type == tokens.Type.IMPLICIT_NULL:
            if self.comment is not None:
                return self.comment.string()
            return ''
        if self.comment is not None:
            return add_comment_string('null', self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return 'null'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False



##


# IntegerNode type of integer node
@dc.dataclass(kw_only=True)
class IntegerNode(ScalarNode, BaseNode):
    token: tokens.Token
    value: ta.Any  # int64 or uint64 value

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns IntegerType
    def type(self) -> NodeType:
        return NodeType.INTEGER

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.token.add_column(col)

    # get_value returns int64 value
    def get_value(self) -> ta.Any:
        return self.value

    # String int64 to text
    def __str__(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# FloatNode type of float node
@dc.dataclass(kw_only=True)
class FloatNode(ScalarNode, BaseNode):
    token: tokens.Token
    precision: int = 0
    value: float

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns FloatType
    def type(self) -> NodeType:
        return NodeType.FLOAT

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.token.add_column(col)

    # get_value returns float64 value
    def get_value(self) -> ta.Any:
        return self.value

    # String float64 to text
    def __str__(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

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
@dc.dataclass(kw_only=True)
class StringNode(ScalarNode, BaseNode):
    token: tokens.Token
    value: str

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns StringType
    def type(self) -> NodeType:
        return NodeType.STRING

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.token.add_column(col)

    # get_value returns string value
    def get_value(self) -> ta.Any:
        return self.value

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False

    # string string value to text with quote or literal header if required
    def __str__(self) -> str:
        if self.token.type == tokens.Type.SINGLE_QUOTE:
            quoted = escape_single_quote(self.value)
            if self.comment is not None:
                return add_comment_string(quoted, self.comment)
            return quoted
        elif self.token.type == tokens.Type.DOUBLE_QUOTE:
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
        if self.token.type == tokens.Type.SINGLE_QUOTE:
            quoted = f"'{self.value}'"
            return quoted
        elif self.token.type == tokens.Type.DOUBLE_QUOTE:
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
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None


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
@dc.dataclass(kw_only=True)
class LiteralNode(ScalarNode, BaseNode):
    start: tokens.Token
    value: ta.Optional['StringNode'] = None

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns LiteralType
    def type(self) -> NodeType:
        return NodeType.LITERAL

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.start.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # get_value returns string value
    def get_value(self) -> ta.Any:
        return self.string()

    # String literal to text
    def __str__(self) -> str:
        origin = self.value.get_token().origin
        lit = origin.rstrip(' ').rstrip('\n')
        if self.comment is not None:
            return f'{self.start.value} {self.comment.string()}\n{lit}'
        return f'{self.start.value}\n{lit}'

    def string_without_comment(self) -> str:
        return self.string()

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# MergeKeyNode type of merge key node
@dc.dataclass(kw_only=True)
class MergeKeyNode(ScalarNode, BaseNode):
    token: tokens.Token

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns MergeKeyType
    def type(self) -> NodeType:
        return NodeType.MERGE_KEY

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.token

    # get_value returns '<<' value
    def get_value(self) -> ta.Any:
        return self.token.value

    # String returns '<<' value
    def __str__(self) -> str:
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.token.add_column(col)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return str(self), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return True


##


# BoolNode type of boolean node
@dc.dataclass(kw_only=True)
class BoolNode(ScalarNode, BaseNode):
    token: tokens.Token
    value: bool

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns BoolType
    def type(self) -> NodeType:
        return NodeType.BOOL

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.token.add_column(col)

    # get_value returns boolean value
    def get_value(self) -> ta.Any:
        return self.value

    # String boolean to text
    def __str__(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# InfinityNode type of infinity node
@dc.dataclass(kw_only=True)
class InfinityNode(ScalarNode, BaseNode):
    token: tokens.Token
    value: float

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns InfinityType
    def type(self) -> NodeType:
        return NodeType.INFINITY

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.token.add_column(col)

    # get_value returns math.Inf(0) or math.Inf(-1)
    def get_value(self) -> ta.Any:
        return self.value

    # String infinity to text
    def __str__(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# NanNode type of nan node
@dc.dataclass(kw_only=True)
class NanNode(ScalarNode, BaseNode):
    token: tokens.Token

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns NanType
    def type(self) -> NodeType:
        return NodeType.NAN

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.token.add_column(col)

    # get_value returns math.NaN()
    def get_value(self) -> ta.Any:
        return float('nan')

    # String returns .nan
    def __str__(self) -> str:
        if self.comment is not None:
            return add_comment_string(self.token.value, self.comment)
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return self.token.value

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# MapNode interface of MappingValueNode / MappingNode
class MapNode(abc.ABC):
    @abc.abstractmethod
    def map_range(self) -> 'MapNodeIter':
        raise NotImplementedError


START_RANGE_INDEX = -1



# MapNodeIter is an iterator for ranging over a MapNode
@dc.dataclass(kw_only=True)
class MapNodeIter:
    values: ta.List['MappingValueNode']
    idx: int

    # next advances the map iterator and reports whether there is another entry.
    # It returns false when the iterator is exhausted.
    def next(self) -> bool:
        self.idx += 1
        nxt = self.idx < len(self.values)
        return nxt

    # key returns the key of the iterator's current map node entry.
    def key(self) -> MapKeyNode:
        return self.values[self.idx].key

    # value returns the value of the iterator's current map node entry.
    def value(self) -> Node:
        return self.values[self.idx].value

    # key_value returns the MappingValueNode of the iterator's current map node entry.
    def key_value(self) -> 'MappingValueNode':
        return self.values[self.idx]


#


# MappingNode type of mapping node
@dc.dataclass(kw_only=True)
class MappingNode(BaseNode):
    start: tokens.Token
    end: ta.Optional[tokens.Token] = None
    is_flow_style: bool
    values: ta.List['MappingValueNode']
    foot_comment: ta.Optional['CommentGroupNode'] = None

    def start_pos(self) -> tokens.Position:
        if len(self.values) == 0:
            return self.start.position
        return self.values[0].key.get_token().position

    # merge merge key/value of map.
    def merge(self, target: 'MappingNode') -> None:
        key_to_map_value_map: ta.Dict[str, MappingValueNode] = {}
        for value in self.values:
            key = value.key.string()
            key_to_map_value_map[key] = value
        column = self.start_pos().column - target.start_pos().column
        target.add_column(column)
        for value in target.values:
            try:
                map_value, exists = key_to_map_value_map[value.key.string()], True
            except KeyError:
                map_value, exists = None, False
            if exists:
                map_value.value = value.value
            else:
                self.values.append(value)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        for value in self.values:
            value.set_is_flow_style(is_flow)

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns MappingType
    def type(self) -> NodeType:
        return NodeType.MAPPING

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.start.add_column(col)
        self.end.add_column(col)
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
        for value in self.values:
            values.append(value.string())
        map_text = '\n'.join(values)
        if comment_mode and self.comment is not None:
            value = values[0]
            space_num = 0
            for i in range(len(value)):
                if value[i] != ' ':
                    break
                space_num += 1
            comment = self.comment.string_with_space(space_num)
            return f'{comment}\n{map_text}'
        return map_text

    # String mapping values to text
    def __str__(self) -> str:
        if len(self.values) == 0:
            if self.comment is not None:
                return add_comment_string('{}', self.comment)
            return '{}'

        comment_mode = True
        if self.is_flow_style or len(self.values) == 0:
            return self.flow_style_string(comment_mode)

        return self.block_style_string(comment_mode)

    # map_range implements MapNode protocol
    def map_range(self) -> MapNodeIter:
        return MapNodeIter(
            idx=START_RANGE_INDEX,
            values=self.values,
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None


##


# MappingKeyNode type of tag node
@dc.dataclass(kw_only=True)
class MappingKeyNode(MapKeyNode, BaseNode):
    start: tokens.Token
    value: ta.Optional[Node] = None

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns MappingKeyType
    def type(self) -> NodeType:
        return NodeType.MAPPING_KEY

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.start.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # String tag to text
    def __str__(self) -> str:
        return self.string_without_comment()

    def string_without_comment(self) -> str:
        return f'{self.start.value} {self.value.string()}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key, = self.value
        if not isinstance(key, MapKeyNode):
            return False
        return key.is_merge_key()


##


# MappingValueNode type of mapping value
@dc.dataclass(kw_only=True)
class MappingValueNode(BaseNode):
    start: tokens.Token  # delimiter token ':'.
    collect_entry: ta.Optional[tokens.Token] = None  # collect entry token ','.
    key: MapKeyNode
    value: Node
    foot_comment: ta.Optional['CommentGroupNode'] = None
    is_flow_style: bool = False

    # Replace replace value node.
    def replace(self, value: Node) -> ta.Optional[str]:
        column = self.value.get_token().position.column - value.get_token().position.column
        value.add_column(column)
        self.value = value
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns MappingValueType
    def type(self) -> NodeType:
        return NodeType.MAPPING_VALUE

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.start.add_column(col)
        if self.key is not None:
            self.key.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # set_is_flow_style set value to is_flow_style field recursively.
    def set_is_flow_style(self, is_flow: bool) -> None:
        self.is_flow_style = is_flow
        if isinstance(self.value, MappingNode):
            self.value.set_is_flow_style(is_flow)
        elif isinstance(self.value, MappingValueNode):
            self.value.set_is_flow_style(is_flow)
        elif isinstance(self.value, SequenceNode):
            self.value.set_is_flow_style(is_flow)

    # String mapping value to text
    def __str__(self) -> str:
        text: str
        if self.comment is not None:
            text = f'{self.comment.string_with_space(self.key.get_token().position.column - 1)}\n{self.to_string()}'
        else:
            text = self.to_string()

        if self.foot_comment is not None:
            text += f'\n{self.foot_comment.string_with_space(self.key.get_token().position.column - 1)}'

        return text

    def to_string(self) -> str:
        space = ' ' * (self.key.get_token().position.column - 1)
        if check_line_break(self.key.get_token()):
            space = f'\n{space}'

        key_indent_level = self.key.get_token().position.indent_level
        value_indent_level = self.value.get_token().position.indent_level
        key_comment = self.key.get_comment()

        if isinstance(self.value, ScalarNode):
            value = self.value.string()
            if value == '':
                # implicit null value.
                return f'{space}{self.key.string()}:'
            return f'{space}{self.key.string()}: {value}'

        elif key_indent_level < value_indent_level and not self.is_flow_style:
            if key_comment is not None:
                return f'{space}{self.key.string_without_comment()}: {key_comment.string()}\n{self.value.string()}'

            return f'{space}{self.key.string()}:\n{self.value.string()}'

        elif isinstance(self.value, MappingNode) and (self.value.is_flow_style or len(self.value.values) == 0):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, SequenceNode) and (self.value.is_flow_style or len(self.value.values) == 0):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, AnchorNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, AliasNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        elif isinstance(self.value, TagNode):
            return f'{space}{self.key.string()}: {self.value.string()}'

        if key_comment is not None:
            return f'{space}{self.key.string_without_comment()}: {key_comment.string()}\n{self.value.string()}'

        if isinstance(self.value, MappingNode) and self.value.comment is not None:
            return f'{space}{self.key.string()}: {self.value.string().lstrip(" ")}'

        return f'{space}{self.key.string()}:\n{self.value.string()}'

    # map_range implements MapNode protocol
    def map_range(self) -> MapNodeIter:
        return MapNodeIter(
            idx=START_RANGE_INDEX,
            values=[self],
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None


##


# ArrayNode interface of SequenceNode
class ArrayNode(abc.ABC):
    @abc.abstractmethod
    def array_range(self) -> ta.Optional['ArrayNodeIter']:
        raise NotImplementedError


# ArrayNodeIter is an iterator for ranging over a ArrayNode
@dc.dataclass(kw_only=True)
class ArrayNodeIter:
    values: ta.List[Node]
    idx: int

    # next advances the array iterator and reports whether there is another entry.
    # It returns false when the iterator is exhausted.
    def next(self) -> bool:
        self.idx += 1
        nxt = self.idx < len(self.values)
        return nxt

    # Value returns the value of the iterator's current array entry.
    def value(self) -> Node:
        return self.values[self.idx]

    # len returns length of array
    def len(self) -> int:
        return len(self.values)


##


# SequenceNode type of sequence node
@dc.dataclass(kw_only=True)
class SequenceNode(BaseNode):
    start: tokens.Token
    end: ta.Optional[tokens.Token] = None
    is_flow_style: bool
    values: ta.List[Node]
    value_head_comments: ta.List['CommentGroupNode'] = dc.field(default_factory=list)
    entries: ta.List['SequenceEntryNode'] = dc.field(default_factory=list)
    foot_comment: ta.Optional['CommentGroupNode'] = None

    # replace replace value node.
    def replace(self, idx: int, value: Node) -> ta.Optional[str]:
        if len(self.values) <= idx:
            return f'invalid index for sequence: sequence length is {len(self.values):d}, but specified {idx:d} index'

        column = self.values[idx].get_token().position.column - value.get_token().position.column
        value.add_column(column)
        self.values[idx] = value
        return None

    # merge merge sequence value.
    def merge(self, target: 'SequenceNode') -> None:
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
            if isinstance(value, MappingNode):
                value.set_is_flow_style(is_flow)
            elif isinstance(value, MappingValueNode):
                value.set_is_flow_style(is_flow)
            elif isinstance(value, SequenceNode):
                value.set_is_flow_style(is_flow)

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns SequenceType
    def type(self) -> NodeType:
        return NodeType.SEQUENCE

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.start.add_column(col)
        self.end.add_column(col)
        for value in self.values:
            value.add_column(col)

    def flow_style_string(self) -> str:
        values: ta.List[str] = []
        for value in self.values:
            values.append(value.string())

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
            if (len(splitted_values) > 1 and value.type() == NodeType.STRING) or value.type() == NodeType.LITERAL:
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
                    f'{self.value_head_comments[idx].string_with_space(self.start.position.column - 1)}',
                )
                new_line_prefix = ''

            values.append(f'{new_line_prefix}{space}- {new_value}')

        if self.foot_comment is not None:
            values.append(self.foot_comment.string_with_space(self.start.position.column - 1))

        return '\n'.join(values)

    # String sequence to text
    def __str__(self) -> str:
        if self.is_flow_style or len(self.values) == 0:
            return self.flow_style_string()
        return self.block_style_string()

    # array_range implements ArrayNode protocol
    def array_range(self) -> ArrayNodeIter | None:
        return ArrayNodeIter(
            idx=START_RANGE_INDEX,
            values=self.values,
        )

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None


##


# SequenceEntryNode is the sequence entry.
@dc.dataclass(kw_only=True)
class SequenceEntryNode(BaseNode):
    head_comment: 'CommentGroupNode'  # head comment.
    line_comment: ta.Optional['CommentGroupNode'] = None  # line comment e.g.) - # comment.
    start: tokens.Token  # entry token.
    value: Node  # value node.

    # String node to text
    def __str__(self) -> str:
        return ''  # TODO

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    # type returns type of node
    def type(self) -> NodeType:
        return NodeType.SEQUENCE_ENTRY

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.start.add_column(col)

    # set_comment set line comment.
    def set_comment(self, cm: 'CommentGroupNode') -> ta.Optional[str]:
        self.line_comment = cm
        return None

    # comment returns comment token instance
    def get_comment(self) -> 'CommentGroupNode':
        return self.line_comment

    # marshal_yaml
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)


# sequence_entry creates SequenceEntryNode instance.
def sequence_entry(
        start: tokens.Token,
        value: Node,
        head_comment: ta.Optional['CommentGroupNode'],
) -> SequenceEntryNode:
    return SequenceEntryNode(
        head_comment=head_comment,
        start=start,
        value=value,
    )


# SequenceMergeValue creates SequenceMergeValueNode instance.
def sequence_merge_value(*values: MapNode) -> 'SequenceMergeValueNode':
    return SequenceMergeValueNode(
        values=list(values),
    )


##


# SequenceMergeValueNode is used to convert the Sequence node specified for the merge key into a MapNode format.
@dc.dataclass(kw_only=True)
class SequenceMergeValueNode(MapNode):
    values: ta.List[MapNode]

    # map_range returns MapNodeIter instance.
    def map_range(self) -> MapNodeIter:
        ret = MapNodeIter(values=[], idx=START_RANGE_INDEX)
        for value in self.values:
            it = value.map_range()
            ret.values.extend(it.values)
        return ret


##


# AnchorNode type of anchor node
@dc.dataclass(kw_only=True)
class AnchorNode(ScalarNode, BaseNode):
    start: tokens.Token
    name: ta.Optional[Node] = None
    value: ta.Optional[Node] = None

    def string_without_comment(self) -> str:
        return self.value.string()

    def set_name(self, name: str) -> ta.Optional[str]:
        if self.name is None:
            return ERR_INVALID_ANCHOR_NAME
        s = self.name
        if not isinstance(s, StringNode):
            return ERR_INVALID_ANCHOR_NAME
        s.value = name
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns AnchorType
    def type(self) -> NodeType:
        return NodeType.ANCHOR

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    def get_value(self) -> ta.Any:
        return self.value.get_token().value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.start.add_column(col)
        if self.name is not None:
            self.name.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # String anchor to text
    def __str__(self) -> str:
        anchor = '&' + self.name.string()
        value = self.value.string()
        if isinstance(self.value, SequenceNode) and not self.value.is_flow_style:
            return f'{anchor}\n{value}'
        elif isinstance(self.value, MappingNode) and not self.value.is_flow_style:
            return f'{anchor}\n{value}'
        if value == '':
            # implicit null value.
            return anchor
        return f'{anchor} {value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyNode):
            return False
        return key.is_merge_key()


##


# AliasNode type of alias node
@dc.dataclass(kw_only=True)
class AliasNode(ScalarNode, BaseNode):
    start: tokens.Token
    value: ta.Optional[Node] = None

    def string_without_comment(self) -> str:
        return self.value.string()

    def set_name(self, name: str) -> ta.Optional[str]:
        if self.value is None:
            return ERR_INVALID_ALIAS_NAME
        if not isinstance(self.value, StringNode):
            return ERR_INVALID_ALIAS_NAME
        self.value.value = name
        return None

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns AliasType
    def type(self) -> NodeType:
        return NodeType.ALIAS

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    def get_value(self) -> ta.Any:
        return self.value.get_token().value

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.start.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # String alias to text
    def __str__(self) -> str:
        return f'*{self.value.string()}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        return False


##


# DirectiveNode type of directive node
@dc.dataclass(kw_only=True)
class DirectiveNode(BaseNode):
    # Start is '%' token.
    start: tokens.Token
    # Name is directive name e.g.) "YAML" or "TAG".
    name: Node
    # Values is directive values e.g.) "1.2" or "!!" and "tag:clarkevans.com,2002:app/".
    values: ta.List[Node]

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns DirectiveType
    def type(self) -> NodeType:
        return NodeType.DIRECTIVE

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        if self.name is not None:
            self.name.add_column(col)
        for value in self.values:
            value.add_column(col)

    # String directive to text
    def __str__(self) -> str:
        values: ta.List[str] = []
        for val in self.values:
            values.append(val.string())
        return ' '.join(['%' + self.name.string(), *values])

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None


##


# TagNode type of tag node
@dc.dataclass(kw_only=True)
class TagNode(ScalarNode, BaseNode):
    directive: DirectiveNode
    start: tokens.Token
    value: Node

    def get_value(self) -> ta.Any:
        if not isinstance(self.value, ScalarNode):
            return None
        return self.value.get_value()

    def string_without_comment(self) -> str:
        return self.value.string()

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns TagType
    def type(self) -> NodeType:
        return NodeType.TAG

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.start

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        self.start.add_column(col)
        if self.value is not None:
            self.value.add_column(col)

    # String tag to text
    def __str__(self) -> str:
        value = self.value.string()
        if isinstance(self.value, SequenceNode) and not self.value.is_flow_style:
            return f'{self.start.value}\n{value}'
        elif isinstance(self.value, MappingNode) and not self.value.is_flow_style:
            return f'{self.start.value}\n{value}'

        return f'{self.start.value} {value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None

    # is_merge_key returns whether it is a MergeKey node.
    def is_merge_key(self) -> bool:
        if self.value is None:
            return False
        key = self.value
        if not isinstance(key, MapKeyNode):
            return False
        return key.is_merge_key()

    def array_range(self) -> ArrayNodeIter | None:
        arr = self.value
        if not isinstance(arr, ArrayNode):
            return None
        return arr.array_range()


##


# CommentNode type of comment node
@dc.dataclass(kw_only=True)
class CommentNode(BaseNode):
    token: tokens.Token

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns CommentType
    def type(self) -> NodeType:
        return NodeType.COMMENT

    # get_token returns token instance
    def get_token(self) -> tokens.Token:
        return self.token

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        if self.token is None:
            return
        self.token.add_column(col)

    # String comment to text
    def __str__(self) -> str:
        return f'#{self.token.value}'

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None


##


# CommentGroupNode type of comment node
@dc.dataclass(kw_only=True)
class CommentGroupNode(BaseNode):
    comments: ta.List[CommentNode]

    # read implements(io.Reader).Read
    def read(self, p: str) -> ta.Tuple[int, ta.Optional[str]]:
        return read_node(p, self)

    # type returns CommentType
    def type(self) -> NodeType:
        return NodeType.COMMENT

    # get_token returns token instance
    def get_token(self) -> ta.Optional[tokens.Token]:
        if len(self.comments) > 0:
            return self.comments[0].token
        return None

    # add_column add column number to child nodes recursively
    def add_column(self, col: int) -> None:
        for comment in self.comments:
            comment.add_column(col)

    # String comment to text
    def __str__(self) -> str:
        values: ta.List[str] = []
        for comment in self.comments:
            values.append(comment.string())
        return '\n'.join(values)

    def string_with_space(self, col: int) -> str:
        values: ta.List[str] = []
        space = ' ' * col
        for comment in self.comments:
            spc = space
            if check_line_break(comment.token):
                spc = f'\n{spc}'
            values.append(spc + comment.string())
        return '\n'.join(values)

    # marshal_yaml encodes to a YAML text
    def marshal_yaml(self) -> ta.Tuple[str, ta.Optional[str]]:
        return self.string(), None


##


# Visitor has Visit method that is invokded for each node encountered by walk.
# If the result visitor w is not nil, walk visits each of the children of node with the visitor w,
# followed by a call of w.visit(nil).
class Visitor(abc.ABC):
    @abc.abstractmethod
    def visit(self, node: Node) -> 'Visitor':
        raise NotImplementedError


# walk traverses an AST in depth-first order: It starts by calling v.visit(node); node must not be nil.
# If the visitor w returned by v.visit(node) is not nil,
# walk is invoked recursively with visitor w for each of the non-nil children of node,
# followed by a call of w.visit(nil).
def walk(v: Visitor, node: Node) -> None:
    if (v := v.visit(node)) is None:
        return

    n = node
    if isinstance(n, (CommentNode, NullNode)):
        walk_comment(v, n)
    if isinstance(n, IntegerNode):
        walk_comment(v, n)
    if isinstance(n, FloatNode):
        walk_comment(v, n)
    if isinstance(n, StringNode):
        walk_comment(v, n)
    if isinstance(n, MergeKeyNode):
        walk_comment(v, n)
    if isinstance(n, BoolNode):
        walk_comment(v, n)
    if isinstance(n, InfinityNode):
        walk_comment(v, n)
    if isinstance(n, NanNode):
        walk_comment(v, n)
    if isinstance(n, LiteralNode):
        walk_comment(v, n)
        walk(v, n.value)
    if isinstance(n, DirectiveNode):
        walk_comment(v, n)
        walk(v, n.name)
        for value in n.values:
            walk(v, value)
    if isinstance(n, TagNode):
        walk_comment(v, n)
        walk(v, n.value)
    if isinstance(n, DocumentNode):
        walk_comment(v, n)
        walk(v, n.body)
    if isinstance(n, MappingNode):
        walk_comment(v, n)
        for value in n.values:
            walk(v, value)
    if isinstance(n, MappingKeyNode):
        walk_comment(v, n)
        walk(v, n.value)
    if isinstance(n, MappingValueNode):
        walk_comment(v, n)
        walk(v, n.key)
        walk(v, n.value)
    if isinstance(n, SequenceNode):
        walk_comment(v, n)
        for value in n.values:
            walk(v, value)
    if isinstance(n, AnchorNode):
        walk_comment(v, n)
        walk(v, n.name)
        walk(v, n.value)
    if isinstance(n, AliasNode):
        walk_comment(v, n)
        walk(v, n.value)


def walk_comment(v: Visitor, base: BaseNode | None) -> None:
    if base is None:
        return
    if base.comment is None:
        return
    walk(v, base.comment)


#


@dc.dataclass(kw_only=True)
class FilterWalker(Visitor):
    typ: NodeType
    results: ta.List[Node]

    def visit(self, n: Node) -> Visitor:
        if self.typ == n.type():
            self.results.append(n)
        return self


#


@dc.dataclass(kw_only=True)
class ParentFinder:
    target: Node

    def walk(self, parent: Node, node: Node) -> ta.Optional[Node]:
        if self.target == node:
            return parent

        n = node
        if isinstance(n, CommentNode):
            return None
        if isinstance(n, NullNode):
            return None
        if isinstance(n, IntegerNode):
            return None
        if isinstance(n, FloatNode):
            return None
        if isinstance(n, StringNode):
            return None
        if isinstance(n, MergeKeyNode):
            return None
        if isinstance(n, BoolNode):
            return None
        if isinstance(n, InfinityNode):
            return None
        if isinstance(n, NanNode):
            return None
        if isinstance(n, LiteralNode):
            return self.walk(node, n.value)
        if isinstance(n, DirectiveNode):
            if (found := self.walk(node, n.name)) is not None:
                return found
            for value in n.values:
                if (found := self.walk(node, value)) is not None:
                    return found
        if isinstance(n, TagNode):
            return self.walk(node, n.value)
        if isinstance(n, DocumentNode):
            return self.walk(node, n.body)
        if isinstance(n, MappingNode):
            for value in n.values:
                if (found := self.walk(node, value)) is not None:
                    return found
        if isinstance(n, MappingKeyNode):
            return self.walk(node, n.value)
        if isinstance(n, MappingValueNode):
            if (found := self.walk(node, n.key)) is not None:
                return found
            return self.walk(node, n.value)
        if isinstance(n, SequenceNode):
            for value in n.values:
                if (found := self.walk(node, value)) is not None:
                    return found
        if isinstance(n, AnchorNode):
            if (found := self.walk(node, n.name)) is not None:
                return found
            return self.walk(node, n.value)
        if isinstance(n, AliasNode):
            return self.walk(node, n.value)
        return None


# Parent get parent node from child node.
def parent(root: Node, child: Node) -> Node:
    finder = ParentFinder(target=child)
    return finder.walk(root, root)


#


# Filter returns a list of nodes that match the given type.
def filter_(typ: NodeType, node: Node) -> ta.List[Node]:
    walker = FilterWalker(typ=typ)
    walk(walker, node)
    return walker.results


# FilterFile returns a list of nodes that match the given type.
def filter_file(typ: NodeType, file: File) -> ta.List[Node]:
    results: ta.List[Node] = []
    for doc in file.docs:
        walker = FilterWalker(typ=typ)
        walk(walker, doc)
        results.extend(walker.results)
    return results


#


@dc.dataclass(kw_only=True)
class ErrInvalidMergeType:
    dst: Node
    src: Node

    def error(self) -> str:
        return f'cannot merge {self.src.type()} into {self.dst.type()}'


# Merge merge document, map, sequence node.
def merge(dst: Node, src: Node) -> ta.Optional[str]:
    if isinstance(src, DocumentNode):
        doc: DocumentNode = src
        src = doc.body

    err = ErrInvalidMergeType(dst=dst, src=src)
    if dst.type() == NodeType.DOCUMENT:
        node: DocumentNode = dst
        return merge(node.body, src)
    if dst.type() == NodeType.MAPPING:
        node: MappingNode = dst
        if not isinstance(src, MappingNode):
            return err
        target: MappingNode = src
        node.merge(target)
        return None
    if dst.type() == NodeType.SEQUENCE:
        node: SequenceNode = dst
        if not isinstance(target := src, SequenceNode):
            return err
        node.merge(target)
        return None
    return err.error()
