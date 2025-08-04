# ruff: noqa: UP006 UP007 UP043 UP045
import copy
import dataclasses as dc
import enum
import typing as ta

from omlish.lite.check import check

from . import ast
from . import scanning
from . import tokens
from . import tokens as tokens_
from .errors import YamlError
from .errors import YamlErrorOr
from .errors import yaml_error


##


# context context at parsing
@dc.dataclass(kw_only=True)
class Context:
    token_ref: ta.Optional['TokenRef'] = None
    path: str
    is_flow: bool = False

    def current_token(self) -> ta.Optional['Token']:
        if self.token_ref.idx >= self.token_ref.size:
            return None

        return self.token_ref.tokens[self.token_ref.idx]

    def is_comment(self) -> bool:
        return Token.type(self.current_token()) == tokens_.Type.COMMENT

    def next_token(self) -> ta.Optional['Token']:
        if self.token_ref.idx + 1 >= self.token_ref.size:
            return None

        return self.token_ref.tokens[self.token_ref.idx + 1]

    def next_not_comment_token(self) -> ta.Optional['Token']:
        for i in range(self.token_ref.idx + 1, self.token_ref.size):
            tk = self.token_ref.tokens[i]
            if tk.type() == tokens_.Type.COMMENT:
                continue
            return tk

        return None

    def is_token_not_found(self) -> bool:
        return self.current_token() is None

    def with_group(self, g: 'TokenGroup') -> 'Context':
        ctx = copy.copy(self)
        ctx.token_ref = TokenRef(
            tokens=g.tokens,
            size=len(g.tokens),
        )
        return ctx

    def with_child(self, path: str) -> 'Context':
        ctx = copy.copy(self)
        ctx.path = self.path + '.' + normalize_path(path)
        return ctx

    def with_index(self, idx: int) -> 'Context':
        ctx = copy.copy(self)
        ctx.path = self.path + '[' + str(idx) + ']'
        return ctx

    def with_flow(self, is_flow: bool) -> 'Context':
        ctx = copy.copy(self)
        ctx.is_flow = is_flow
        return ctx

    @staticmethod
    def new_context() -> 'Context':
        return Context(
            path= '$',
        )

    def go_next(self) -> None:
        ref = self.token_ref
        if ref.size <= ref.idx+1:
            ref.idx = ref.size
        else:
            ref.idx += 1

    def next(self) -> bool:
        return self.token_ref.idx < self.token_ref.size

    def insert_null_token(self, tk: 'Token') -> 'Token':
        null_token = self.create_implicit_null_token(tk)
        self.insert_token(null_token)
        self.go_next()

        return null_token

    def add_null_value_token(self, tk: 'Token') -> 'Token':
        null_token = self.create_implicit_null_token(tk)
        raw_tk = null_token.raw_token()

        # add space for map or sequence value.
        raw_tk.position.column += 1

        self.add_token(null_token)
        self.go_next()

        return null_token

    def create_implicit_null_token(self, base: 'Token') -> 'Token':
        pos = copy.copy(base.raw_token().position)
        pos.column+=1
        tk = tokens.new('null', ' null', pos)
        tk.type = tokens_.Type.IMPLICIT_NULL
        return Token(token=tk)

    def insert_token(self, tk: 'Token') -> None:
        ref = self.token_ref
        idx = ref.idx
        if ref.size < idx:
            return

        if ref.size == idx:
            cur_token = ref.tokens[ref.size-1]
            tk.raw_token().next = cur_token.raw_token()
            cur_token.raw_token().prev = tk.raw_token()

            ref.tokens.append(tk)
            ref.size = len(ref.tokens)
            return

        cur_token = ref.tokens[idx]
        tk.raw_token().next = cur_token.raw_token()
        cur_token.raw_token().prev = tk.raw_token()

        ref.tokens = [*ref.tokens[:idx+1], *ref.tokens[idx:]]
        ref.tokens[idx] = tk
        ref.size = len(ref.tokens)

    def add_token(self, tk: 'Token') -> None:
        ref = self.token_ref
        last_tk = ref.tokens[ref.size-1]
        if last_tk.group is not None:
            last_tk = last_tk.group.last()

        last_tk.raw_token().next = tk.raw_token()
        tk.raw_token().prev = last_tk.raw_token()

        ref.tokens.append(tk)
        ref.size = len(ref.tokens)


@dc.dataclass(kw_only=True)
class TokenRef:
    tokens: ta.List['Token']
    size: int
    idx: int = 0


##


PATH_SPECIAL_CHARS = (
    '$', '*', '.', '[', ']',
)


def contains_path_special_char(path: str) -> bool:
    return any(char in path for char in PATH_SPECIAL_CHARS)


def normalize_path(path: str) -> str:
    if contains_path_special_char(path):
        return f"'{path}'"

    return path


##


# Option represents parser's option.
Option: ta.TypeAlias = ta.Callable[['Parser'], None]


# AllowDuplicateMapKey allow the use of keys with the same name in the same map, but by default, this is not permitted.
def allow_duplicate_map_key() -> Option:
    def fn(p: 'Parser') -> None:
        p.allow_duplicate_map_key = True

    return fn


##


class TokenGroupType(enum.Enum):
    NONE = enum.auto()
    DIRECTIVE = enum.auto()
    DIRECTIVE_NAME = enum.auto()
    DOCUMENT = enum.auto()
    DOCUMENT_BODY = enum.auto()
    ANCHOR = enum.auto()
    ANCHOR_NAME = enum.auto()
    ALIAS = enum.auto()
    LITERAL = enum.auto()
    FOLDED = enum.auto()
    SCALAR_TAG = enum.auto()
    MAP_KEY = enum.auto()
    MAP_KEY_VALUE = enum.auto()


@dc.dataclass(kw_only=True)
class Token:
    token: ta.Optional[tokens.Token] = None
    group: ta.Optional['TokenGroup'] = None
    line_comment: ta.Optional[tokens.Token] = None

    def raw_token(self: ta.Optional['Token']) -> ta.Optional[tokens.Token]:
        if self is None:
            return None

        if self.token is not None:
            return self.token

        return self.group.raw_token()

    def type(self: ta.Optional['Token']) -> tokens.Type:
        if self is None:
            return tokens_.Type.UNKNOWN
        if self.token is not None:
            return self.token.type
        return self.group.token_type()

    def group_type(self: ta.Optional['Token']) -> TokenGroupType:
        if self is None:
            return TokenGroupType.NONE
        if self.token is not None:
            return TokenGroupType.NONE
        return self.group.type

    def line(self: ta.Optional['Token']) -> int:
        if self is None:
            return 0
        if self.token is not None:
            return self.token.position.line
        return self.group.line()

    def column(self: ta.Optional['Token']) -> int:
        if self is None:
            return 0
        if self.token is not None:
            return self.token.position.column
        return self.group.column()

    def set_group_type(self, typ: TokenGroupType) -> None:
        if self.group is None:
            return
        self.group.type = typ


##


@dc.dataclass(kw_only=True)
class TokenGroup:
    type: TokenGroupType = TokenGroupType.NONE
    tokens: ta.List[Token]

    def first(self) -> ta.Optional[Token]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0]

    def last(self) -> ta.Optional[Token]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[len(self.tokens) - 1]

    def raw_token(self) -> ta.Optional[tokens_.Token]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0].raw_token()

    def line(self) -> int:
        if len(self.tokens) == 0:
            return 0
        return self.tokens[0].line()

    def column(self) -> int:
        if len(self.tokens) == 0:
            return 0
        return self.tokens[0].column()

    def token_type(self) -> tokens_.Type:
        if len(self.tokens) == 0:
            return tokens_.Type.UNKNOWN
        return self.tokens[0].type()


def create_grouped_tokens(tokens: tokens.Tokens) -> YamlErrorOr[ta.List[Token]]:
    tks: YamlErrorOr[ta.List[Token]] = new_tokens(tokens)

    tks = create_line_comment_token_groups(tks)

    tks = create_literal_and_folded_token_groups(tks)
    if isinstance(tks, YamlError):
        return tks

    tks = create_anchor_and_alias_token_groups(tks)
    if isinstance(tks, YamlError):
        return tks

    tks = create_scalar_tag_token_groups(tks)
    if isinstance(tks, YamlError):
        return tks

    tks = create_anchor_with_scalar_tag_token_groups(tks)
    if isinstance(tks, YamlError):
        return tks

    tks = create_map_key_token_groups(tks)
    if isinstance(tks, YamlError):
        return tks

    tks = create_map_key_value_token_groups(tks)

    tks = create_directive_token_groups(tks)
    if isinstance(tks, YamlError):
        return tks

    tks = create_document_tokens(tks)
    if isinstance(tks, YamlError):
        return tks

    return tks


