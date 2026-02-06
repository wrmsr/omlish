# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import copy
import dataclasses as dc
import enum
import typing as ta

from omlish.lite.check import check
from omlish.lite.dataclasses import dataclass_field_required

from . import ast
from .errors import YamlError
from .errors import YamlErrorOr
from .errors import yaml_error
from .scanning import yaml_tokenize
from .tokens import YamlReservedTagKeywords
from .tokens import YamlToken
from .tokens import YamlTokens
from .tokens import YamlTokenType
from .tokens import new_yaml_token


##


# context context at parsing
@dc.dataclass()
class YamlParsingContext:
    token_ref: ta.Optional['YamlParseTokenRef'] = None
    path: str = dc.field(default_factory=dataclass_field_required('path'))
    is_flow: bool = False

    def current_token(self) -> ta.Optional['YamlParseToken']:
        ref = check.not_none(self.token_ref)

        if ref.idx >= ref.size:
            return None

        return ref.tokens[ref.idx]

    def is_comment(self) -> bool:
        return YamlParseToken.type(self.current_token()) == YamlTokenType.COMMENT

    def next_token(self) -> ta.Optional['YamlParseToken']:
        ref = check.not_none(self.token_ref)

        if ref.idx + 1 >= ref.size:
            return None

        return ref.tokens[ref.idx + 1]

    def next_not_comment_token(self) -> ta.Optional['YamlParseToken']:
        ref = check.not_none(self.token_ref)

        for i in range(ref.idx + 1, ref.size):
            tk = ref.tokens[i]
            if tk.type() == YamlTokenType.COMMENT:
                continue
            return tk

        return None

    def is_token_not_found(self) -> bool:
        return self.current_token() is None

    def with_group(self, g: 'YamlParseTokenGroup') -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.token_ref = YamlParseTokenRef(
            tokens=g.tokens,
            size=len(g.tokens),
        )
        return ctx

    def with_child(self, path: str) -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.path = self.path + '.' + normalize_path(path)
        return ctx

    def with_index(self, idx: int) -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.path = self.path + '[' + str(idx) + ']'
        return ctx

    def with_flow(self, is_flow: bool) -> 'YamlParsingContext':
        ctx = copy.copy(self)
        ctx.is_flow = is_flow
        return ctx

    @staticmethod
    def new() -> 'YamlParsingContext':
        return YamlParsingContext(
            path='$',
        )

    def go_next(self) -> None:
        ref = check.not_none(self.token_ref)
        if ref.size <= ref.idx + 1:
            ref.idx = ref.size
        else:
            ref.idx += 1

    def next(self) -> bool:
        return check.not_none(self.token_ref).idx < check.not_none(self.token_ref).size

    def insert_null_token(self, tk: 'YamlParseToken') -> 'YamlParseToken':
        null_token = self.create_implicit_null_token(tk)
        self.insert_token(null_token)
        self.go_next()

        return null_token

    def add_null_value_token(self, tk: 'YamlParseToken') -> 'YamlParseToken':
        null_token = self.create_implicit_null_token(tk)
        raw_tk = null_token.raw_token()

        # add space for map or sequence value.
        check.not_none(raw_tk).position.column += 1

        self.add_token(null_token)
        self.go_next()

        return null_token

    def create_implicit_null_token(self, base: 'YamlParseToken') -> 'YamlParseToken':
        pos = copy.copy(check.not_none(base.raw_token()).position)
        pos.column += 1
        tk = new_yaml_token('null', ' null', pos)
        tk.type = YamlTokenType.IMPLICIT_NULL
        return YamlParseToken(token=tk)

    def insert_token(self, tk: 'YamlParseToken') -> None:
        ref = check.not_none(self.token_ref)
        idx = ref.idx
        if ref.size < idx:
            return

        if ref.size == idx:
            cur_token = ref.tokens[ref.size - 1]
            check.not_none(tk.raw_token()).next = cur_token.raw_token()
            check.not_none(cur_token.raw_token()).prev = tk.raw_token()

            ref.tokens.append(tk)
            ref.size = len(ref.tokens)
            return

        cur_token = ref.tokens[idx]
        check.not_none(tk.raw_token()).next = cur_token.raw_token()
        check.not_none(cur_token.raw_token()).prev = tk.raw_token()

        ref.tokens = [*ref.tokens[:idx + 1], *ref.tokens[idx:]]
        ref.tokens[idx] = tk
        ref.size = len(ref.tokens)

    def add_token(self, tk: 'YamlParseToken') -> None:
        ref = check.not_none(self.token_ref)
        last_tk = check.not_none(ref.tokens[ref.size - 1])
        if last_tk.group is not None:
            last_tk = check.not_none(last_tk.group.last())

        check.not_none(last_tk.raw_token()).next = tk.raw_token()
        check.not_none(tk.raw_token()).prev = last_tk.raw_token()

        ref.tokens.append(tk)
        ref.size = len(ref.tokens)


@dc.dataclass()
class YamlParseTokenRef:
    tokens: ta.List['YamlParseToken']
    size: int
    idx: int = 0


##


PATH_SPECIAL_CHARS = (
    '$',
    '*',
    '.',
    '[',
    ']',
)


def contains_path_special_char(path: str) -> bool:
    return any(char in path for char in PATH_SPECIAL_CHARS)


def normalize_path(path: str) -> str:
    if contains_path_special_char(path):
        return f"'{path}'"

    return path


##


# Option represents parser's option.
Option = ta.Callable[['YamlParser'], None]  # ta.TypeAlias  # omlish-amalg-typing-no-move


# AllowDuplicateMapKey allow the use of keys with the same name in the same map, but by default, this is not permitted.
def allow_duplicate_map_key() -> Option:
    def fn(p: 'YamlParser') -> None:
        p.allow_duplicate_map_key = True

    return fn


##


class YamlParseTokenGroupType(enum.Enum):
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


@dc.dataclass()
class YamlParseToken:
    token: ta.Optional[YamlToken] = None
    group: ta.Optional['YamlParseTokenGroup'] = None
    line_comment: ta.Optional[YamlToken] = None

    def raw_token(self: ta.Optional['YamlParseToken']) -> ta.Optional[YamlToken]:
        if self is None:
            return None
        if self.token is not None:
            return self.token
        return check.not_none(self.group).raw_token()

    def type(self: ta.Optional['YamlParseToken']) -> YamlTokenType:
        if self is None:
            return YamlTokenType.UNKNOWN
        if self.token is not None:
            return self.token.type
        return check.not_none(self.group).token_type()

    def group_type(self: ta.Optional['YamlParseToken']) -> YamlParseTokenGroupType:
        if self is None:
            return YamlParseTokenGroupType.NONE
        if self.token is not None:
            return YamlParseTokenGroupType.NONE
        return check.not_none(self.group).type

    def line(self: ta.Optional['YamlParseToken']) -> int:
        if self is None:
            return 0
        if self.token is not None:
            return self.token.position.line
        return check.not_none(self.group).line()

    def column(self: ta.Optional['YamlParseToken']) -> int:
        if self is None:
            return 0
        if self.token is not None:
            return self.token.position.column
        return check.not_none(self.group).column()

    def set_group_type(self, typ: YamlParseTokenGroupType) -> None:
        if self.group is None:
            return
        self.group.type = typ


##


@dc.dataclass()
class YamlParseTokenGroup:
    type: YamlParseTokenGroupType = YamlParseTokenGroupType.NONE
    tokens: ta.List[YamlParseToken] = dc.field(default_factory=dataclass_field_required('tokens'))

    def first(self) -> ta.Optional[YamlParseToken]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0]

    def last(self) -> ta.Optional[YamlParseToken]:
        if len(self.tokens) == 0:
            return None
        return self.tokens[len(self.tokens) - 1]

    def raw_token(self) -> ta.Optional[YamlToken]:
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

    def token_type(self) -> YamlTokenType:
        if len(self.tokens) == 0:
            return YamlTokenType.UNKNOWN
        return self.tokens[0].type()


def create_grouped_tokens(tokens: YamlTokens) -> YamlErrorOr[ta.List[YamlParseToken]]:
    tks = new_tokens(tokens)

    tks = create_line_comment_token_groups(tks)

    tks_ = create_literal_and_folded_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = create_anchor_and_alias_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = create_scalar_tag_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = create_anchor_with_scalar_tag_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = create_map_key_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks = create_map_key_value_token_groups(tks)

    tks_ = create_directive_token_groups(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    tks_ = create_document_tokens(tks)
    if isinstance(tks_, YamlError):
        return tks_
    tks = tks_

    return tks


def new_tokens(tks: YamlTokens) -> ta.List[YamlParseToken]:
    ret: ta.List[YamlParseToken] = []
    for tk in tks:
        ret.append(YamlParseToken(token=tk))
    return ret


def create_line_comment_token_groups(tokens: ta.List[YamlParseToken]) -> ta.List[YamlParseToken]:
    ret: ta.List[YamlParseToken] = []
    for i in range(len(tokens)):
        tk = tokens[i]
        if tk.type() == YamlTokenType.COMMENT:
            if i > 0 and tokens[i - 1].line() == tk.line():
                tokens[i - 1].line_comment = tk.raw_token()
            else:
                ret.append(tk)
        else:
            ret.append(tk)
    return ret


def create_literal_and_folded_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.LITERAL:
            tks: ta.List[YamlParseToken] = [tk]
            if i + 1 < len(tokens):
                tks.append(tokens[i + 1])
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.LITERAL,
                    tokens=tks,
                ),
            ))
            i += 1
        elif tk.type() == YamlTokenType.FOLDED:
            tks = [tk]
            if i + 1 < len(tokens):
                tks.append(tokens[i + 1])
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.FOLDED,
                    tokens=tks,
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def err_syntax(msg: str, tk: ta.Optional[YamlToken]) -> YamlError:
    return yaml_error(f'Syntax error: {msg}, {tk}')


def create_anchor_and_alias_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.ANCHOR:
            if i + 1 >= len(tokens):
                return err_syntax('undefined anchor name', tk.raw_token())
            if i + 2 >= len(tokens):
                return err_syntax('undefined anchor value', tk.raw_token())
            anchor_name = YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.ANCHOR_NAME,
                    tokens=[tk, tokens[i + 1]],
                ),
            )
            value_tk = tokens[i + 2]
            if tk.line() == value_tk.line() and value_tk.type() == YamlTokenType.SEQUENCE_ENTRY:
                return err_syntax(
                    'sequence entries are not allowed after anchor on the same line',
                    value_tk.raw_token(),
                )
            if tk.line() == value_tk.line() and is_scalar_type(value_tk):
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.ANCHOR,
                        tokens=[anchor_name, value_tk],
                    ),
                ))
                i += 1
            else:
                ret.append(anchor_name)
            i += 1
        elif tk.type() == YamlTokenType.ALIAS:
            if i + 1 == len(tokens):
                return err_syntax('undefined alias name', tk.raw_token())
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.ALIAS,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def create_scalar_tag_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() != YamlTokenType.TAG:
            ret.append(tk)
            continue
        tag = check.not_none(tk.raw_token())
        if tag.value.startswith('!!'):
            # secondary tag.
            if tag.value in (
                    YamlReservedTagKeywords.INTEGER,
                    YamlReservedTagKeywords.FLOAT,
                    YamlReservedTagKeywords.STRING,
                    YamlReservedTagKeywords.BINARY,
                    YamlReservedTagKeywords.TIMESTAMP,
                    YamlReservedTagKeywords.BOOLEAN,
                    YamlReservedTagKeywords.NULL,
            ):
                if len(tokens) <= i + 1:
                    ret.append(tk)
                    continue
                if tk.line() != tokens[i + 1].line():
                    ret.append(tk)
                    continue
                if tokens[i + 1].group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                    ret.append(tk)
                    continue
                if is_scalar_type(tokens[i + 1]):
                    ret.append(YamlParseToken(
                        group=YamlParseTokenGroup(
                            type=YamlParseTokenGroupType.SCALAR_TAG,
                            tokens=[tk, tokens[i + 1]],
                        ),
                    ))
                    i += 1
                else:
                    ret.append(tk)
            elif tag.value == YamlReservedTagKeywords.MERGE:
                if len(tokens) <= i + 1:
                    ret.append(tk)
                    continue
                if tk.line() != tokens[i + 1].line():
                    ret.append(tk)
                    continue
                if tokens[i + 1].group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                    ret.append(tk)
                    continue
                if tokens[i + 1].type() != YamlTokenType.MERGE_KEY:
                    return err_syntax('could not find merge key', tokens[i + 1].raw_token())
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.SCALAR_TAG,
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
            if tokens[i + 1].group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                ret.append(tk)
                continue
            if is_flow_type(tokens[i + 1]):
                ret.append(tk)
                continue
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.SCALAR_TAG,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
    return ret


def create_anchor_with_scalar_tag_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
            if i + 1 >= len(tokens):
                return err_syntax('undefined anchor value', tk.raw_token())
            value_tk = tokens[i + 1]
            if tk.line() == value_tk.line() and value_tk.group_type() == YamlParseTokenGroupType.SCALAR_TAG:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.ANCHOR,
                        tokens=[tk, tokens[i + 1]],
                    ),
                ))
                i += 1
            else:
                ret.append(tk)
        else:
            ret.append(tk)
    return ret


def create_map_key_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    tks = create_map_key_by_mapping_key(tokens)
    if isinstance(tks, YamlError):
        return tks
    return create_map_key_by_mapping_value(tks)


def create_map_key_by_mapping_key(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.MAPPING_KEY:
            if i + 1 >= len(tokens):
                return err_syntax('undefined map key', tk.raw_token())
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.MAP_KEY,
                    tokens=[tk, tokens[i + 1]],
                ),
            ))
            i += 1
        else:
            ret.append(tk)
    return ret


def create_map_key_by_mapping_value(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.MAPPING_VALUE:
            if i == 0:
                return err_syntax('unexpected key name', tk.raw_token())
            map_key_tk = tokens[i - 1]
            if is_not_map_key_type(map_key_tk):
                return err_syntax('found an invalid key for this map', tokens[i].raw_token())
            new_tk = YamlParseToken(
                token=map_key_tk.token,
                group=map_key_tk.group,
            )
            map_key_tk.token = None
            map_key_tk.group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.MAP_KEY,
                tokens=[new_tk, tk],
            )
        else:
            ret.append(tk)
    return ret


def create_map_key_value_token_groups(tokens: ta.List[YamlParseToken]) -> ta.List[YamlParseToken]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.group_type() == YamlParseTokenGroupType.MAP_KEY:
            if len(tokens) <= i + 1:
                ret.append(tk)
                continue
            value_tk = tokens[i + 1]
            if tk.line() != value_tk.line():
                ret.append(tk)
                continue
            if value_tk.group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                ret.append(tk)
                continue
            if (
                    value_tk.type() == YamlTokenType.TAG and
                    value_tk.group_type() != YamlParseTokenGroupType.SCALAR_TAG
            ):
                ret.append(tk)
                continue

            if is_scalar_type(value_tk) or value_tk.type() == YamlTokenType.TAG:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.MAP_KEY_VALUE,
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


def create_directive_token_groups(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.DIRECTIVE:
            if i + 1 >= len(tokens):
                return err_syntax('undefined directive value', tk.raw_token())
            directive_name = YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.DIRECTIVE_NAME,
                    tokens=[tk, tokens[i + 1]],
                ),
            )
            i += 1
            value_tks: ta.List[YamlParseToken] = []
            for j in range(i + 1, len(tokens)):
                if tokens[j].line() != tk.line():
                    break
                value_tks.append(tokens[j])
                i += 1
            if i + 1 >= len(tokens) or tokens[i + 1].type() != YamlTokenType.DOCUMENT_HEADER:
                return err_syntax('unexpected directive value. document not started', tk.raw_token())
            if len(value_tks) != 0:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DIRECTIVE,
                        tokens=[directive_name, *value_tks],
                    ),
                ))
            else:
                ret.append(directive_name)
        else:
            ret.append(tk)
    return ret