def new_tokens(tks: tokens.Tokens) -> ta.List[Token]:
    ret: ta.List[Token] = []
    for tk in tks:
        ret.append(Token(token=tk))
    return ret


def create_line_comment_token_groups(tokens: ta.List[Token]) -> ta.List[Token]:
    ret: ta.List[Token] = []
    for i in range(len(tokens)):
        tk = tokens[i]
        if tk.type() == tokens_.Type.COMMENT:
            if i > 0 and tokens[i - 1].line() == tk.line():
                tokens[i - 1].line_comment = tk.raw_token()
            else:
                ret.append(tk)
        else:
            ret.append(tk)
    return ret


def create_literal_and_folded_token_groups(tokens: ta.List[Token]) -> YamlErrorOr[ta.List[Token]]:
    ret: ta.List[Token] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == tokens_.Type.LITERAL:
            tks: ta.List[Token] = [tk]
            if i + 1 < len(tokens):
                tks.append(tokens[i + 1])
            ret.append(Token(
                group=TokenGroup(
                    type=TokenGroupType.LITERAL,
                    tokens=tks,
                ),
            ))
            i += 1
        elif tk.type() == tokens_.Type.FOLDED:
            tks: ta.List[Token] = [tk]
            if i + 1 < len(tokens):
                tks.append(tokens[i + 1])
            ret.append(Token(
                group=TokenGroup(
                    type=TokenGroupType.FOLDED,
                    tokens=tks,
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def err_syntax(msg: str, tk: ta.Optional[tokens.Token]) -> YamlError:
    return yaml_error(f'Syntax error: {msg}, {tk}')


def create_anchor_and_alias_token_groups(tokens: ta.List[Token]) -> YamlErrorOr[ta.List[Token]]:
    ret: ta.List[Token] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == tokens_.Type.ANCHOR:
            if i + 1 >= len(tokens):
                return err_syntax('undefined anchor name', tk.raw_token())
            if i + 2 >= len(tokens):
                return err_syntax('undefined anchor value', tk.raw_token())
            anchor_name = Token(
                group=TokenGroup(
                    type=TokenGroupType.ANCHOR_NAME,
                    tokens=[tk, tokens[i + 1]],
                ),
            )
            value_tk = tokens[i + 2]
            if tk.line() == value_tk.line() and value_tk.type() == tokens_.Type.SEQUENCE_ENTRY:
                return err_syntax(
                    'sequence entries are not allowed after anchor on the same line',
                    value_tk.raw_token(),
                )
            if tk.line() == value_tk.line() and is_scalar_type(value_tk):
                ret.append(Token(
                    group=TokenGroup(
                        type=TokenGroupType.ANCHOR,
                        tokens=[anchor_name, value_tk],
                    ),
                ))
                i += 1
            else:
                ret.append(anchor_name)
            i += 1
        elif tk.type() == tokens_.Type.ALIAS:
            if i + 1 == len(tokens):
                return err_syntax('undefined alias name', tk.raw_token())
            ret.append(Token(
                group=TokenGroup(
                    type=TokenGroupType.ALIAS,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def create_scalar_tag_token_groups(tokens: ta.List[Token]) -> YamlErrorOr[ta.List[Token]]:
    ret: ta.List[Token] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() != tokens_.Type.TAG:
            ret.append(tk)
            continue
        tag = tk.raw_token()
        if tag.value.startswith('!!'):
            # secondary tag.
            if tag.value in (
                    tokens_.ReservedTagKeywords.INTEGER,
                    tokens_.ReservedTagKeywords.FLOAT,
                    tokens_.ReservedTagKeywords.STRING,
                    tokens_.ReservedTagKeywords.BINARY,
                    tokens_.ReservedTagKeywords.TIMESTAMP,
                    tokens_.ReservedTagKeywords.BOOLEAN,
                    tokens_.ReservedTagKeywords.NULL,
            ):
                if len(tokens) <= i + 1:
                    ret.append(tk)
                    continue
                if tk.line() != tokens[i + 1].line():
                    ret.append(tk)
                    continue
                if tokens[i + 1].group_type() == TokenGroupType.ANCHOR_NAME:
                    ret.append(tk)
                    continue
                if is_scalar_type(tokens[i + 1]):
                    ret.append(Token(
                        group=TokenGroup(
                            type=TokenGroupType.SCALAR_TAG,
                            tokens=[tk, tokens[i + 1]],
                        ),
                    ))
                    i += 1
                else:
                    ret.append(tk)
            elif tag.value == tokens_.ReservedTagKeywords.MERGE:
                if len(tokens) <= i + 1:
                    ret.append(tk)
                    continue
                if tk.line() != tokens[i + 1].line():
                    ret.append(tk)
                    continue
                if tokens[i + 1].group_type() == TokenGroupType.ANCHOR_NAME:
                    ret.append(tk)
                    continue
                if tokens[i + 1].type() != tokens_.Type.MERGE_KEY:
                    return err_syntax('could not find merge key', tokens[i + 1].raw_token())
                ret.append(Token(
                    group=TokenGroup(
                        type=TokenGroupType.SCALAR_TAG,
                        tokens=[tk, tokens[i + 1]],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
        else:
            if len(tokens) <= i + 1:
                ret.append(tk)
                continue
            if tk.line() != tokens[i + 1].line():
                ret.append(tk)
                continue
            if tokens[i + 1].group_type() == TokenGroupType.ANCHOR_NAME:
                ret.append(tk)
                continue
            if is_flow_type(tokens[i + 1]):
                ret.append(tk)
                continue
            ret.append(Token(
                group=TokenGroup(
                    type=TokenGroupType.SCALAR_TAG,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
    return ret


def create_anchor_with_scalar_tag_token_groups(tokens: ta.List[Token]) -> YamlErrorOr[ta.List[Token]]:
    ret: ta.List[Token] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.group_type() == TokenGroupType.ANCHOR_NAME:
            if i + 1 >= len(tokens):
                return err_syntax('undefined anchor value', tk.raw_token())
            value_tk = tokens[i + 1]
            if tk.line() == value_tk.line() and value_tk.group_type() == TokenGroupType.SCALAR_TAG:
                ret.append(Token(
                    group=TokenGroup(
                        type=TokenGroupType.ANCHOR,
                        tokens=[tk, tokens[i + 1]],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
        else:
            ret.append(tk)
    return ret


def create_map_key_token_groups(tokens: ta.List[Token]) -> YamlErrorOr[ta.List[Token]]:
    tks = create_map_key_by_mapping_key(tokens)
    if isinstance(tks, YamlError):
        return tks
    return create_map_key_by_mapping_value(tks)


def create_map_key_by_mapping_key(tokens: ta.List[Token]) -> YamlErrorOr[ta.List[Token]]:
    ret: ta.List[Token] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == tokens_.Type.MAPPING_KEY:
            if i + 1 >= len(tokens):
                return err_syntax('undefined map key', tk.raw_token())
            ret.append(Token(
                group=TokenGroup(
                    type=TokenGroupType.MAP_KEY,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def create_map_key_by_mapping_value(tokens: ta.List[Token]) -> YamlErrorOr[ta.List[Token]]:
    ret: ta.List[Token] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == tokens_.Type.MAPPING_VALUE:
            if i == 0:
                return err_syntax('unexpected key name', tk.raw_token())
            map_key_tk = tokens[i - 1]
            if is_not_map_key_type(map_key_tk):
                return err_syntax('found an invalid key for this map', tokens[i].raw_token())
            new_tk = Token(
                token=map_key_tk.token,
                group=map_key_tk.group,
            )
            map_key_tk.token = None
            map_key_tk.group = TokenGroup(
                type=TokenGroupType.MAP_KEY,
                tokens=[new_tk, tk],
            )
        else:
            ret.append(tk)
    return ret


def create_map_key_value_token_groups(tokens: ta.List[Token]) -> ta.List[Token]:
    ret: ta.List[Token] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.group_type() == TokenGroupType.MAP_KEY:
            if len(tokens) <= i + 1:
                ret.append(tk)
                continue
            value_tk = tokens[i + 1]
            if tk.line() != value_tk.line():
                ret.append(tk)
                continue
            if value_tk.group_type() == TokenGroupType.ANCHOR_NAME:
                ret.append(tk)
                continue
            if value_tk.type() == tokens_.Type.TAG and value_tk.group_type() != TokenGroupType.SCALAR_TAG:
                ret.append(tk)
                continue

            if is_scalar_type(value_tk) or value_tk.type() == tokens_.Type.TAG:
                ret.append(Token(
                    group=TokenGroup(
                        type=TokenGroupType.MAP_KEY_VALUE,
                        tokens=[tk, value_tk],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
                continue
        else:
            ret.append(tk)
    return ret


def create_directive_token_groups(tokens: ta.List[Token]) -> YamlErrorOr[ta.List[Token]]:
    ret: ta.List[Token] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == tokens_.Type.DIRECTIVE:
            if i + 1 >= len(tokens):
                return err_syntax('undefined directive value', tk.raw_token())
            directive_name = Token(
                group=TokenGroup(
                    type=TokenGroupType.DIRECTIVE_NAME,
                    tokens=[tk, tokens[i + 1]],
                ),
            )
            i += 1
            value_tks: ta.List[Token] = []
            for j in range(i + 1, len(tokens)):
                if tokens[j].line() != tk.line():
                    break
                value_tks.append(tokens[j])
                i += 1
            if i + 1 >= len(tokens) or tokens[i + 1].type() != tokens_.Type.DOCUMENT_HEADER:
                return err_syntax('unexpected directive value. document not started', tk.raw_token())
            if len(value_tks) != 0:
                ret.append(Token(
                    group=TokenGroup(
                        type=TokenGroupType.DIRECTIVE,
                        tokens=[directive_name, *value_tks],
                    ),
                ))
            else:
                ret.append(directive_name)
        else:
            ret.append(tk)
    return ret


def create_document_tokens(tokens: ta.List[Token]) -> YamlErrorOr[ta.List[Token]]:
    ret: ta.List[Token] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == tokens_.Type.DOCUMENT_HEADER:
            if i != 0:
                ret.append(Token(
                    group=TokenGroup(tokens=tokens[:i]),
                ))
            if i + 1 == len(tokens):
                # if current token is last token, add DocumentHeader only tokens to ret.
                ret.append(Token(
                    group=TokenGroup(
                        type=TokenGroupType.DOCUMENT,
                        tokens=[tk],
                    ),
                ))
                return ret
            if tokens[i + 1].type() == tokens_.Type.DOCUMENT_HEADER:
                ret.append(Token(
                    group=TokenGroup(
                        type=TokenGroupType.DOCUMENT,
                        tokens=[tk],
                    ),
                ))
                return ret
            if tokens[i].line() == tokens[i + 1].line():
                if tokens[i + 1].group_type() in (
                        TokenGroupType.MAP_KEY,
                        TokenGroupType.MAP_KEY_VALUE,
                ):
                    return err_syntax(
                        'value cannot be placed after document separator',
                        tokens[i + 1].raw_token(),
                    )
                if tokens[i + 1].type() == tokens_.Type.SEQUENCE_ENTRY:
                    return err_syntax(
                        'value cannot be placed after document separator',
                        tokens[i + 1].raw_token(),
                    )
            tks = create_document_tokens(tokens[i + 1:])
            if isinstance(tks, YamlError):
                return tks
            if len(tks) != 0:
                tks[0].set_group_type(TokenGroupType.DOCUMENT)
                tks[0].group.tokens = list(tks[0].group.tokens)
                ret.extend(tks)
                return ret
            ret.append(Token(
                group=TokenGroup(
                    type=TokenGroupType.DOCUMENT,
                    tokens=[tk],
                ),
            ))
            return ret
        elif tk.type() == tokens_.Type.DOCUMENT_END:
            if i != 0:
                ret.append(Token(
                    group=TokenGroup(
                        type=TokenGroupType.DOCUMENT,
                        tokens=tokens[0: i + 1],
                    ),
                ))
            if i + 1 == len(tokens):
                return ret
            if is_scalar_type(tokens[i + 1]):
                return err_syntax('unexpected end content', tokens[i + 1].raw_token())

            tks = create_document_tokens(tokens[i + 1:])
            if isinstance(tks, YamlError):
                return tks
            ret.extend(tks)
            return ret
    ret.append(Token(
        group=TokenGroup(
            type=TokenGroupType.DOCUMENT,
            tokens=tokens,
        ),
    ))
    return ret


def is_scalar_type(tk: Token) -> bool:
    if tk.group_type() in (TokenGroupType.MAP_KEY, TokenGroupType.MAP_KEY_VALUE):
        return False
    typ = tk.type()
    return typ in (
        tokens_.Type.ANCHOR,
        tokens_.Type.ALIAS,
        tokens_.Type.LITERAL,
        tokens_.Type.FOLDED,
        tokens_.Type.NULL,
        tokens_.Type.IMPLICIT_NULL,
        tokens_.Type.BOOL,
        tokens_.Type.INTEGER,
        tokens_.Type.BINARY_INTEGER,
        tokens_.Type.OCTET_INTEGER,
        tokens_.Type.HEX_INTEGER,
        tokens_.Type.FLOAT,
        tokens_.Type.INFINITY,
        tokens_.Type.NAN,
        tokens_.Type.STRING,
        tokens_.Type.SINGLE_QUOTE,
        tokens_.Type.DOUBLE_QUOTE,
    )

def is_not_map_key_type(tk: Token) -> bool:
    typ = tk.type()
    return typ in (
        tokens_.Type.DIRECTIVE,
        tokens_.Type.DOCUMENT_HEADER,
        tokens_.Type.DOCUMENT_END,
        tokens_.Type.COLLECT_ENTRY,
        tokens_.Type.MAPPING_START,
        tokens_.Type.MAPPING_VALUE,
        tokens_.Type.MAPPING_END,
        tokens_.Type.SEQUENCE_START,
        tokens_.Type.SEQUENCE_ENTRY,
        tokens_.Type.SEQUENCE_END,
    )


def is_flow_type(tk: Token) -> bool:
    typ = tk.type()
    return typ in (
        tokens_.Type.MAPPING_START,
        tokens_.Type.MAPPING_END,
        tokens_.Type.SEQUENCE_START,
        tokens_.Type.SEQUENCE_ENTRY,
    )


##


def new_mapping_node(
        ctx: Context,
        tk: Token,
        is_flow: bool,
        *values: ast.MappingValueNode,
) -> YamlErrorOr[ast.MappingNode]:
    node = ast.mapping(tk.raw_token(), is_flow, *values)
    node.set_path(ctx.path)
    return node


def new_mapping_value_node(
        ctx: Context,
        colon_tk: Token,
        entry_tk: ta.Optional[Token],
        key: ast.MapKeyNode,
        value: ast.Node,
) -> YamlErrorOr[ast.MappingValueNode]:
    node = ast.mapping_value(colon_tk.raw_token(), key, value)
    node.set_path(ctx.path)
    node.collect_entry = Token.raw_token(entry_tk)
    if key.get_token().position.line == value.get_token().position.line:
        # originally key was commented, but now that null value has been added, value must be commented.
        if (err := set_line_comment(ctx, value, colon_tk)) is not None:
            return err
        # set line comment by colon_tk or entry_tk.
        if (err := set_line_comment(ctx, value, entry_tk)) is not None:
            return err
    else:
        if (err := set_line_comment(ctx, key, colon_tk)) is not None:
            return err
        # set line comment by colon_tk or entry_tk.
        if (err := set_line_comment(ctx, key, entry_tk)) is not None:
            return err
    return node


def new_mapping_key_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.MappingKeyNode]:
    node = ast.mapping_key(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_anchor_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.AnchorNode]:
    node = ast.anchor(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_alias_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.AliasNode]:
    node = ast.alias(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_directive_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.DirectiveNode]:
    node = ast.directive(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_merge_key_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.MergeKeyNode]:
    node = ast.merge_key(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_null_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.NullNode]:
    node = ast.null(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_bool_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.BoolNode]:
    node = ast.bool_(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_integer_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.IntegerNode]:
    node = ast.integer(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_float_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.FloatNode]:
    node = ast.float_(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_infinity_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.InfinityNode]:
    node = ast.infinity(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_nan_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.NanNode]:
    node = ast.nan(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_string_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.StringNode]:
    node = ast.string(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_literal_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.LiteralNode]:
    node = ast.literal(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_tag_node(ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.TagNode]:
    node = ast.tag(Token.raw_token(tk))
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_sequence_node(ctx: Context, tk: ta.Optional[Token], is_flow: bool) -> YamlErrorOr[ast.SequenceNode]:
    node = ast.sequence(Token.raw_token(tk), is_flow)
    node.set_path(ctx.path)
    if (err := set_line_comment(ctx, node, tk)) is not None:
        return err
    return node


def new_tag_default_scalar_value_node(ctx: Context, tag: tokens_.Token) -> YamlErrorOr[ast.ScalarNode]:
    pos = copy.copy(tag.position)
    pos.column += 1

    tk: YamlErrorOr[Token]
    node: YamlErrorOr[ast.ScalarNode]

    if tag.value == tokens_.ReservedTagKeywords.INTEGER:
        tk = Token(token=tokens.new('0', '0', pos))
        n = new_integer_node(ctx, tk)
        if isinstance(n, YamlError):
            return n
        node = n
    elif tag.value == tokens_.ReservedTagKeywords.FLOAT:
        tk = Token(token=tokens_.new('0', '0', pos))
        n = new_float_node(ctx, tk)
        if isinstance(n, YamlError):
            return n
        node = n
    elif tag.value in (
            tokens_.ReservedTagKeywords.STRING,
            tokens_.ReservedTagKeywords.BINARY,
            tokens_.ReservedTagKeywords.TIMESTAMP,
    ):
        tk = Token(token=tokens_.new('', '', pos))
        n = new_string_node(ctx, tk)
        if isinstance(n, YamlError):
            return n
        node = n
    elif tag.value == tokens_.ReservedTagKeywords.BOOLEAN:
        tk = Token(token=tokens_.new('false', 'false', pos))
        n = new_bool_node(ctx, tk)
        if isinstance(n, YamlError):
            return n
        node = n
    elif tag.value == tokens_.ReservedTagKeywords.NULL:
        tk = Token(token=tokens_.new('null', 'null', pos))
        n = new_null_node(ctx, tk)
        if isinstance(n, YamlError):
            return n
        node = n
    else:
        return err_syntax(f'cannot assign default value for {tag.value!r} tag', tag)
    ctx.insert_token(tk)
    ctx.go_next()
    return node


def set_line_comment(ctx: Context, node: ast.Node, tk: ta.Optional[Token]) -> ta.Optional[YamlError]:
    if tk is None or tk.line_comment is None:
        return None
    comment = ast.comment_group([tk.line_comment])
    comment.set_path(ctx.path)
    if (err := node.set_comment(comment)) is not None:
        return err
    return None


def set_head_comment(cm: ta.Optional[ast.CommentGroupNode], value: ast.Node) -> ta.Optional[YamlError]:
    if cm is None:
        return None
    n = value
    if isinstance(n, ast.MappingNode):
        if len(n.values) != 0 and value.get_comment() is None:
            cm.set_path(n.values[0].get_path())
            return n.values[0].set_comment(cm)
    elif isinstance(n, ast.MappingValueNode):
        cm.set_path(n.get_path())
        return n.set_comment(cm)
    cm.set_path(value.get_path())
    return value.set_comment(cm)


##


ParseMode: ta.TypeAlias = int
PARSE_COMMENTS = ParseMode(1)  # parse comments and add them to AST


# ParseBytes parse from byte slice, and returns ast.File
def parse_str(
        s: str,
        mode: ParseMode = ParseMode(0),
        *opts: Option,
) -> YamlErrorOr[ast.File]:
    tokens = scanning.tokenize(s)
    f = parse(tokens, mode, *opts)
    if isinstance(f, YamlError):
        return f
    return f


# Parse parse from token instances, and returns ast.File
def parse(
        tokens: tokens_.Tokens,
        mode: ParseMode = ParseMode(0),
        *opts: Option,
) -> YamlErrorOr[ast.File]:
    if (tk := tokens.invalid_token()) is not None:
        return err_syntax(tk.error, tk)
    p = Parser.new_parser(tokens, mode, opts)
    if isinstance(p, YamlError):
        return p
    f = p.parse(Context.new_context())
    if isinstance(f, YamlError):
        return f
    return f


#


YAMLVersion: ta.TypeAlias = str

YAML10 = YAMLVersion('1.0')
YAML11 = YAMLVersion('1.1')
YAML12 = YAMLVersion('1.2')
YAML13 = YAMLVersion('1.3')

YAML_VERSION_MAP: ta.Mapping[str, YAMLVersion] = {
    '1.0': YAML10,
    '1.1': YAML11,
    '1.2': YAML12,
    '1.3': YAML13,
}


#

@dc.dataclass(kw_only=True)
class Parser:
    tokens: ta.List[Token]
    path_map: ta.Dict[str, ast.Node]
    yaml_version: YAMLVersion = YAMLVersion('')
    allow_duplicate_map_key: bool = False
    secondary_tag_directive: ta.Optional[ast.DirectiveNode] = None

    @staticmethod
    def new_parser(
            tokens: tokens_.Tokens,
            mode: ParseMode,
            opts: ta.Iterable[Option],
    ) -> YamlErrorOr['Parser']:
        filtered_tokens: ta.List[tokens_.Token] = []
        if mode & PARSE_COMMENTS != 0:
            filtered_tokens = tokens
        else:
            for tk in tokens:
                if tk.type == tokens_.Type.COMMENT:
                    continue
                # keep prev/next reference between tokens containing comments
                # https://github.com/goccy/go-yaml/issues/254
                filtered_tokens.append(tk)
        tks = create_grouped_tokens(tokens_.Tokens(filtered_tokens))
        if isinstance(tks, YamlError):
            return tks
        p = Parser(
            tokens=tks,
            path_map={},
        )
        for opt in opts:
            opt(p)
        return p

    def parse(self, ctx: Context) -> YamlErrorOr[ast.File]:
        file = ast.File(docs=[])
        for token in self.tokens:
            doc = self.parse_document(ctx, token.group)
            if isinstance(doc, YamlError):
                return doc
            file.docs.append(doc)
        return file

    def parse_document(
            self,
            ctx: Context,
            doc_group: TokenGroup,
    ) -> YamlErrorOr[ast.DocumentNode]:
        if len(doc_group.tokens) == 0:
            return ast.document(doc_group.raw_token(), None)

        self.path_map: ta.Dict[str, ast.Node] = {}

        tokens = doc_group.tokens
        start: ta.Optional[tokens_.Token] = None
        end: ta.Optional[tokens_.Token] = None
        if doc_group.first().type() == tokens_.Type.DOCUMENT_HEADER:
            start = doc_group.first().raw_token()
            tokens = tokens[1:]

        clear_yaml_version = False
        try:
            if doc_group.last().type() == tokens_.Type.DOCUMENT_END:
                end = doc_group.last().raw_token()
                tokens = tokens[:len(tokens) - 1]
                # clear yaml version value if DocumentEnd token (...) is specified.
                clear_yaml_version = True

            if len(tokens) == 0:
                return ast.document(doc_group.raw_token(), None)

            body = self.parse_document_body(ctx.with_group(TokenGroup(
                type=TokenGroupType.DOCUMENT_BODY,
                tokens=tokens,
            )))
            if isinstance(body, YamlError):
                return body
            node = ast.document(start, body)
            node.end = end
            return node

        finally:
            if clear_yaml_version:
                self.yaml_version = ''

    def parse_document_body(self, ctx: Context) -> YamlErrorOr[ast.Node]:
        node = self.parse_token(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        if ctx.next():
            return err_syntax('value is not allowed in this context', ctx.current_token().raw_token())
        return node

    def parse_token(self, ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ast.Node]:
        if Token.group_type(tk) in (
                TokenGroupType.MAP_KEY,
                TokenGroupType.MAP_KEY_VALUE,
        ):
            return self.parse_map(ctx)
        elif Token.group_type(tk) == TokenGroupType.DIRECTIVE:
            node = self.parse_directive(ctx.with_group(tk.group), tk.group)
            if isinstance(node, YamlError):
                return node
            ctx.go_next()
            return node
        elif Token.group_type(tk) == TokenGroupType.DIRECTIVE_NAME:
            node = self.parse_directive_name(ctx.with_group(tk.group))
            if isinstance(node, YamlError):
                return node
            ctx.go_next()
            return node
        elif Token.group_type(tk) == TokenGroupType.ANCHOR:
            node = self.parse_anchor(ctx.with_group(tk.group), tk.group)
            if isinstance(node, YamlError):
                return node
            ctx.go_next()
            return node
        elif Token.group_type(tk) == TokenGroupType.ANCHOR_NAME:
            anchor = self.parse_anchor_name(ctx.with_group(tk.group))
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            if ctx.is_token_not_found():
                return err_syntax('could not find anchor value', tk.raw_token())
            value = self.parse_token(ctx, ctx.current_token())
            if isinstance(value, YamlError):
                return value
            if isinstance(value, ast.AnchorNode):
                return err_syntax('anchors cannot be used consecutively', value.get_token())
            anchor.value = value
            return anchor
        elif Token.group_type(tk) == TokenGroupType.ALIAS:
            node = self.parse_alias(ctx.with_group(tk.group))
            if isinstance(node, YamlError):
                return node
            ctx.go_next()
            return node
        elif Token.group_type(tk) in (
                TokenGroupType.LITERAL,
                TokenGroupType.FOLDED,
        ):
            node = self.parse_literal(ctx.with_group(tk.group))
            if isinstance(node, YamlError):
                return node
            ctx.go_next()
            return node
        elif Token.group_type(tk) == TokenGroupType.SCALAR_TAG:
            node = self.parse_tag(ctx.with_group(tk.group))
            if isinstance(node, YamlError):
                return node
            ctx.go_next()
            return node
        if Token.type(tk) == tokens_.Type.COMMENT:
            return self.parse_comment(ctx)
        elif Token.type(tk) == tokens_.Type.TAG:
            return self.parse_tag(ctx)
        elif Token.type(tk) == tokens_.Type.MAPPING_START:
            return self.parse_flow_map(ctx.with_flow(True))
        elif Token.type(tk) == tokens_.Type.SEQUENCE_START:
            return self.parse_flow_sequence(ctx.with_flow(True))
        elif Token.type(tk) == tokens_.Type.SEQUENCE_ENTRY:
            return self.parse_sequence(ctx)
        elif Token.type(tk) == tokens_.Type.SEQUENCE_END:
            # SequenceEndType is always validated in parse_flow_sequence.
            # Therefore, if this is found in other cases, it is treated as a syntax error.
            return err_syntax("could not find '[' character corresponding to ']'", tk.raw_token())
        elif Token.type(tk) == tokens_.Type.MAPPING_END:
            # MappingEndType is always validated in parse_flow_map.
            # Therefore, if this is found in other cases, it is treated as a syntax error.
            return err_syntax("could not find '{' character corresponding to '}'", tk.raw_token())
        elif Token.type(tk) == tokens_.Type.MAPPING_VALUE:
            return err_syntax('found an invalid key for this map', tk.raw_token())
        node = self.parse_scalar_value(ctx, tk)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()
        return node

    def parse_scalar_value(self, ctx: Context, tk: ta.Optional[Token]) -> YamlErrorOr[ta.Optional[ast.ScalarNode]]:
        tk = check.not_none(tk)
        if tk.group is not None:
            if tk.group_type() == TokenGroupType.ANCHOR:
                return self.parse_anchor(ctx.with_group(tk.group), tk.group)
            elif tk.group_type() == TokenGroupType.ANCHOR_NAME:
                anchor = self.parse_anchor_name(ctx.with_group(tk.group))
                if isinstance(anchor, YamlError):
                    return anchor
                ctx.go_next()
                if ctx.is_token_not_found():
                    return err_syntax('could not find anchor value', tk.raw_token())
                value = self.parse_token(ctx, ctx.current_token())
                if isinstance(value, YamlError):
                    return value
                if isinstance(value, ast.AnchorNode):
                    return err_syntax('anchors cannot be used consecutively', value.get_token())
                anchor.value = value
                return anchor
            elif tk.group_type() == TokenGroupType.ALIAS:
                return self.parse_alias(ctx.with_group(tk.group))
            elif tk.group_type() in (
                    TokenGroupType.LITERAL,
                    TokenGroupType.FOLDED,
            ):
                return self.parse_literal(ctx.with_group(tk.group))
            elif tk.group_type() == TokenGroupType.SCALAR_TAG:
                return self.parse_tag(ctx.with_group(tk.group))
            else:
                return err_syntax('unexpected scalar value', tk.raw_token())
        if tk.type() == tokens_.Type.MERGE_KEY:
            return new_merge_key_node(ctx, tk)
        if tk.type() in (tokens_.Type.NULL, tokens_.Type.IMPLICIT_NULL):
            return new_null_node(ctx, tk)
        if tk.type() == tokens_.Type.BOOL:
            return new_bool_node(ctx, tk)
        if tk.type() in (
                tokens_.Type.INTEGER,
                tokens_.Type.BINARY_INTEGER,
                tokens_.Type.OCTET_INTEGER,
                tokens_.Type.HEX_INTEGER,
        ):
            return new_integer_node(ctx, tk)
        if tk.type() == tokens_.Type.FLOAT:
            return new_float_node(ctx, tk)
        if tk.type() == tokens_.Type.INFINITY:
            return new_infinity_node(ctx, tk)
        if tk.type() == tokens_.Type.NAN:
            return new_nan_node(ctx, tk)
        if tk.type() in (
                tokens_.Type.STRING,
                tokens_.Type.SINGLE_QUOTE,
                tokens_.Type.DOUBLE_QUOTE,
        ):
            return new_string_node(ctx, tk)
        if tk.type() == tokens_.Type.TAG:
            # this case applies when it is a scalar tag and its value does not exist.
            # Examples of cases where the value does not exist include cases like `key: !!str,` or `!!str : value`.
            return self.parse_scalar_tag(ctx)
        return err_syntax('unexpected scalar value type', tk.raw_token())

    def parse_flow_map(self, ctx: Context) -> YamlErrorOr[ast.MappingNode]:
        node = new_mapping_node(ctx, ctx.current_token(), True)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip MappingStart token

        is_first = True
        while ctx.next():
            tk = ctx.current_token()
            if tk.type() == tokens_.Type.MAPPING_END:
                node.end = tk.raw_token()
                break

            entry_tk: ta.Optional[Token] = None
            if tk.type() == tokens_.Type.COLLECT_ENTRY:
                entry_tk = tk
                ctx.go_next()
            elif not is_first:
                return err_syntax("',' or '}' must be specified", tk.raw_token())

            if (tk := ctx.current_token()).type() == tokens_.Type.MAPPING_END:
                # this case is here: "{ elem, }".
                # In this case, ignore the last element and break mapping parsing.
                node.end = tk.raw_token()
                break

            map_key_tk = ctx.current_token()
            if map_key_tk.group_type() == TokenGroupType.MAP_KEY_VALUE:
                value = self.parse_map_key_value(ctx.with_group(map_key_tk.group), map_key_tk.group, entry_tk)
                if isinstance(value, YamlError):
                    return value
                node.values.append(value)
                ctx.go_next()
            elif map_key_tk.group_type() == TokenGroupType.MAP_KEY:
                key = self.parse_map_key(ctx.with_group(map_key_tk.group), map_key_tk.group)
                if isinstance(key, YamlError):
                    return key
                ctx = ctx.with_child(self.map_key_text(key))
                colon_tk = map_key_tk.group.last()
                if self.is_flow_map_delim(ctx.next_token()):
                    value = new_null_node(ctx, ctx.insert_null_token(colon_tk))
                    if isinstance(value, YamlError):
                        return value
                    map_value = new_mapping_value_node(ctx, colon_tk, entry_tk, key, value)
                    if isinstance(map_value, YamlError):
                        return map_value
                    node.values.append(map_value)
                    ctx.go_next()
                else:
                    ctx.go_next()
                    if ctx.is_token_not_found():
                        return err_syntax('could not find map value', colon_tk.raw_token())
                    value = self.parse_token(ctx, ctx.current_token())
                    if isinstance(value, YamlError):
                        return value
                    map_value = new_mapping_value_node(ctx, colon_tk, entry_tk, key, value)
                    if isinstance(map_value, YamlError):
                        return map_value
                    node.values.append(map_value)
            else:
                if not self.is_flow_map_delim(ctx.next_token()):
                    err_tk = map_key_tk
                    if err_tk is None:
                        err_tk = tk
                    return err_syntax('could not find flow map content', err_tk.raw_token())
                key = self.parse_scalar_value(ctx, map_key_tk)
                if isinstance(key, YamlError):
                    return key
                value = new_null_node(ctx, ctx.insert_null_token(map_key_tk))
                if isinstance(value, YamlError):
                    return value
                map_value = new_mapping_value_node(ctx, map_key_tk, entry_tk, key, value)
                if isinstance(map_value, YamlError):
                    return map_value
                node.values.append(map_value)
                ctx.go_next()
            is_first = False
        if node.end is None:
            return err_syntax("could not find flow mapping end token '}'", node.start)
        ctx.go_next()  # skip mapping end token.
        return node

    def is_flow_map_delim(self, tk: Token) -> bool:
        return tk.type() == tokens_.Type.MAPPING_END or tk.type() == tokens_.Type.COLLECT_ENTRY

    def parse_map(self, ctx: Context) -> YamlErrorOr[ast.MappingNode]:
        key_tk = ctx.current_token()
        if key_tk.group is None:
            return err_syntax('unexpected map key', key_tk.raw_token())
        key_value_node: ast.MappingValueNode
        if key_tk.group_type() == TokenGroupType.MAP_KEY_VALUE:
            node = self.parse_map_key_value(ctx.with_group(key_tk.group), key_tk.group, None)
            if isinstance(node, YamlError):
                return node
            key_value_node = node
            ctx.go_next()
            if (err := self.validate_map_key_value_next_token(ctx, key_tk, ctx.current_token())) is not None:
                return err
        else:
            key = self.parse_map_key(ctx.with_group(key_tk.group), key_tk.group)
            if isinstance(key, YamlError):
                return key
            ctx.go_next()

            value_tk = ctx.current_token()
            if Token.line(key_tk) == Token.line(value_tk) and Token.type(value_tk) == tokens_.Type.SEQUENCE_ENTRY:
                return err_syntax('block sequence entries are not allowed in this context', value_tk.raw_token())
            ctx = ctx.with_child(self.map_key_text(key))
            value = self.parse_map_value(ctx, key, key_tk.group.last())
            if isinstance(value, YamlError):
                return value
            node = new_mapping_value_node(ctx, key_tk.group.last(), None, key, value)
            if isinstance(node, YamlError):
                return node
            key_value_node = node
        map_node = new_mapping_node(ctx, Token(token=key_value_node.get_token()), False, key_value_node)
        if isinstance(map_node, YamlError):
            return map_node
        tk: Token
        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        else:
            tk = ctx.current_token()
        while Token.column(tk) == Token.column(key_tk):
            typ = tk.type()
            if ctx.is_flow and typ == tokens_.Type.SEQUENCE_END:
                # [
                # key: value
                # ] <=
                break
            if not self.is_map_token(tk):
                return err_syntax('non-map value is specified', tk.raw_token())
            cm = self.parse_head_comment(ctx)
            if typ == tokens_.Type.MAPPING_END:
                # a: {
                #  b: c
                # } <=
                ctx.go_next()
                break
            node = self.parse_map(ctx)
            if isinstance(node, YamlError):
                return node
            if len(node.values) != 0:
                if (err := set_head_comment(cm, node.values[0])) is not None:
                    return err
            map_node.values.extend(node.values)
            if node.foot_comment is not None:
                map_node.values[len(map_node.values) - 1].foot_comment = node.foot_comment
            tk = ctx.current_token()
        if ctx.is_comment():
            if key_tk.column() <= ctx.current_token().column():
                # If the comment is in the same or deeper column as the last element column in map value,
                # treat it as a footer comment for the last element.
                if len(map_node.values) == 1:
                    map_node.values[0].foot_comment = self.parse_foot_comment(ctx, key_tk.column())
                    map_node.values[0].foot_comment.set_path(map_node.values[0].key.get_path())
                else:
                    map_node.foot_comment = self.parse_foot_comment(ctx, key_tk.column())
                    map_node.foot_comment.set_path(map_node.get_path())
        return map_node

    def validate_map_key_value_next_token(self, ctx: Context, key_tk, tk: Token) -> ta.Optional[YamlError]:
        if tk is None:
            return None
        if tk.column() <= key_tk.column():
            return None
        if ctx.is_comment():
            return None
        if ctx.is_flow and (tk.type() == tokens_.Type.COLLECT_ENTRY or tk.type() == tokens_.Type.SEQUENCE_END):
            return None
        # a: b
        #  c <= this token is invalid.
        return err_syntax('value is not allowed in this context. map key-value is pre-defined', tk.raw_token())

    def is_map_token(self, tk: Token) -> bool:
        if tk.group is None:
            return tk.type() == tokens_.Type.MAPPING_START or tk.type() == tokens_.Type.MAPPING_END
        g = tk.group
        return g.type == TokenGroupType.MAP_KEY or g.type == TokenGroupType.MAP_KEY_VALUE

    def parse_map_key_value( self,
            ctx: Context,
            g: TokenGroup,
            entry_tk: ta.Optional[Token],
    ) -> YamlErrorOr[ast.MappingValueNode]:
        if g.type != TokenGroupType.MAP_KEY_VALUE:
            return err_syntax('unexpected map key-value pair', g.raw_token())
        if g.first().group is None:
            return err_syntax('unexpected map key', g.raw_token())
        key_group = g.first().group
        key = self.parse_map_key(ctx.with_group(key_group), key_group)
        if isinstance(key, YamlError):
            return key

        c = ctx.with_child(self.map_key_text(key))
        value = self.parse_token(c, g.last())
        if isinstance(value, YamlError):
            return value
        return new_mapping_value_node(c, key_group.last(), entry_tk, key, value)

    def parse_map_key(self, ctx: Context, g: TokenGroup) -> YamlErrorOr[ast.MapKeyNode]:
        if g.type != TokenGroupType.MAP_KEY:
            return err_syntax('unexpected map key', g.raw_token())
        if Token.type(g.first()) == tokens_.Type.MAPPING_KEY:
            map_key_tk = check.not_none(g.first())
            if map_key_tk.group is not None:
                ctx = ctx.with_group(map_key_tk.group)
            key0 = new_mapping_key_node(ctx, map_key_tk)
            if isinstance(key0, YamlError):
                return key0
            ctx.go_next()  # skip mapping key token
            if ctx.is_token_not_found():
                return err_syntax('could not find value for mapping key', Token.raw_token(map_key_tk))

            scalar0 = self.parse_scalar_value(ctx, ctx.current_token())
            if isinstance(scalar0, YamlError):
                return scalar0
            key0.value = scalar0
            key_text = self.map_key_text(scalar0)
            key_path = ctx.with_child(key_text).path
            key0.set_path(key_path)
            if (err := self.validate_map_key(
                    ctx,
                    check.not_none(key0.get_token()),
                    key_path,
                    check.not_none(g.last()),
            )) is not None:
                return err
            self.path_map[key_path] = key0
            return key0
        if Token.type(g.last()) != tokens_.Type.MAPPING_VALUE:
            return err_syntax("expected map key-value delimiter ':'", Token.raw_token(g.last()))

        scalar1 = self.parse_scalar_value(ctx, g.first())
        if isinstance(scalar1, YamlError):
            return scalar1
        if not isinstance(scalar1, ast.MapKeyNode):
            return err_syntax('cannot take map-key node', check.not_none(scalar1).get_token())
        key1: ast.MapKeyNode = ta.cast(ast.MapKeyNode, scalar1)
        key_text = self.map_key_text(key1)
        key_path = ctx.with_child(key_text).path
        key1.set_path(key_path)
        if (err := self.validate_map_key(
                ctx,
                check.not_none(key1.get_token()),
                key_path,
                check.not_none(g.last()),
        )) is not None:
            return err
        self.path_map[key_path] = key1
        return key1

    def validate_map_key(
            self,
            ctx: Context,
            tk: tokens_.Token,
            key_path: str,
            colon_tk: Token,
    ) -> ta.Optional[YamlError]:
        if not self.allow_duplicate_map_key:
            if (n := self.path_map.get(key_path)) is not None:
                pos = check.not_none(n.get_token()).position
                return err_syntax(
                    f'mapping key {tk.value!r} already defined at [{pos.line:d}:{pos.column:d}]',
                    tk,
                )
        origin = self.remove_left_white_space(tk.origin)
        if ctx.is_flow:
            if tk.type == tokens_.Type.STRING:
                origin = self.remove_right_white_space(origin)
                if tk.position.line + self.new_line_character_num(origin) != colon_tk.line():
                    return err_syntax('map key definition includes an implicit line break', tk)
            return None
        if (
                tk.type != tokens_.Type.STRING and
                tk.type != tokens_.Type.SINGLE_QUOTE and
                tk.type != tokens_.Type.DOUBLE_QUOTE
        ):
            return None
        if self.exists_new_line_character(origin):
            return err_syntax('unexpected key name', tk)
        return None

    def remove_left_white_space(self, src: str) -> str:
        # CR or LF or CRLF
        return src.lstrip(' \r\n')

    def remove_right_white_space(self, src: str) -> str:
        # CR or LF or CRLF
        return src.rstrip(' \r\n')

    def exists_new_line_character(self, src: str) -> bool:
        return self.new_line_character_num(src) > 0

    def new_line_character_num(self, src: str) -> int:
        num = 0
        i = -1
        while True:
            i += 1
            if not (i < len(src)):
                break
            if src[i] == '\r':
                if len(src) > i + 1 and src[i + 1] == '\n':
                    i += 1
                num += 1
            elif src[i] == '\n':
                num += 1
        return num

    def map_key_text(self, n: ta.Optional[ast.Node]) -> str:
        if n is None:
            return ''
        nn = n
        if isinstance(nn, ast.MappingKeyNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, ast.TagNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, ast.AnchorNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, ast.AliasNode):
            return ''
        return check.not_none(n.get_token()).value

    def parse_map_value(
            self,
            ctx: Context,
            key: ast.MapKeyNode,
            colon_tk: Token,
    ) -> YamlErrorOr[ast.Node]:
        tk = ctx.current_token()
        if tk is None:
            return new_null_node(ctx, ctx.add_null_value_token(colon_tk))

        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        key_col = check.not_none(key.get_token()).position.column
        key_line = check.not_none(key.get_token()).position.line

        if (
                Token.column(tk) != key_col and
                Token.line(tk) == key_line and
                (Token.group_type(tk) == TokenGroupType.MAP_KEY or Token.group_type(tk) == TokenGroupType.MAP_KEY_VALUE)
        ):
            # a: b:
            #    ^
            #
            # a: b: c
            #    ^
            return err_syntax('mapping value is not allowed in this context', Token.raw_token(tk))

        if Token.column(tk) == key_col and self.is_map_token(check.not_none(tk)):
            # in this case,
            # ----
            # key: <value does not defined>
            # next
            return new_null_node(ctx, ctx.insert_null_token(colon_tk))

        if (
                Token.line(tk) == key_line and
                Token.group_type(tk) == TokenGroupType.ANCHOR_NAME and
                Token.column(ctx.next_token()) == key_col and
                self.is_map_token(check.not_none(ctx.next_token()))
        ):
            # in this case,
            # ----
            # key: &anchor
            # next
            group = TokenGroup(
                type=TokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        if Token.column(tk) <= key_col and Token.group_type(tk) == TokenGroupType.ANCHOR_NAME:
            # key: <value does not defined>
            # &anchor
            return err_syntax('anchor is not allowed in this context', Token.raw_token(tk))
        if Token.column(tk) <= key_col and Token.type(tk) == tokens_.Type.TAG:
            # key: <value does not defined>
            # !!tag
            return err_syntax('tag is not allowed in this context', Token.raw_token(tk))

        if Token.column(tk) < key_col:
            # in this case,
            # ----
            #   key: <value does not defined>
            # next
            return new_null_node(ctx, ctx.insert_null_token(colon_tk))

        if (
                Token.line(tk) == key_line and
                Token.group_type(tk) == TokenGroupType.ANCHOR_NAME and
                Token.column(ctx.next_token()) < key_col
        ):
            # in this case,
            # ----
            #   key: &anchor
            # next
            group = TokenGroup(
                type=TokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        value = self.parse_token(ctx, ctx.current_token())
        if isinstance(value, YamlError):
            return value
        if (err := self.validate_anchor_value_in_map_or_seq(value, key_col)) is not None:
            return err
        return value

    def validate_anchor_value_in_map_or_seq(self, value: ast.Node, col: int) -> ta.Optional[YamlError]:
        if not isinstance(value, ast.AnchorNode):
            return None
        anchor: ast.AnchorNode = value
        if not isinstance(anchor.value, ast.TagNode):
            return None
        tag: ast.TagNode = anchor.value
        anchor_tk = anchor.get_token()
        tag_tk = tag.get_token()

        if anchor_tk.position.line == tag_tk.position.line:
            # key:
            #   &anchor !!tag
            #
            # - &anchor !!tag
            return None

        if tag_tk.position.column <= col:
            # key: &anchor
            # !!tag
            #
            # - &anchor
            # !!tag
            return err_syntax('tag is not allowed in this context', tag_tk)
        return None

    def parse_anchor(self, ctx: Context, g: TokenGroup) -> YamlErrorOr[ast.AnchorNode]:
        anchor_name_group = check.not_none(check.not_none(g.first()).group)
        anchor = self.parse_anchor_name(ctx.with_group(anchor_name_group))
        if isinstance(anchor, YamlError):
            return anchor
        ctx.go_next()
        if ctx.is_token_not_found():
            return err_syntax('could not find anchor value', anchor.get_token())

        value = self.parse_token(ctx, ctx.current_token())
        if isinstance(value, YamlError):
            return value
        if isinstance(value, ast.AnchorNode):
            return err_syntax('anchors cannot be used consecutively', value.get_token())
        anchor.value = value
        return anchor

    def parse_anchor_name(self, ctx: Context) -> YamlErrorOr[ast.AnchorNode]:
        anchor = new_anchor_node(ctx, ctx.current_token())
        if isinstance(anchor, YamlError):
            return anchor
        ctx.go_next()
        if ctx.is_token_not_found():
            return err_syntax('could not find anchor value', anchor.get_token())

        anchor_name = self.parse_scalar_value(ctx, ctx.current_token())
        if isinstance(anchor_name, YamlError):
            return anchor_name
        if anchor_name is None:
            return err_syntax(
                'unexpected anchor. anchor name is not scalar value',
                Token.raw_token(ctx.current_token()),
            )
        anchor.name = anchor_name
        return anchor

    def parse_alias(self, ctx: Context) -> YamlErrorOr[ast.AliasNode]:
        alias = new_alias_node(ctx, ctx.current_token())
        if isinstance(alias, YamlError):
            return alias
        ctx.go_next()
        if ctx.is_token_not_found():
            return err_syntax('could not find alias value', alias.get_token())

        alias_name = self.parse_scalar_value(ctx, ctx.current_token())
        if isinstance(alias_name, YamlError):
            return alias_name
        if alias_name is None:
            return err_syntax(
                'unexpected alias. alias name is not scalar value',
                Token.raw_token(ctx.current_token()),
            )
        alias.value = alias_name
        return alias

    def parse_literal(self, ctx: Context) -> YamlErrorOr[ast.LiteralNode]:
        node = new_literal_node(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip literal/folded token

        tk = ctx.current_token()
        if tk is None:
            value0 = new_string_node(ctx, Token(token=tokens.new('', '', node.start.position)))
            if isinstance(value0, YamlError):
                return value0
            node.value = value0
            return node
        value1 = self.parse_token(ctx, tk)
        if isinstance(value1, YamlError):
            return value1
        if not isinstance(s := value1, ast.StringNode):
            return err_syntax('unexpected token. required string token', value1.get_token())
        node.value = s
        return node

    def parse_scalar_tag(self, ctx: Context) -> YamlErrorOr[ast.TagNode]:
        tag = self.parse_tag(ctx)
        if isinstance(tag, YamlError):
            return tag
        if tag.value is None:
            return err_syntax('specified not scalar tag', tag.get_token())
        if not isinstance(tag.value, ast.ScalarNode):
            return err_syntax('specified not scalar tag', tag.get_token())
        return tag

    def parse_tag(self, ctx: Context) -> YamlErrorOr[ast.TagNode]:
        tag_tk = ctx.current_token()
        tag_raw_tk = Token.raw_token(tag_tk)
        node = new_tag_node(ctx, tag_tk)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()

        comment = self.parse_head_comment(ctx)

        tag_value: ast.Node
        if self.secondary_tag_directive is not None:
            value0 = new_string_node(ctx, ctx.current_token())
            if isinstance(value0, YamlError):
                return value0
            tag_value = value0
            node.directive = self.secondary_tag_directive
        else:
            value1 = self.parse_tag_value(ctx, check.not_none(tag_raw_tk), ctx.current_token())
            if isinstance(value1, YamlError):
                return value1
            tag_value = check.not_none(value1)
        if (err := set_head_comment(comment, tag_value)) is not None:
            return err
        node.value = tag_value
        return node

    def parse_tag_value(
            self,
            ctx: Context,
            tag_raw_tk: tokens_.Token,
            tk: ta.Optional[Token],
    ) -> YamlErrorOr[ta.Optional[ast.Node]]:
        if tk is None:
            return new_null_node(ctx, ctx.create_implicit_null_token(Token(token=tag_raw_tk)))
        if tag_raw_tk.value in (
                tokens_.ReservedTagKeywords.MAPPING,
                tokens_.ReservedTagKeywords.SET,
        ):
            if not self.is_map_token(tk):
                return err_syntax('could not find map', tk.raw_token())
            if tk.type() == tokens_.Type.MAPPING_START:
                return self.parse_flow_map(ctx.with_flow(True))
            return self.parse_map(ctx)
        elif tag_raw_tk.value in (
                tokens_.ReservedTagKeywords.INTEGER,
                tokens_.ReservedTagKeywords.FLOAT,
                tokens_.ReservedTagKeywords.STRING,
                tokens_.ReservedTagKeywords.BINARY,
                tokens_.ReservedTagKeywords.TIMESTAMP,
                tokens_.ReservedTagKeywords.BOOLEAN,
                tokens_.ReservedTagKeywords.NULL,
        ):
            if tk.group_type() == TokenGroupType.LITERAL or tk.group_type() == TokenGroupType.FOLDED:
                return self.parse_literal(ctx.with_group(check.not_none(tk.group)))
            elif tk.type() == tokens_.Type.COLLECT_ENTRY or tk.type() == tokens_.Type.MAPPING_VALUE:
                return new_tag_default_scalar_value_node(ctx, tag_raw_tk)
            scalar = self.parse_scalar_value(ctx, tk)
            if isinstance(scalar, YamlError):
                return scalar
            ctx.go_next()
            return scalar
        elif tag_raw_tk.value in (
                tokens_.ReservedTagKeywords.SEQUENCE,
                tokens_.ReservedTagKeywords.ORDERED_MAP,
        ):
            if tk.type() == tokens_.Type.SEQUENCE_START:
                return self.parse_flow_sequence(ctx.with_flow(True))
            return self.parse_sequence(ctx)
        return self.parse_token(ctx, tk)

    def parse_flow_sequence(self, ctx: Context) -> YamlErrorOr[ast.SequenceNode]:
        node = new_sequence_node(ctx, ctx.current_token(), True)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip SequenceStart token

        is_first = True
        while ctx.next():
            tk = ctx.current_token()
            if Token.type(tk) == tokens_.Type.SEQUENCE_END:
                node.end = Token.raw_token(tk)
                break

            entry_tk: ta.Optional[Token] = None
            if Token.type(tk) == tokens_.Type.COLLECT_ENTRY:
                if is_first:
                    return err_syntax("expected sequence element, but found ','", Token.raw_token(tk))
                entry_tk = tk
                ctx.go_next()
            elif not is_first:
                return err_syntax("',' or ']' must be specified", Token.raw_token(tk))

            if Token.type(tk := ctx.current_token()) == tokens_.Type.SEQUENCE_END:
                # this case is here: "[ elem, ]".
                # In this case, ignore the last element and break sequence parsing.
                node.end = Token.raw_token(tk)
                break

            if ctx.is_token_not_found():
                break

            ctx = ctx.with_index(len(node.values))
            value = self.parse_token(ctx, ctx.current_token())
            if isinstance(value, YamlError):
                return value
            node.values.append(value)
            seq_entry = ast.sequence_entry(
                entry_tk.raw_token() if entry_tk is not None else None,
                value,
                None,
            )
            if (err := set_line_comment(ctx, seq_entry, entry_tk)) is not None:
                return err
            seq_entry.set_path(ctx.path)
            node.entries.append(seq_entry)

            is_first = False
        if node.end is None:
            return err_syntax("sequence end token ']' not found", node.start)
        ctx.go_next()  # skip sequence end token.
        return node

    def parse_sequence(self, ctx: Context) -> YamlErrorOr[ast.SequenceNode]:
        seq_tk = ctx.current_token()
        seq_node = new_sequence_node(ctx, seq_tk, False)
        if isinstance(seq_node, YamlError):
            return seq_node

        tk = seq_tk
        while Token.type(tk) == tokens_.Type.SEQUENCE_ENTRY and Token.column(tk) == Token.column(seq_tk):
            head_comment = self.parse_head_comment(ctx)
            ctx.go_next()  # skip sequence entry token

            ctx = ctx.with_index(len(seq_node.values))
            value = self.parse_sequence_value(ctx, check.not_none(seq_tk))
            if isinstance(value, YamlError):
                return value
            seq_entry = ast.sequence_entry(Token.raw_token(seq_tk), value, head_comment)
            if (err := set_line_comment(ctx, seq_entry, seq_tk)) is not None:
                return err
            seq_entry.set_path(ctx.path)
            seq_node.value_head_comments.append(head_comment)
            seq_node.values.append(value)
            seq_node.entries.append(seq_entry)

            if ctx.is_comment():
                tk = ctx.next_not_comment_token()
            else:
                tk = ctx.current_token()
        if ctx.is_comment():
            if Token.column(seq_tk) <= Token.column(ctx.current_token()):
                # If the comment is in the same or deeper column as the last element column in sequence value,
                # treat it as a footer comment for the last element.
                seq_node.foot_comment = self.parse_foot_comment(ctx, Token.column(seq_tk))
                if len(seq_node.values) != 0:
                    check.not_none(seq_node.foot_comment).set_path(seq_node.values[len(seq_node.values) - 1].get_path())
        return seq_node

    def parse_sequence_value(self, ctx: Context, seq_tk: Token) -> YamlErrorOr[ast.Node]:
        tk = ctx.current_token()
        if tk is None:
            return new_null_node(ctx, ctx.add_null_value_token(seq_tk))

        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        seq_col = seq_tk.column()
        seq_line = seq_tk.line()

        if Token.column(tk) == seq_col and Token.type(tk) == tokens_.Type.SEQUENCE_ENTRY:
            # in this case,
            # ----
            # - <value does not defined>
            # -
            return new_null_node(ctx, ctx.insert_null_token(seq_tk))

        if (
                Token.line(tk) == seq_line and
                Token.group_type(tk) == TokenGroupType.ANCHOR_NAME and
                Token.column(ctx.next_token()) == seq_col and
                Token.type(ctx.next_token()) == tokens_.Type.SEQUENCE_ENTRY
        ):
            # in this case,
            # ----
            # - &anchor
            # -
            group = TokenGroup(
                type=TokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        if Token.column(tk) <= seq_col and Token.group_type(tk) == TokenGroupType.ANCHOR_NAME:
            # - <value does not defined>
            # &anchor
            return err_syntax('anchor is not allowed in this sequence context', Token.raw_token(tk))
        if Token.column(tk) <= seq_col and Token.type(tk) == tokens_.Type.TAG:
            # - <value does not defined>
            # !!tag
            return err_syntax('tag is not allowed in this sequence context', Token.raw_token(tk))

        if Token.column(tk) < seq_col:
            # in this case,
            # ----
            #   - <value does not defined>
            # next
            return new_null_node(ctx, ctx.insert_null_token(seq_tk))

        if (
                Token.line(tk) == seq_line and
                Token.group_type(tk) == TokenGroupType.ANCHOR_NAME and
                Token.column(ctx.next_token()) < seq_col
        ):
            # in this case,
            # ----
            #   - &anchor
            # next
            group = TokenGroup(
                type=TokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        value = self.parse_token(ctx, ctx.current_token())
        if isinstance(value, YamlError):
            return value
        if (err := self.validate_anchor_value_in_map_or_seq(value, seq_col)) is not None:
            return err
        return value

    def parse_directive(self, ctx: Context, g: TokenGroup) -> YamlErrorOr[ast.DirectiveNode]:
        directive_name_group = check.not_none(check.not_none(g.first()).group)
        directive = self.parse_directive_name(ctx.with_group(directive_name_group))
        if isinstance(directive, YamlError):
            return directive

        if directive.name == 'YAML':
            if len(g.tokens) != 2:
                return err_syntax('unexpected format YAML directive', Token.raw_token(g.first()))
            value_tk = g.tokens[1]
            value_raw_tk = check.not_none(value_tk.raw_token())
            value0 = value_raw_tk.value
            ver = YAML_VERSION_MAP.get(value0)
            if ver is None:
                return err_syntax(f'unknown YAML version {value0!r}', value_raw_tk)
            if self.yaml_version != '':
                return err_syntax('YAML version has already been specified', value_raw_tk)
            self.yaml_version = ver
            version_node = new_string_node(ctx, value_tk)
            if isinstance(version_node, YamlError):
                return version_node
            directive.values.append(version_node)
        elif directive.name == 'TAG':
            if len(g.tokens) != 3:
                return err_syntax('unexpected format TAG directive', Token.raw_token(g.first()))
            tag_key = new_string_node(ctx, g.tokens[1])
            if isinstance(tag_key, YamlError):
                return tag_key
            if tag_key.value == '!!':
                self.secondary_tag_directive = directive
            tag_value = new_string_node(ctx, g.tokens[2])
            if isinstance(tag_value, YamlError):
                return tag_value
            directive.values.extend([tag_key, tag_value])
        elif len(g.tokens) > 1:
            for tk in g.tokens[1:]:
                value1 = new_string_node(ctx, tk)
                if isinstance(value1, YamlError):
                    return value1
                directive.values.append(value1)
        return directive

    def parse_directive_name(self, ctx: Context) -> YamlErrorOr[ast.DirectiveNode]:
        directive = new_directive_node(ctx, ctx.current_token())
        if isinstance(directive, YamlError):
            return directive
        ctx.go_next()
        if ctx.is_token_not_found():
            return err_syntax('could not find directive value', directive.get_token())

        directive_name = self.parse_scalar_value(ctx, ctx.current_token())
        if isinstance(directive_name, YamlError):
            return directive_name
        if directive_name is None:
            return err_syntax(
                'unexpected directive. directive name is not scalar value',
                Token.raw_token(ctx.current_token()),
            )
        directive.name = directive_name
        return directive

    def parse_comment(self, ctx: Context) -> YamlErrorOr[ta.Optional[ast.Node]]:
        cm = self.parse_head_comment(ctx)
        if ctx.is_token_not_found():
            return cm
        node = self.parse_token(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        if (err := set_head_comment(cm, node)) is not None:
            return err
        return node

    def parse_head_comment(self, ctx: Context) -> ta.Optional[ast.CommentGroupNode]:
        tks: ta.List[ta.Optional[tokens_.Token]] = []
        while ctx.is_comment():
            tks.append(Token.raw_token(ctx.current_token()))
            ctx.go_next()
        if len(tks) == 0:
            return None
        return ast.comment_group(tks)

    def parse_foot_comment(self, ctx: Context, col: int) -> ta.Optional[ast.CommentGroupNode]:
        tks: ta.List[ta.Optional[tokens_.Token]] = []
        while ctx.is_comment() and col <= Token.column(ctx.current_token()):
            tks.append(Token.raw_token(ctx.current_token()))
            ctx.go_next()
        if len(tks) == 0:
            return None
        return ast.comment_group(tks)