def create_document_tokens(tokens: ta.List[YamlParseToken]) -> YamlErrorOr[ta.List[YamlParseToken]]:
    ret: ta.List[YamlParseToken] = []
    i = -1
    while True:
        i += 1
        if not (i < len(tokens)):
            break
        tk = tokens[i]
        if tk.type() == YamlTokenType.DOCUMENT_HEADER:
            if i != 0:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(tokens=tokens[:i]),
                ))
            if i + 1 == len(tokens):
                # if current token is last token, add DocumentHeader only tokens to ret.
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DOCUMENT,
                        tokens=[tk],
                    ),
                ))
                return ret
            if tokens[i + 1].type() == YamlTokenType.DOCUMENT_HEADER:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DOCUMENT,
                        tokens=[tk],
                    ),
                ))
                return ret
            if tokens[i].line() == tokens[i + 1].line():
                if tokens[i + 1].group_type() in (
                        YamlParseTokenGroupType.MAP_KEY,
                        YamlParseTokenGroupType.MAP_KEY_VALUE,
                ):
                    return err_syntax(
                        'value cannot be placed after document separator',
                        tokens[i + 1].raw_token(),
                    )
                if tokens[i + 1].type() == YamlTokenType.SEQUENCE_ENTRY:
                    return err_syntax(
                        'value cannot be placed after document separator',
                        tokens[i + 1].raw_token(),
                    )
            tks = create_document_tokens(tokens[i + 1:])
            if isinstance(tks, YamlError):
                return tks
            if len(tks) != 0:
                tks[0].set_group_type(YamlParseTokenGroupType.DOCUMENT)
                check.not_none(tks[0].group).tokens = list(check.not_none(tks[0].group).tokens)
                ret.extend(tks)
                return ret
            ret.append(YamlParseToken(
                group=YamlParseTokenGroup(
                    type=YamlParseTokenGroupType.DOCUMENT,
                    tokens=[tk],
                ),
            ))
            return ret
        elif tk.type() == YamlTokenType.DOCUMENT_END:
            if i != 0:
                ret.append(YamlParseToken(
                    group=YamlParseTokenGroup(
                        type=YamlParseTokenGroupType.DOCUMENT,
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
    ret.append(YamlParseToken(
        group=YamlParseTokenGroup(
            type=YamlParseTokenGroupType.DOCUMENT,
            tokens=tokens,
        ),
    ))
    return ret


def is_scalar_type(tk: YamlParseToken) -> bool:
    if tk.group_type() in (YamlParseTokenGroupType.MAP_KEY, YamlParseTokenGroupType.MAP_KEY_VALUE):
        return False
    typ = tk.type()
    return typ in (
        YamlTokenType.ANCHOR,
        YamlTokenType.ALIAS,
        YamlTokenType.LITERAL,
        YamlTokenType.FOLDED,
        YamlTokenType.NULL,
        YamlTokenType.IMPLICIT_NULL,
        YamlTokenType.BOOL,
        YamlTokenType.INTEGER,
        YamlTokenType.BINARY_INTEGER,
        YamlTokenType.OCTET_INTEGER,
        YamlTokenType.HEX_INTEGER,
        YamlTokenType.FLOAT,
        YamlTokenType.INFINITY,
        YamlTokenType.NAN,
        YamlTokenType.STRING,
        YamlTokenType.SINGLE_QUOTE,
        YamlTokenType.DOUBLE_QUOTE,
    )


def is_not_map_key_type(tk: YamlParseToken) -> bool:
    typ = tk.type()
    return typ in (
        YamlTokenType.DIRECTIVE,
        YamlTokenType.DOCUMENT_HEADER,
        YamlTokenType.DOCUMENT_END,
        YamlTokenType.COLLECT_ENTRY,
        YamlTokenType.MAPPING_START,
        YamlTokenType.MAPPING_VALUE,
        YamlTokenType.MAPPING_END,
        YamlTokenType.SEQUENCE_START,
        YamlTokenType.SEQUENCE_ENTRY,
        YamlTokenType.SEQUENCE_END,
    )


def is_flow_type(tk: YamlParseToken) -> bool:
    typ = tk.type()
    return typ in (
        YamlTokenType.MAPPING_START,
        YamlTokenType.MAPPING_END,
        YamlTokenType.SEQUENCE_START,
        YamlTokenType.SEQUENCE_ENTRY,
    )


##


class YamlNodeMakers:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    @staticmethod
    def new_mapping_node(
            ctx: YamlParsingContext,
            tk: YamlParseToken,
            is_flow: bool,
            *values: ast.MappingValueYamlNode,
    ) -> YamlErrorOr[ast.MappingYamlNode]:
        node = ast.mapping(check.not_none(tk.raw_token()), is_flow, *values)
        node.set_path(ctx.path)
        return node

    @staticmethod
    def new_mapping_value_node(
            ctx: YamlParsingContext,
            colon_tk: YamlParseToken,
            entry_tk: ta.Optional[YamlParseToken],
            key: ast.MapKeyYamlNode,
            value: ast.YamlNode,
    ) -> YamlErrorOr[ast.MappingValueYamlNode]:
        node = ast.mapping_value(check.not_none(colon_tk.raw_token()), key, value)
        node.set_path(ctx.path)
        node.collect_entry = YamlParseToken.raw_token(entry_tk)
        if check.not_none(key.get_token()).position.line == check.not_none(value.get_token()).position.line:
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

    @staticmethod
    def new_mapping_key_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.MappingKeyYamlNode]:  # noqa
        node = ast.mapping_key(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_anchor_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.AnchorYamlNode]:
        node = ast.anchor(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_alias_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.AliasYamlNode]:
        node = ast.alias(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_directive_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.DirectiveYamlNode]:  # noqa
        node = ast.directive(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_merge_key_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.MergeKeyYamlNode]:  # noqa
        node = ast.merge_key(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_null_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.NullYamlNode]:
        node = ast.null(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_bool_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.BoolYamlNode]:
        node = ast.bool_(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_integer_node(ctx: YamlParsingContext, tk: YamlParseToken) -> YamlErrorOr[ast.IntegerYamlNode]:
        node = ast.integer(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_float_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.FloatYamlNode]:
        node = ast.float_(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_infinity_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.InfinityYamlNode]:  # noqa
        node = ast.infinity(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_nan_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.NanYamlNode]:
        node = ast.nan(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_string_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.StringYamlNode]:
        node = ast.string(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_literal_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.LiteralYamlNode]:
        node = ast.literal(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_tag_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.TagYamlNode]:
        node = ast.tag(check.not_none(YamlParseToken.raw_token(tk)))
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_sequence_node(ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken], is_flow: bool) -> YamlErrorOr[ast.SequenceYamlNode]:  # noqa
        node = ast.sequence(check.not_none(YamlParseToken.raw_token(tk)), is_flow)
        node.set_path(ctx.path)
        if (err := set_line_comment(ctx, node, tk)) is not None:
            return err
        return node

    @staticmethod
    def new_tag_default_scalar_value_node(ctx: YamlParsingContext, tag: YamlToken) -> YamlErrorOr[ast.ScalarYamlNode]:
        pos = copy.copy(tag.position)
        pos.column += 1

        tk: YamlErrorOr[YamlParseToken]
        node: YamlErrorOr[ast.ScalarYamlNode]

        if tag.value == YamlReservedTagKeywords.INTEGER:
            tk = YamlParseToken(token=new_yaml_token('0', '0', pos))
            n0 = YamlNodeMakers.new_integer_node(ctx, tk)
            if isinstance(n0, YamlError):
                return n0
            node = n0
        elif tag.value == YamlReservedTagKeywords.FLOAT:
            tk = YamlParseToken(token=new_yaml_token('0', '0', pos))
            n1 = YamlNodeMakers.new_float_node(ctx, tk)
            if isinstance(n1, YamlError):
                return n1
            node = n1
        elif tag.value in (
                YamlReservedTagKeywords.STRING,
                YamlReservedTagKeywords.BINARY,
                YamlReservedTagKeywords.TIMESTAMP,
        ):
            tk = YamlParseToken(token=new_yaml_token('', '', pos))
            n2 = YamlNodeMakers.new_string_node(ctx, tk)
            if isinstance(n2, YamlError):
                return n2
            node = n2
        elif tag.value == YamlReservedTagKeywords.BOOLEAN:
            tk = YamlParseToken(token=new_yaml_token('false', 'false', pos))
            n3 = YamlNodeMakers.new_bool_node(ctx, tk)
            if isinstance(n3, YamlError):
                return n3
            node = n3
        elif tag.value == YamlReservedTagKeywords.NULL:
            tk = YamlParseToken(token=new_yaml_token('null', 'null', pos))
            n4 = YamlNodeMakers.new_null_node(ctx, tk)
            if isinstance(n4, YamlError):
                return n4
            node = n4
        else:
            return err_syntax(f'cannot assign default value for {tag.value!r} tag', tag)
        ctx.insert_token(tk)
        ctx.go_next()
        return node


def set_line_comment(ctx: YamlParsingContext, node: ast.YamlNode, tk: ta.Optional[YamlParseToken]) -> ta.Optional[YamlError]:  # noqa
    if tk is None or tk.line_comment is None:
        return None
    comment = ast.comment_group([tk.line_comment])
    comment.set_path(ctx.path)
    if (err := node.set_comment(comment)) is not None:
        return err
    return None


def set_head_comment(cm: ta.Optional[ast.CommentGroupYamlNode], value: ast.YamlNode) -> ta.Optional[YamlError]:
    if cm is None:
        return None
    n = value
    if isinstance(n, ast.MappingYamlNode):
        if len(n.values) != 0 and value.get_comment() is None:
            cm.set_path(n.values[0].get_path())
            return n.values[0].set_comment(cm)
    elif isinstance(n, ast.MappingValueYamlNode):
        cm.set_path(n.get_path())
        return n.set_comment(cm)
    cm.set_path(value.get_path())
    return value.set_comment(cm)


##


ParseMode = int  # ta.TypeAlias  # omlish-amalg-typing-no-move

PARSE_COMMENTS = ParseMode(1)  # parse comments and add them to AST


# ParseBytes parse from byte slice, and returns ast.File
def parse_str(
        s: str,
        mode: ParseMode = ParseMode(0),
        *opts: Option,
) -> YamlErrorOr[ast.YamlFile]:
    tokens = yaml_tokenize(s)
    f = parse(tokens, mode, *opts)
    if isinstance(f, YamlError):
        return f
    return f


# Parse parse from token instances, and returns ast.File
def parse(
        tokens: YamlTokens,
        mode: ParseMode = ParseMode(0),
        *opts: Option,
) -> YamlErrorOr[ast.YamlFile]:
    if (tk := tokens.invalid_token()) is not None:
        return err_syntax(check.not_none(tk.error).message, tk)
    p = YamlParser.new_parser(tokens, mode, opts)
    if isinstance(p, YamlError):
        return p
    f = p.parse(YamlParsingContext.new())
    if isinstance(f, YamlError):
        return f
    return f


#


YAMLVersion = str  # ta.TypeAlias  # omlish-amalg-typing-no-move

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

@dc.dataclass()
class YamlParser:
    tokens: ta.List[YamlParseToken]
    path_map: ta.Dict[str, ast.YamlNode]
    yaml_version: YAMLVersion = YAMLVersion('')
    allow_duplicate_map_key: bool = False
    secondary_tag_directive: ta.Optional[ast.DirectiveYamlNode] = None

    @staticmethod
    def new_parser(
            tokens: YamlTokens,
            mode: ParseMode,
            opts: ta.Iterable[Option],
    ) -> YamlErrorOr['YamlParser']:
        filtered_tokens: ta.List[YamlToken] = []
        if mode & PARSE_COMMENTS != 0:
            filtered_tokens = tokens
        else:
            for tk in tokens:
                if tk.type == YamlTokenType.COMMENT:
                    continue
                # keep prev/next reference between tokens containing comments
                # https://github.com/goccy/go-yaml/issues/254
                filtered_tokens.append(tk)
        tks = create_grouped_tokens(YamlTokens(filtered_tokens))
        if isinstance(tks, YamlError):
            return tks
        p = YamlParser(
            tokens=tks,
            path_map={},
        )
        for opt in opts:
            opt(p)
        return p

    def parse(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.YamlFile]:
        file = ast.YamlFile(docs=[])
        for token in self.tokens:
            doc = self.parse_document(ctx, check.not_none(token.group))
            if isinstance(doc, YamlError):
                return doc
            file.docs.append(doc)
        return file

    def parse_document(
            self,
            ctx: YamlParsingContext,
            doc_group: YamlParseTokenGroup,
    ) -> YamlErrorOr[ast.DocumentYamlNode]:
        if len(doc_group.tokens) == 0:
            return ast.document(doc_group.raw_token(), None)

        self.path_map: ta.Dict[str, ast.YamlNode] = {}

        tokens = doc_group.tokens
        start: ta.Optional[YamlToken] = None
        end: ta.Optional[YamlToken] = None
        if YamlParseToken.type(doc_group.first()) == YamlTokenType.DOCUMENT_HEADER:
            start = YamlParseToken.raw_token(doc_group.first())
            tokens = tokens[1:]

        clear_yaml_version = False
        try:
            if YamlParseToken.type(doc_group.last()) == YamlTokenType.DOCUMENT_END:
                end = YamlParseToken.raw_token(doc_group.last())
                tokens = tokens[:len(tokens) - 1]
                # clear yaml version value if DocumentEnd token (...) is specified.
                clear_yaml_version = True

            if len(tokens) == 0:
                return ast.document(doc_group.raw_token(), None)

            body = self.parse_document_body(ctx.with_group(YamlParseTokenGroup(
                type=YamlParseTokenGroupType.DOCUMENT_BODY,
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

    def parse_document_body(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.YamlNode]:
        node = self.parse_token(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        if ctx.next():
            return err_syntax('value is not allowed in this context', YamlParseToken.raw_token(ctx.current_token()))
        return node

    def parse_token(self, ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ast.YamlNode]:
        if YamlParseToken.group_type(tk) in (
                YamlParseTokenGroupType.MAP_KEY,
                YamlParseTokenGroupType.MAP_KEY_VALUE,
        ):
            return self.parse_map(ctx)
        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.DIRECTIVE:
            node0 = self.parse_directive(
                ctx.with_group(check.not_none(check.not_none(tk).group)),
                check.not_none(check.not_none(tk).group),
            )
            if isinstance(node0, YamlError):
                return node0
            ctx.go_next()
            return node0
        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.DIRECTIVE_NAME:
            node1 = self.parse_directive_name(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node1, YamlError):
                return node1
            ctx.go_next()
            return node1
        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR:
            node2 = self.parse_anchor(
                ctx.with_group(check.not_none(check.not_none(tk).group)),
                check.not_none(check.not_none(tk).group),
            )
            if isinstance(node2, YamlError):
                return node2
            ctx.go_next()
            return node2
        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME:
            anchor = self.parse_anchor_name(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            if ctx.is_token_not_found():
                return err_syntax('could not find anchor value', YamlParseToken.raw_token(tk))
            value = self.parse_token(ctx, ctx.current_token())
            if isinstance(value, YamlError):
                return value
            if isinstance(value, ast.AnchorYamlNode):
                return err_syntax('anchors cannot be used consecutively', value.get_token())
            anchor.value = value
            return anchor
        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ALIAS:
            node3 = self.parse_alias(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node3, YamlError):
                return node3
            ctx.go_next()
            return node3
        elif YamlParseToken.group_type(tk) in (
                YamlParseTokenGroupType.LITERAL,
                YamlParseTokenGroupType.FOLDED,
        ):
            node4 = self.parse_literal(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node4, YamlError):
                return node4
            ctx.go_next()
            return node4
        elif YamlParseToken.group_type(tk) == YamlParseTokenGroupType.SCALAR_TAG:
            node5 = self.parse_tag(ctx.with_group(check.not_none(check.not_none(tk).group)))
            if isinstance(node5, YamlError):
                return node5
            ctx.go_next()
            return node5
        if YamlParseToken.type(tk) == YamlTokenType.COMMENT:
            return ta.cast('YamlErrorOr[ast.YamlNode]', check.not_none(self.parse_comment(ctx)))
        elif YamlParseToken.type(tk) == YamlTokenType.TAG:
            return self.parse_tag(ctx)
        elif YamlParseToken.type(tk) == YamlTokenType.MAPPING_START:
            return self.parse_flow_map(ctx.with_flow(True))
        elif YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_START:
            return self.parse_flow_sequence(ctx.with_flow(True))
        elif YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_ENTRY:
            return self.parse_sequence(ctx)
        elif YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_END:
            # SequenceEndType is always validated in parse_flow_sequence.
            # Therefore, if this is found in other cases, it is treated as a syntax error.
            return err_syntax("could not find '[' character corresponding to ']'", YamlParseToken.raw_token(tk))
        elif YamlParseToken.type(tk) == YamlTokenType.MAPPING_END:
            # MappingEndType is always validated in parse_flow_map.
            # Therefore, if this is found in other cases, it is treated as a syntax error.
            return err_syntax("could not find '{' character corresponding to '}'", YamlParseToken.raw_token(tk))
        elif YamlParseToken.type(tk) == YamlTokenType.MAPPING_VALUE:
            return err_syntax('found an invalid key for this map', YamlParseToken.raw_token(tk))
        node6 = self.parse_scalar_value(ctx, tk)
        if isinstance(node6, YamlError):
            return node6
        ctx.go_next()
        return check.not_none(node6)

    def parse_scalar_value(self, ctx: YamlParsingContext, tk: ta.Optional[YamlParseToken]) -> YamlErrorOr[ta.Optional[ast.ScalarYamlNode]]:  # noqa
        tk = check.not_none(tk)
        if tk.group is not None:
            if tk.group_type() == YamlParseTokenGroupType.ANCHOR:
                return self.parse_anchor(ctx.with_group(tk.group), tk.group)
            elif tk.group_type() == YamlParseTokenGroupType.ANCHOR_NAME:
                anchor = self.parse_anchor_name(ctx.with_group(tk.group))
                if isinstance(anchor, YamlError):
                    return anchor
                ctx.go_next()
                if ctx.is_token_not_found():
                    return err_syntax('could not find anchor value', tk.raw_token())
                value = self.parse_token(ctx, ctx.current_token())
                if isinstance(value, YamlError):
                    return value
                if isinstance(value, ast.AnchorYamlNode):
                    return err_syntax('anchors cannot be used consecutively', value.get_token())
                anchor.value = value
                return anchor
            elif tk.group_type() == YamlParseTokenGroupType.ALIAS:
                return self.parse_alias(ctx.with_group(tk.group))
            elif tk.group_type() in (
                    YamlParseTokenGroupType.LITERAL,
                    YamlParseTokenGroupType.FOLDED,
            ):
                return self.parse_literal(ctx.with_group(tk.group))
            elif tk.group_type() == YamlParseTokenGroupType.SCALAR_TAG:
                return self.parse_tag(ctx.with_group(tk.group))
            else:
                return err_syntax('unexpected scalar value', tk.raw_token())
        if tk.type() == YamlTokenType.MERGE_KEY:
            return YamlNodeMakers.new_merge_key_node(ctx, tk)
        if tk.type() in (YamlTokenType.NULL, YamlTokenType.IMPLICIT_NULL):
            return YamlNodeMakers.new_null_node(ctx, tk)
        if tk.type() == YamlTokenType.BOOL:
            return YamlNodeMakers.new_bool_node(ctx, tk)
        if tk.type() in (
                YamlTokenType.INTEGER,
                YamlTokenType.BINARY_INTEGER,
                YamlTokenType.OCTET_INTEGER,
                YamlTokenType.HEX_INTEGER,
        ):
            return YamlNodeMakers.new_integer_node(ctx, tk)
        if tk.type() == YamlTokenType.FLOAT:
            return YamlNodeMakers.new_float_node(ctx, tk)
        if tk.type() == YamlTokenType.INFINITY:
            return YamlNodeMakers.new_infinity_node(ctx, tk)
        if tk.type() == YamlTokenType.NAN:
            return YamlNodeMakers.new_nan_node(ctx, tk)
        if tk.type() in (
                YamlTokenType.STRING,
                YamlTokenType.SINGLE_QUOTE,
                YamlTokenType.DOUBLE_QUOTE,
        ):
            return YamlNodeMakers.new_string_node(ctx, tk)
        if tk.type() == YamlTokenType.TAG:
            # this case applies when it is a scalar tag and its value does not exist.
            # Examples of cases where the value does not exist include cases like `key: !!str,` or `!!str : value`.
            return self.parse_scalar_tag(ctx)
        return err_syntax('unexpected scalar value type', tk.raw_token())

    def parse_flow_map(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.MappingYamlNode]:
        node = YamlNodeMakers.new_mapping_node(ctx, check.not_none(ctx.current_token()), True)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip MappingStart token

        is_first = True
        while ctx.next():
            tk = ctx.current_token()
            if YamlParseToken.type(tk) == YamlTokenType.MAPPING_END:
                node.end = YamlParseToken.raw_token(tk)
                break

            entry_tk: ta.Optional[YamlParseToken] = None
            if YamlParseToken.type(tk) == YamlTokenType.COLLECT_ENTRY:
                entry_tk = tk
                ctx.go_next()
            elif not is_first:
                return err_syntax("',' or '}' must be specified", YamlParseToken.raw_token(tk))

            if YamlParseToken.type(tk := ctx.current_token()) == YamlTokenType.MAPPING_END:
                # this case is here: "{ elem, }".
                # In this case, ignore the last element and break mapping parsing.
                node.end = YamlParseToken.raw_token(tk)
                break

            map_key_tk = ctx.current_token()
            if YamlParseToken.group_type(map_key_tk) == YamlParseTokenGroupType.MAP_KEY_VALUE:
                value0 = self.parse_map_key_value(
                    ctx.with_group(check.not_none(check.not_none(map_key_tk).group)),
                    check.not_none(check.not_none(map_key_tk).group),
                    entry_tk,
                )
                if isinstance(value0, YamlError):
                    return value0
                node.values.append(value0)
                ctx.go_next()
            elif YamlParseToken.group_type(map_key_tk) == YamlParseTokenGroupType.MAP_KEY:
                key0 = self.parse_map_key(
                    ctx.with_group(check.not_none(check.not_none(map_key_tk).group)),
                    check.not_none(check.not_none(map_key_tk).group),
                )
                if isinstance(key0, YamlError):
                    return key0
                ctx = ctx.with_child(self.map_key_text(key0))
                colon_tk = check.not_none(check.not_none(map_key_tk).group).last()
                if self.is_flow_map_delim(check.not_none(ctx.next_token())):
                    value1 = YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(check.not_none(colon_tk)))
                    if isinstance(value1, YamlError):
                        return value1
                    map_value = YamlNodeMakers.new_mapping_value_node(
                        ctx,
                        check.not_none(colon_tk),
                        entry_tk,
                        key0,
                        value1,
                    )
                    if isinstance(map_value, YamlError):
                        return map_value
                    node.values.append(map_value)
                    ctx.go_next()
                else:
                    ctx.go_next()
                    if ctx.is_token_not_found():
                        return err_syntax('could not find map value', YamlParseToken.raw_token(colon_tk))
                    value2 = self.parse_token(ctx, ctx.current_token())
                    if isinstance(value2, YamlError):
                        return value2
                    map_value = YamlNodeMakers.new_mapping_value_node(
                        ctx,
                        check.not_none(colon_tk),
                        entry_tk,
                        key0,
                        value2,
                    )
                    if isinstance(map_value, YamlError):
                        return map_value
                    node.values.append(map_value)
            else:
                if not self.is_flow_map_delim(check.not_none(ctx.next_token())):
                    err_tk = map_key_tk
                    if err_tk is None:
                        err_tk = tk
                    return err_syntax('could not find flow map content', YamlParseToken.raw_token(err_tk))
                key1 = self.parse_scalar_value(ctx, map_key_tk)
                if isinstance(key1, YamlError):
                    return key1
                value3 = YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(check.not_none(map_key_tk)))
                if isinstance(value3, YamlError):
                    return value3
                map_value = YamlNodeMakers.new_mapping_value_node(
                    ctx,
                    check.not_none(map_key_tk),
                    entry_tk,
                    check.not_none(key1),
                    value3,
                )
                if isinstance(map_value, YamlError):
                    return map_value
                node.values.append(map_value)
                ctx.go_next()
            is_first = False
        if node.end is None:
            return err_syntax("could not find flow mapping end token '}'", node.start)
        ctx.go_next()  # skip mapping end token.
        return node

    def is_flow_map_delim(self, tk: YamlParseToken) -> bool:
        return tk.type() == YamlTokenType.MAPPING_END or tk.type() == YamlTokenType.COLLECT_ENTRY

    def parse_map(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.MappingYamlNode]:
        key_tk = check.not_none(ctx.current_token())
        if key_tk.group is None:
            return err_syntax('unexpected map key', YamlParseToken.raw_token(key_tk))
        key_value_node: ast.MappingValueYamlNode
        if YamlParseToken.group_type(key_tk) == YamlParseTokenGroupType.MAP_KEY_VALUE:
            node0 = self.parse_map_key_value(
                ctx.with_group(check.not_none(key_tk.group)),
                check.not_none(key_tk.group),
                None,
            )
            if isinstance(node0, YamlError):
                return node0
            key_value_node = node0
            ctx.go_next()
            if (err := self.validate_map_key_value_next_token(ctx, key_tk, ctx.current_token())) is not None:
                return err
        else:
            key = self.parse_map_key(ctx.with_group(check.not_none(key_tk.group)), check.not_none(key_tk.group))
            if isinstance(key, YamlError):
                return key
            ctx.go_next()

            value_tk = ctx.current_token()
            if (
                    YamlParseToken.line(key_tk) == YamlParseToken.line(value_tk) and
                    YamlParseToken.type(value_tk) == YamlTokenType.SEQUENCE_ENTRY
            ):
                return err_syntax(
                    'block sequence entries are not allowed in this context',
                    YamlParseToken.raw_token(value_tk),
                )
            ctx = ctx.with_child(self.map_key_text(key))
            value = self.parse_map_value(ctx, key, check.not_none(check.not_none(key_tk.group).last()))
            if isinstance(value, YamlError):
                return value
            node1 = YamlNodeMakers.new_mapping_value_node(
                ctx,
                check.not_none(check.not_none(key_tk.group).last()),
                None,
                key,
                value,
            )
            if isinstance(node1, YamlError):
                return node1
            key_value_node = node1
        map_node = YamlNodeMakers.new_mapping_node(
            ctx,
            YamlParseToken(token=key_value_node.get_token()),
            False,
            key_value_node,
        )
        if isinstance(map_node, YamlError):
            return map_node
        tk: ta.Optional[YamlParseToken]
        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        else:
            tk = ctx.current_token()
        while YamlParseToken.column(tk) == YamlParseToken.column(key_tk):
            typ = YamlParseToken.type(tk)
            if ctx.is_flow and typ == YamlTokenType.SEQUENCE_END:
                # [
                # key: value
                # ] <=
                break
            if not self.is_map_token(check.not_none(tk)):
                return err_syntax('non-map value is specified', YamlParseToken.raw_token(tk))
            cm = self.parse_head_comment(ctx)
            if typ == YamlTokenType.MAPPING_END:
                # a: {
                #  b: c
                # } <=
                ctx.go_next()
                break
            node2 = self.parse_map(ctx)
            if isinstance(node2, YamlError):
                return node2
            if len(node2.values) != 0:
                if (err := set_head_comment(cm, node2.values[0])) is not None:
                    return err
            map_node.values.extend(node2.values)
            if node2.foot_comment is not None:
                map_node.values[len(map_node.values) - 1].foot_comment = node2.foot_comment
            tk = ctx.current_token()
        if ctx.is_comment():
            if YamlParseToken.column(key_tk) <= YamlParseToken.column(ctx.current_token()):
                # If the comment is in the same or deeper column as the last element column in map value,
                # treat it as a footer comment for the last element.
                if len(map_node.values) == 1:
                    map_node.values[0].foot_comment = self.parse_foot_comment(ctx, YamlParseToken.column(key_tk))
                    ast.BaseYamlNode.set_path(map_node.values[0].foot_comment, map_node.values[0].key.get_path())
                else:
                    map_node.foot_comment = self.parse_foot_comment(ctx, YamlParseToken.column(key_tk))
                    ast.BaseYamlNode.set_path(map_node.foot_comment, map_node.get_path())
        return map_node

    def validate_map_key_value_next_token(self, ctx: YamlParsingContext, key_tk, tk: ta.Optional[YamlParseToken]) -> ta.Optional[YamlError]:  # noqa
        if tk is None:
            return None
        if tk.column() <= key_tk.column():
            return None
        if ctx.is_comment():
            return None
        if (
                ctx.is_flow and
                (tk.type() == YamlTokenType.COLLECT_ENTRY or tk.type() == YamlTokenType.SEQUENCE_END)
        ):
            return None
        # a: b
        #  c <= this token is invalid.
        return err_syntax('value is not allowed in this context. map key-value is pre-defined', tk.raw_token())

    def is_map_token(self, tk: YamlParseToken) -> bool:
        if tk.group is None:
            return tk.type() == YamlTokenType.MAPPING_START or tk.type() == YamlTokenType.MAPPING_END
        g = tk.group
        return g.type == YamlParseTokenGroupType.MAP_KEY or g.type == YamlParseTokenGroupType.MAP_KEY_VALUE

    def parse_map_key_value(self,
                            ctx: YamlParsingContext,
                            g: YamlParseTokenGroup,
                            entry_tk: ta.Optional[YamlParseToken],
                            ) -> YamlErrorOr[ast.MappingValueYamlNode]:
        if g.type != YamlParseTokenGroupType.MAP_KEY_VALUE:
            return err_syntax('unexpected map key-value pair', g.raw_token())
        if check.not_none(g.first()).group is None:
            return err_syntax('unexpected map key', g.raw_token())
        key_group = check.not_none(check.not_none(g.first()).group)
        key = self.parse_map_key(ctx.with_group(key_group), key_group)
        if isinstance(key, YamlError):
            return key

        c = ctx.with_child(self.map_key_text(key))
        value = self.parse_token(c, g.last())
        if isinstance(value, YamlError):
            return value
        return YamlNodeMakers.new_mapping_value_node(c, check.not_none(key_group.last()), entry_tk, key, value)

    def parse_map_key(self, ctx: YamlParsingContext, g: YamlParseTokenGroup) -> YamlErrorOr[ast.MapKeyYamlNode]:
        if g.type != YamlParseTokenGroupType.MAP_KEY:
            return err_syntax('unexpected map key', g.raw_token())
        if YamlParseToken.type(g.first()) == YamlTokenType.MAPPING_KEY:
            map_key_tk = check.not_none(g.first())
            if map_key_tk.group is not None:
                ctx = ctx.with_group(map_key_tk.group)
            key0 = YamlNodeMakers.new_mapping_key_node(ctx, map_key_tk)
            if isinstance(key0, YamlError):
                return key0
            ctx.go_next()  # skip mapping key token
            if ctx.is_token_not_found():
                return err_syntax('could not find value for mapping key', YamlParseToken.raw_token(map_key_tk))

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
        if YamlParseToken.type(g.last()) != YamlTokenType.MAPPING_VALUE:
            return err_syntax("expected map key-value delimiter ':'", YamlParseToken.raw_token(g.last()))

        scalar1 = self.parse_scalar_value(ctx, g.first())
        if isinstance(scalar1, YamlError):
            return scalar1
        if not isinstance(scalar1, ast.MapKeyYamlNode):
            # FIXME: not possible
            return err_syntax(
                'cannot take map-key node',
                check.not_none(scalar1).get_token(),
            )
        key1: ast.MapKeyYamlNode = ta.cast(ast.MapKeyYamlNode, scalar1)
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
            ctx: YamlParsingContext,
            tk: YamlToken,
            key_path: str,
            colon_tk: YamlParseToken,
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
            if tk.type == YamlTokenType.STRING:
                origin = self.remove_right_white_space(origin)
                if tk.position.line + self.new_line_character_num(origin) != colon_tk.line():
                    return err_syntax('map key definition includes an implicit line break', tk)
            return None
        if (
                tk.type != YamlTokenType.STRING and
                tk.type != YamlTokenType.SINGLE_QUOTE and
                tk.type != YamlTokenType.DOUBLE_QUOTE
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

    def map_key_text(self, n: ta.Optional[ast.YamlNode]) -> str:
        if n is None:
            return ''
        nn = n
        if isinstance(nn, ast.MappingKeyYamlNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, ast.TagYamlNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, ast.AnchorYamlNode):
            return self.map_key_text(nn.value)
        if isinstance(nn, ast.AliasYamlNode):
            return ''
        return check.not_none(n.get_token()).value

    def parse_map_value(
            self,
            ctx: YamlParsingContext,
            key: ast.MapKeyYamlNode,
            colon_tk: YamlParseToken,
    ) -> YamlErrorOr[ast.YamlNode]:
        tk = ctx.current_token()
        if tk is None:
            return YamlNodeMakers.new_null_node(ctx, ctx.add_null_value_token(colon_tk))

        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        key_col = check.not_none(key.get_token()).position.column
        key_line = check.not_none(key.get_token()).position.line

        if (
            YamlParseToken.column(tk) != key_col and
            YamlParseToken.line(tk) == key_line and
            (
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.MAP_KEY or
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.MAP_KEY_VALUE
            )
        ):
            # a: b:
            #    ^
            #
            # a: b: c
            #    ^
            return err_syntax('mapping value is not allowed in this context', YamlParseToken.raw_token(tk))

        if YamlParseToken.column(tk) == key_col and self.is_map_token(check.not_none(tk)):
            # in this case,
            # ----
            # key: <value does not defined>
            # next
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(colon_tk))

        if (
                YamlParseToken.line(tk) == key_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) == key_col and
                self.is_map_token(check.not_none(ctx.next_token()))
        ):
            # in this case,
            # ----
            # key: &anchor
            # next
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        if (
                YamlParseToken.column(tk) <= key_col and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME
        ):
            # key: <value does not defined>
            # &anchor
            return err_syntax('anchor is not allowed in this context', YamlParseToken.raw_token(tk))
        if YamlParseToken.column(tk) <= key_col and YamlParseToken.type(tk) == YamlTokenType.TAG:
            # key: <value does not defined>
            # !!tag
            return err_syntax('tag is not allowed in this context', YamlParseToken.raw_token(tk))

        if YamlParseToken.column(tk) < key_col:
            # in this case,
            # ----
            #   key: <value does not defined>
            # next
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(colon_tk))

        if (
                YamlParseToken.line(tk) == key_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) < key_col
        ):
            # in this case,
            # ----
            #   key: &anchor
            # next
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
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

    def validate_anchor_value_in_map_or_seq(self, value: ast.YamlNode, col: int) -> ta.Optional[YamlError]:
        if not isinstance(value, ast.AnchorYamlNode):
            return None
        anchor: ast.AnchorYamlNode = value
        if not isinstance(anchor.value, ast.TagYamlNode):
            return None
        tag: ast.TagYamlNode = anchor.value
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

    def parse_anchor(self, ctx: YamlParsingContext, g: YamlParseTokenGroup) -> YamlErrorOr[ast.AnchorYamlNode]:
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
        if isinstance(value, ast.AnchorYamlNode):
            return err_syntax('anchors cannot be used consecutively', value.get_token())
        anchor.value = value
        return anchor

    def parse_anchor_name(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.AnchorYamlNode]:
        anchor = YamlNodeMakers.new_anchor_node(ctx, ctx.current_token())
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
                YamlParseToken.raw_token(ctx.current_token()),
            )
        anchor.name = anchor_name
        return anchor

    def parse_alias(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.AliasYamlNode]:
        alias = YamlNodeMakers.new_alias_node(ctx, ctx.current_token())
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
                YamlParseToken.raw_token(ctx.current_token()),
            )
        alias.value = alias_name
        return alias

    def parse_literal(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.LiteralYamlNode]:
        node = YamlNodeMakers.new_literal_node(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip literal/folded token

        tk = ctx.current_token()
        if tk is None:
            value0 = YamlNodeMakers.new_string_node(
                ctx,
                YamlParseToken(token=new_yaml_token('', '', node.start.position)),
            )
            if isinstance(value0, YamlError):
                return value0
            node.value = value0
            return node
        value1 = self.parse_token(ctx, tk)
        if isinstance(value1, YamlError):
            return value1
        if not isinstance(s := value1, ast.StringYamlNode):
            return err_syntax('unexpected token. required string token', value1.get_token())
        node.value = s
        return node

    def parse_scalar_tag(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.TagYamlNode]:
        tag = self.parse_tag(ctx)
        if isinstance(tag, YamlError):
            return tag
        if tag.value is None:
            return err_syntax('specified not scalar tag', tag.get_token())
        if not isinstance(tag.value, ast.ScalarYamlNode):
            return err_syntax('specified not scalar tag', tag.get_token())
        return tag

    def parse_tag(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.TagYamlNode]:
        tag_tk = ctx.current_token()
        tag_raw_tk = YamlParseToken.raw_token(tag_tk)
        node = YamlNodeMakers.new_tag_node(ctx, tag_tk)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()

        comment = self.parse_head_comment(ctx)

        tag_value: ast.YamlNode
        if self.secondary_tag_directive is not None:
            value0 = YamlNodeMakers.new_string_node(ctx, ctx.current_token())
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
            ctx: YamlParsingContext,
            tag_raw_tk: YamlToken,
            tk: ta.Optional[YamlParseToken],
    ) -> YamlErrorOr[ta.Optional[ast.YamlNode]]:
        if tk is None:
            return YamlNodeMakers.new_null_node(ctx, ctx.create_implicit_null_token(YamlParseToken(token=tag_raw_tk)))
        if tag_raw_tk.value in (
                YamlReservedTagKeywords.MAPPING,
                YamlReservedTagKeywords.SET,
        ):
            if not self.is_map_token(tk):
                return err_syntax('could not find map', tk.raw_token())
            if tk.type() == YamlTokenType.MAPPING_START:
                return self.parse_flow_map(ctx.with_flow(True))
            return self.parse_map(ctx)
        elif tag_raw_tk.value in (
                YamlReservedTagKeywords.INTEGER,
                YamlReservedTagKeywords.FLOAT,
                YamlReservedTagKeywords.STRING,
                YamlReservedTagKeywords.BINARY,
                YamlReservedTagKeywords.TIMESTAMP,
                YamlReservedTagKeywords.BOOLEAN,
                YamlReservedTagKeywords.NULL,
        ):
            if tk.group_type() == YamlParseTokenGroupType.LITERAL or tk.group_type() == YamlParseTokenGroupType.FOLDED:
                return self.parse_literal(ctx.with_group(check.not_none(tk.group)))
            elif tk.type() == YamlTokenType.COLLECT_ENTRY or tk.type() == YamlTokenType.MAPPING_VALUE:
                return YamlNodeMakers.new_tag_default_scalar_value_node(ctx, tag_raw_tk)
            scalar = self.parse_scalar_value(ctx, tk)
            if isinstance(scalar, YamlError):
                return scalar
            ctx.go_next()
            return scalar
        elif tag_raw_tk.value in (
                YamlReservedTagKeywords.SEQUENCE,
                YamlReservedTagKeywords.ORDERED_MAP,
        ):
            if tk.type() == YamlTokenType.SEQUENCE_START:
                return self.parse_flow_sequence(ctx.with_flow(True))
            return self.parse_sequence(ctx)
        return self.parse_token(ctx, tk)

    def parse_flow_sequence(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.SequenceYamlNode]:
        node = YamlNodeMakers.new_sequence_node(ctx, ctx.current_token(), True)
        if isinstance(node, YamlError):
            return node
        ctx.go_next()  # skip SequenceStart token

        is_first = True
        while ctx.next():
            tk = ctx.current_token()
            if YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_END:
                node.end = YamlParseToken.raw_token(tk)
                break

            entry_tk: ta.Optional[YamlParseToken] = None
            if YamlParseToken.type(tk) == YamlTokenType.COLLECT_ENTRY:
                if is_first:
                    return err_syntax("expected sequence element, but found ','", YamlParseToken.raw_token(tk))
                entry_tk = tk
                ctx.go_next()
            elif not is_first:
                return err_syntax("',' or ']' must be specified", YamlParseToken.raw_token(tk))

            if YamlParseToken.type(tk := ctx.current_token()) == YamlTokenType.SEQUENCE_END:
                # this case is here: "[ elem, ]".
                # In this case, ignore the last element and break sequence parsing.
                node.end = YamlParseToken.raw_token(tk)
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

    def parse_sequence(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.SequenceYamlNode]:
        seq_tk = ctx.current_token()
        seq_node = YamlNodeMakers.new_sequence_node(ctx, seq_tk, False)
        if isinstance(seq_node, YamlError):
            return seq_node

        tk = seq_tk
        while (
                YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_ENTRY and
                YamlParseToken.column(tk) == YamlParseToken.column(seq_tk)
        ):
            head_comment = self.parse_head_comment(ctx)
            ctx.go_next()  # skip sequence entry token

            ctx = ctx.with_index(len(seq_node.values))
            value = self.parse_sequence_value(ctx, check.not_none(seq_tk))
            if isinstance(value, YamlError):
                return value
            seq_entry = ast.sequence_entry(YamlParseToken.raw_token(seq_tk), value, head_comment)
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
            if YamlParseToken.column(seq_tk) <= YamlParseToken.column(ctx.current_token()):
                # If the comment is in the same or deeper column as the last element column in sequence value,
                # treat it as a footer comment for the last element.
                seq_node.foot_comment = self.parse_foot_comment(ctx, YamlParseToken.column(seq_tk))
                if len(seq_node.values) != 0:
                    check.not_none(seq_node.foot_comment).set_path(
                        check.not_none(seq_node.values[len(seq_node.values) - 1]).get_path(),
                    )
        return seq_node

    def parse_sequence_value(self, ctx: YamlParsingContext, seq_tk: YamlParseToken) -> YamlErrorOr[ast.YamlNode]:
        tk = ctx.current_token()
        if tk is None:
            return YamlNodeMakers.new_null_node(ctx, ctx.add_null_value_token(seq_tk))

        if ctx.is_comment():
            tk = ctx.next_not_comment_token()
        seq_col = seq_tk.column()
        seq_line = seq_tk.line()

        if YamlParseToken.column(tk) == seq_col and YamlParseToken.type(tk) == YamlTokenType.SEQUENCE_ENTRY:
            # in this case,
            # ----
            # - <value does not defined>
            # -
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(seq_tk))

        if (
                YamlParseToken.line(tk) == seq_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) == seq_col and
                YamlParseToken.type(ctx.next_token()) == YamlTokenType.SEQUENCE_ENTRY
        ):
            # in this case,
            # ----
            # - &anchor
            # -
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
                tokens=[check.not_none(tk), ctx.create_implicit_null_token(check.not_none(tk))],
            )
            anchor = self.parse_anchor(ctx.with_group(group), group)
            if isinstance(anchor, YamlError):
                return anchor
            ctx.go_next()
            return anchor

        if (
                YamlParseToken.column(tk) <= seq_col and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME
        ):
            # - <value does not defined>
            # &anchor
            return err_syntax('anchor is not allowed in this sequence context', YamlParseToken.raw_token(tk))
        if YamlParseToken.column(tk) <= seq_col and YamlParseToken.type(tk) == YamlTokenType.TAG:
            # - <value does not defined>
            # !!tag
            return err_syntax('tag is not allowed in this sequence context', YamlParseToken.raw_token(tk))

        if YamlParseToken.column(tk) < seq_col:
            # in this case,
            # ----
            #   - <value does not defined>
            # next
            return YamlNodeMakers.new_null_node(ctx, ctx.insert_null_token(seq_tk))

        if (
                YamlParseToken.line(tk) == seq_line and
                YamlParseToken.group_type(tk) == YamlParseTokenGroupType.ANCHOR_NAME and
                YamlParseToken.column(ctx.next_token()) < seq_col
        ):
            # in this case,
            # ----
            #   - &anchor
            # next
            group = YamlParseTokenGroup(
                type=YamlParseTokenGroupType.ANCHOR,
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

    def parse_directive(self, ctx: YamlParsingContext, g: YamlParseTokenGroup) -> YamlErrorOr[ast.DirectiveYamlNode]:
        directive_name_group = check.not_none(check.not_none(g.first()).group)
        directive = self.parse_directive_name(ctx.with_group(directive_name_group))
        if isinstance(directive, YamlError):
            return directive

        if directive.name == 'YAML':
            if len(g.tokens) != 2:
                return err_syntax('unexpected format YAML directive', YamlParseToken.raw_token(g.first()))
            value_tk = g.tokens[1]
            value_raw_tk = check.not_none(value_tk.raw_token())
            value0 = value_raw_tk.value
            ver = YAML_VERSION_MAP.get(value0)
            if ver is None:
                return err_syntax(f'unknown YAML version {value0!r}', value_raw_tk)
            if self.yaml_version != '':
                return err_syntax('YAML version has already been specified', value_raw_tk)
            self.yaml_version = ver
            version_node = YamlNodeMakers.new_string_node(ctx, value_tk)
            if isinstance(version_node, YamlError):
                return version_node
            directive.values.append(version_node)
        elif directive.name == 'TAG':
            if len(g.tokens) != 3:
                return err_syntax('unexpected format TAG directive', YamlParseToken.raw_token(g.first()))
            tag_key = YamlNodeMakers.new_string_node(ctx, g.tokens[1])
            if isinstance(tag_key, YamlError):
                return tag_key
            if tag_key.value == '!!':
                self.secondary_tag_directive = directive
            tag_value = YamlNodeMakers.new_string_node(ctx, g.tokens[2])
            if isinstance(tag_value, YamlError):
                return tag_value
            directive.values.extend([tag_key, tag_value])
        elif len(g.tokens) > 1:
            for tk in g.tokens[1:]:
                value1 = YamlNodeMakers.new_string_node(ctx, tk)
                if isinstance(value1, YamlError):
                    return value1
                directive.values.append(value1)
        return directive

    def parse_directive_name(self, ctx: YamlParsingContext) -> YamlErrorOr[ast.DirectiveYamlNode]:
        directive = YamlNodeMakers.new_directive_node(ctx, ctx.current_token())
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
                YamlParseToken.raw_token(ctx.current_token()),
            )
        directive.name = directive_name
        return directive

    def parse_comment(self, ctx: YamlParsingContext) -> YamlErrorOr[ta.Optional[ast.YamlNode]]:
        cm = self.parse_head_comment(ctx)
        if ctx.is_token_not_found():
            return cm
        node = self.parse_token(ctx, ctx.current_token())
        if isinstance(node, YamlError):
            return node
        if (err := set_head_comment(cm, node)) is not None:
            return err
        return node

    def parse_head_comment(self, ctx: YamlParsingContext) -> ta.Optional[ast.CommentGroupYamlNode]:
        tks: ta.List[ta.Optional[YamlToken]] = []
        while ctx.is_comment():
            tks.append(YamlParseToken.raw_token(ctx.current_token()))
            ctx.go_next()
        if len(tks) == 0:
            return None
        return ast.comment_group(tks)

    def parse_foot_comment(self, ctx: YamlParsingContext, col: int) -> ta.Optional[ast.CommentGroupYamlNode]:
        tks: ta.List[ta.Optional[YamlToken]] = []
        while ctx.is_comment() and col <= YamlParseToken.column(ctx.current_token()):
            tks.append(YamlParseToken.raw_token(ctx.current_token()))
            ctx.go_next()
        if len(tks) == 0:
            return None
        return ast.comment_group(tks)
