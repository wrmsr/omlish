# ruff: noqa: UP006 UP007 UP043 UP045
# @omlish-lite
import base64
import dataclasses as dc
import datetime
import enum
import glob
import os.path
import typing as ta

from omlish.lite.check import check

from .ast import AliasYamlNode  # noqa
from .ast import AnchorYamlNode
from .ast import ArrayYamlNode  # noqa
from .ast import BaseYamlNode  # noqa
from .ast import BoolYamlNode  # noqa
from .ast import CommentGroupYamlNode  # noqa
from .ast import FloatYamlNode  # noqa
from .ast import InfinityYamlNode  # noqa
from .ast import IntegerYamlNode  # noqa
from .ast import LiteralYamlNode  # noqa
from .ast import MapKeyYamlNode
from .ast import MappingKeyYamlNode  # noqa
from .ast import MappingValueYamlNode
from .ast import MappingYamlNode
from .ast import MapYamlNode
from .ast import MapYamlNodeIter  # noqa
from .ast import NanYamlNode  # noqa
from .ast import NullYamlNode  # noqa
from .ast import SequenceYamlNode  # noqa
from .ast import StringYamlNode  # noqa
from .ast import TagYamlNode  # noqa
from .ast import UnexpectedNodeTypeYamlError
from .ast import YamlFile
from .ast import YamlNode
from .ast import YamlNodeType  # noqa
from .ast import yaml_sequence_merge_value  # noqa
from .errors import EofYamlError
from .errors import YamlError
from .errors import YamlErrorOr
from .errors import yaml_error
from .parsing import YAML_PARSE_COMMENTS  # noqa
from .parsing import YamlOption
from .parsing import YamlParseMode  # noqa
from .parsing import yaml_allow_duplicate_map_key  # noqa
from .parsing import yaml_parse_str  # noqa
from .tokens import YamlReservedTagKeywords  # noqa
from .tokens import YamlSyntaxError  # noqa
from .tokens import YamlToken  # noqa


##


class Context:
    def __init__(self, values: ta.Optional[ta.Dict[ta.Any, ta.Any]] = None) -> None:
        super().__init__()

        self._values: ta.Dict[ta.Any, ta.Any] = values if values is not None else {}

    def with_value(self, key: ta.Any, value: ta.Any) -> 'Context':
        return Context({**self._values, key: value})

    def value(self, key: ta.Any) -> ta.Any:
        return self._values.get(key)


class CTX_MERGE_KEY:  # noqa
    pass


class CTX_ANCHOR_KEY:  # noqa
    pass


def with_merge(ctx: Context) -> Context:
    return ctx.with_value(CTX_MERGE_KEY, True)


def is_merge(ctx: Context) -> bool:
    if not isinstance(v := ctx.value(CTX_MERGE_KEY), bool):
        return False

    return v


def with_anchor(ctx: Context, name: str) -> Context:
    anchor_map = get_anchor_map(ctx)
    new_map: ta.Dict[str, None] = {}
    new_map.update(anchor_map)
    new_map[name] = None
    return ctx.with_value(CTX_ANCHOR_KEY, new_map)


def get_anchor_map(ctx: Context) -> ta.Dict[str, None]:
    if not isinstance(v := ctx.value(CTX_ANCHOR_KEY), dict):
        return {}

    return v


##


# CommentPosition type of the position for comment.
class CommentPosition(enum.IntEnum):
    HEAD = 0
    LINE = 1
    FOOT = 2


# Comment raw data for comment.
@dc.dataclass()
class Comment:
    texts: ta.List[str]
    position: CommentPosition


# LineComment create a one-line comment for CommentMap.
def line_comment(text: str) -> Comment:
    return Comment(
        texts=[text],
        position=CommentPosition.LINE,
    )


# HeadComment create a multiline comment for CommentMap.
def head_comment(*texts: str) -> Comment:
    return Comment(
        texts=list(texts),
        position=CommentPosition.HEAD,
    )


# FootComment create a multiline comment for CommentMap.
def foot_comment(*texts: str) -> Comment:
    return Comment(
        texts=list(texts),
        position=CommentPosition.FOOT,
    )


# CommentMap map of the position of the comment and the comment information.
class CommentMap(ta.Dict[str, ta.List[Comment]]):
    pass


##


# MapItem is an item in a MapSlice.
@dc.dataclass()
class MapItem:
    key: ta.Any
    value: ta.Any


# MapSlice encodes and decodes as a YAML map.
# The order of keys is preserved when encoding and decoding.
class MapSlice(ta.List[MapItem]):
    # ToMap convert to map[interface{}]interface{}.
    def to_map(self) -> ta.Dict[ta.Any, ta.Any]:
        return {item.key: item.value for item in self}


##


class Reader(ta.Protocol):
    def read(self) -> bytes: ...


class ImmediateBytesReader:
    def __init__(self, bs: bytes) -> None:
        self._bs = bs

    def read(self) -> bytes:
        bs = self._bs
        self._bs = b''
        return bs


##


class DecodeOption(ta.Protocol):
    def __call__(self, d: 'YamlDecoder') -> ta.Optional[YamlError]: ...


# StructValidator need to implement Struct method only
# ( see https://pkg.go.dev/github.com/go-playground/validator/v10#Validate.Struct )
class StructValidator(ta.Protocol):
    def struct(self, v: ta.Any) -> ta.Optional[YamlError]: ...


# FieldError need to implement StructField method only
# ( see https://pkg.go.dev/github.com/go-playground/validator/v10#FieldError )
class FieldError:
    def struct_field(self) -> str:
        raise NotImplementedError


##


@dc.dataclass()
class YamlValueBox:
    v: ta.Any
    is_valid: bool = True
    ty: ta.Optional[type] = None

    @classmethod
    def new_invalid(cls) -> 'YamlValueBox':
        return YamlValueBox(None, False)


##


class YamlDecodeErrors:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    EXCEEDED_MAX_DEPTH = yaml_error('exceeded max depth')


@dc.dataclass(frozen=True)
class DuplicateKeyYamlError(YamlError):
    msg: str
    token: YamlToken

    @property
    def message(self) -> str:
        return self.msg

##


# Decoder reads and decodes YAML values from an input stream.
class YamlDecoder:
    reader: Reader
    reference_readers: ta.List[Reader]
    anchor_node_map: ta.Dict[str, ta.Optional[YamlNode]]
    anchor_value_map: ta.Dict[str, YamlValueBox]
    custom_unmarshaler_map: ta.Dict[type, ta.Callable[[Context, ta.Any, bytes], ta.Optional[YamlError]]]
    comment_maps: ta.List[CommentMap]
    to_comment_map: ta.Optional[CommentMap] = None
    opts: ta.List[DecodeOption]
    reference_files: ta.List[str]
    reference_dirs: ta.List[str]
    is_recursive_dir: bool = False
    is_resolved_reference: bool = False
    validator: ta.Optional[StructValidator] = None
    disallow_unknown_field: bool = False
    allowed_field_prefixes: ta.List[str]
    allow_duplicate_map_key: bool = False
    use_ordered_map: bool = False
    use_json_unmarshaler: bool = False
    parsed_file: ta.Optional[YamlFile] = None
    stream_index: int = 0
    decode_depth: int = 0

    # NewDecoder returns a new decoder that reads from r.
    def __init__(self, r: Reader, *opts: DecodeOption) -> None:
        super().__init__()

        self.reader = r
        self.anchor_node_map = {}
        self.anchor_value_map = {}
        self.custom_unmarshaler_map = {}
        self.opts = list(opts)
        self.reference_readers = []
        self.reference_files = []
        self.reference_dirs = []
        self.is_recursive_dir = False
        self.is_resolved_reference = False
        self.disallow_unknown_field = False
        self.allow_duplicate_map_key = False
        self.use_ordered_map = False

        self.comment_maps = []

    MAX_DECODE_DEPTH: ta.ClassVar[int] = 10000

    def step_in(self) -> None:
        self.decode_depth += 1

    def step_out(self) -> None:
        self.decode_depth -= 1

    def is_exceeded_max_depth(self) -> bool:
        return self.decode_depth > self.MAX_DECODE_DEPTH

    def cast_to_float(self, v: ta.Any) -> ta.Any:
        if isinstance(v, float):
            return v
        elif isinstance(v, int):
            return float(v)
        elif isinstance(v, str):
            # if error occurred, return zero value
            try:
                return float(v)
            except ValueError:
                return 0
        return 0

    def map_key_node_to_string(self, ctx: Context, node: MapKeyYamlNode) -> YamlErrorOr[str]:
        key = self.node_to_value(ctx, node)
        if isinstance(key, YamlError):
            return key
        if key is None:
            return 'null'
        if isinstance(key, str):
            return key
        return str(key)

    def set_to_map_value(self, ctx: Context, node: YamlNode, m: ta.Dict[str, ta.Any]) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            self.set_path_comment_map(node)
            if isinstance(n := node, MappingValueYamlNode):
                if n.key.is_merge_key():
                    value = self.get_map_node(n.value, True)
                    if isinstance(value, YamlError):
                        return value

                    it = value.map_range()
                    while it.next():
                        if (err := self.set_to_map_value(ctx, it.key_value(), m)) is not None:
                            return err

                else:
                    key = self.map_key_node_to_string(ctx, n.key)
                    if isinstance(key, YamlError):
                        return key

                    v = self.node_to_value(ctx, n.value)
                    if isinstance(v, YamlError):
                        return v

                    m[key] = v

            elif isinstance(n, MappingYamlNode):
                for value2 in n.values:
                    if (err := self.set_to_map_value(ctx, value2, m)) is not None:
                        return err

            elif isinstance(n, AnchorYamlNode):
                anchor_name = check.not_none(check.not_none(n.name).get_token()).value
                self.anchor_node_map[anchor_name] = n.value

            return None

        finally:
            self.step_out()

    def set_to_ordered_map_value(self, ctx: Context, node: YamlNode, m: MapSlice) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            self.set_path_comment_map(node)
            if isinstance(n := node, MappingValueYamlNode):
                if n.key.is_merge_key():
                    value = self.get_map_node(n.value, True)
                    if isinstance(value, YamlError):
                        return value

                    it = value.map_range()
                    while it.next():
                        if (err := self.set_to_ordered_map_value(ctx, it.key_value(), m)) is not None:
                            return err

                else:
                    key = self.map_key_node_to_string(ctx, n.key)
                    if isinstance(key, YamlError):
                        return key

                    value = self.node_to_value(ctx, n.value)
                    if isinstance(value, YamlError):
                        return value

                    m.append(MapItem(key, value))

            elif isinstance(n, MappingYamlNode):
                for value2 in n.values:
                    if (err := self.set_to_ordered_map_value(ctx, value2, m)) is not None:
                        return err

            return None

        finally:
            self.step_out()

    def set_path_comment_map(self, node: ta.Optional[YamlNode]) -> None:
        if node is None:
            return

        if self.to_comment_map is None:
            return

        self.add_head_or_line_comment_to_map(node)
        self.add_foot_comment_to_map(node)

    def add_head_or_line_comment_to_map(self, node: YamlNode) -> None:
        if isinstance(node, SequenceYamlNode):
            self.add_sequence_node_comment_to_map(node)
            return

        comment_group = node.get_comment()
        if comment_group is None:
            return

        texts: ta.List[str] = []
        target_line = check.not_none(node.get_token()).position.line
        min_comment_line = 1_000_000_000  # FIXME lol
        for comment in comment_group.comments:
            if min_comment_line > check.not_none(comment.token).position.line:
                min_comment_line = check.not_none(comment.token).position.line

            texts.append(check.not_none(comment.token).value)

        if len(texts) == 0:
            return

        comment_path = node.get_path()
        if min_comment_line < target_line:
            if isinstance(n := node, MappingYamlNode):
                if len(n.values) != 0:
                    comment_path = n.values[0].key.get_path()

            elif isinstance(n, MappingValueYamlNode):
                comment_path = n.key.get_path()

            self.add_comment_to_map(comment_path, head_comment(*texts))
        else:
            self.add_comment_to_map(comment_path, line_comment(texts[0]))

    def add_sequence_node_comment_to_map(self, node: SequenceYamlNode) -> None:
        if len(node.value_head_comments) != 0:
            for idx, hc in enumerate(node.value_head_comments):
                if hc is None:
                    continue

                texts: ta.List[str] = []
                for comment in hc.comments:
                    texts.append(check.not_none(comment.token).value)

                if len(texts) != 0:
                    self.add_comment_to_map(check.not_none(node.values[idx]).get_path(), head_comment(*texts))

        first_elem_head_comment = node.get_comment()
        if first_elem_head_comment is not None:
            texts = []
            for comment in first_elem_head_comment.comments:
                texts.append(check.not_none(comment.token).value)

            if len(texts) != 0:
                if len(node.values) != 0:
                    self.add_comment_to_map(check.not_none(node.values[0]).get_path(), head_comment(*texts))

    def add_foot_comment_to_map(self, node: YamlNode) -> None:
        fc: ta.Optional[CommentGroupYamlNode] = None
        foot_comment_path = node.get_path()

        if isinstance(n := node, SequenceYamlNode):
            fc = n.foot_comment
            if n.foot_comment is not None:
                foot_comment_path = n.foot_comment.get_path()

        elif isinstance(n, MappingYamlNode):
            fc = n.foot_comment
            if n.foot_comment is not None:
                foot_comment_path = n.foot_comment.get_path()

        elif isinstance(n, MappingValueYamlNode):
            fc = n.foot_comment
            if n.foot_comment is not None:
                foot_comment_path = n.foot_comment.get_path()

        if fc is None:
            return

        texts: ta.List[str] = []
        for comment in fc.comments:
            texts.append(check.not_none(comment.token).value)

        if len(texts) != 0:
            self.add_comment_to_map(foot_comment_path, foot_comment(*texts))

    def add_comment_to_map(self, path: str, comment: Comment) -> None:
        tcm = check.not_none(self.to_comment_map)[path]
        for c in tcm:
            if c.position == comment.position:
                # already added same comment
                return

        tcm.append(comment)
        tcm.sort(key=lambda c: c.position)

    def node_to_value(self, ctx: Context, node: YamlNode) -> YamlErrorOr[ta.Any]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            self.set_path_comment_map(node)

            if isinstance(n := node, NullYamlNode):
                return None

            elif isinstance(n, StringYamlNode):
                return n.get_value()

            elif isinstance(n, IntegerYamlNode):
                return n.get_value()

            elif isinstance(n, FloatYamlNode):
                return n.get_value()

            elif isinstance(n, BoolYamlNode):
                return n.get_value()

            elif isinstance(n, InfinityYamlNode):
                return n.get_value()

            elif isinstance(n, NanYamlNode):
                return n.get_value()

            elif isinstance(n, TagYamlNode):
                if n.directive is not None:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    if v is None:
                        return ''

                    return str(v)

                rtk = n.start.value
                if rtk == YamlReservedTagKeywords.TIMESTAMP:
                    t = self.cast_to_time(ctx, check.not_none(n.value))
                    if isinstance(t, YamlError):
                        return None
                    return t

                elif rtk == YamlReservedTagKeywords.INTEGER:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    try:
                        return int(str(v))
                    except ValueError:
                        return 0

                elif rtk == YamlReservedTagKeywords.FLOAT:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    return self.cast_to_float(v)

                elif rtk == YamlReservedTagKeywords.NULL:
                    return None

                elif rtk == YamlReservedTagKeywords.BINARY:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    if not isinstance(v, str):
                        return YamlSyntaxError(
                            f'cannot convert {str(v)!r} to string',
                            check.not_none(check.not_none(n.value).get_token()),
                        )
                    try:
                        return base64.b64decode(v)
                    except ValueError:
                        return None

                elif rtk == YamlReservedTagKeywords.BOOLEAN:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    l = str(v).lower()
                    if l in ('true', 't', '1', 'yes'):
                        return True
                    if l in ('false', 'f', '0', 'no'):
                        return False
                    return YamlSyntaxError(
                        f'cannot convert {v!r} to boolean',
                        check.not_none(check.not_none(n.value).get_token()),
                    )

                elif rtk == YamlReservedTagKeywords.STRING:
                    v = self.node_to_value(ctx, check.not_none(n.value))
                    if isinstance(v, YamlError):
                        return v
                    if v is None:
                        return ''
                    return str(v)

                elif rtk == YamlReservedTagKeywords.MAPPING:
                    return self.node_to_value(ctx, check.not_none(n.value))

                else:
                    return self.node_to_value(ctx, check.not_none(n.value))

            elif isinstance(n, AnchorYamlNode):
                anchor_name = check.not_none(check.not_none(n.name).get_token()).value

                # To handle the case where alias is processed recursively, the result of alias can be set to nil in
                # advance.
                self.anchor_node_map[anchor_name] = None
                anchor_value = self.node_to_value(with_anchor(ctx, anchor_name), check.not_none(n.value))
                if isinstance(anchor_value, YamlError):
                    del self.anchor_node_map[anchor_name]
                    return anchor_value
                self.anchor_node_map[anchor_name] = n.value
                self.anchor_value_map[anchor_name] = YamlValueBox(anchor_value)
                return anchor_value

            elif isinstance(n, AliasYamlNode):
                text = check.not_none(n.value).string()
                if text in get_anchor_map(ctx):
                    # self recursion.
                    return None
                try:
                    v = self.anchor_value_map[text]
                except KeyError:
                    pass
                else:
                    if not v.is_valid:
                        return None
                    return v.v
                try:
                    node2 = self.anchor_node_map[text]
                except KeyError:
                    pass
                else:
                    return self.node_to_value(ctx, check.not_none(node2))
                return YamlSyntaxError(
                    f'could not find alias {text!r}',
                    check.not_none(check.not_none(n.value).get_token()),
                )

            elif isinstance(n, LiteralYamlNode):
                return check.not_none(n.value).get_value()

            elif isinstance(n, MappingKeyYamlNode):
                return self.node_to_value(ctx, check.not_none(n.value))

            elif isinstance(n, MappingValueYamlNode):
                if n.key.is_merge_key():
                    value = self.get_map_node(check.not_none(n.value), True)
                    if isinstance(value, YamlError):
                        return value
                    it = value.map_range()
                    if self.use_ordered_map:
                        m = MapSlice()
                        while it.next():
                            if (err := self.set_to_ordered_map_value(ctx, it.key_value(), m)) is not None:
                                return err
                        return m
                    m2: ta.Dict[str, ta.Any] = {}
                    while it.next():
                        if (err := self.set_to_map_value(ctx, it.key_value(), m2)) is not None:
                            return err
                    return m2

                key = self.map_key_node_to_string(ctx, n.key)
                if isinstance(key, YamlError):
                    return key

                if self.use_ordered_map:
                    v = self.node_to_value(ctx, n.value)
                    if isinstance(v, YamlError):
                        return v
                    return MapSlice([MapItem(key, v)])

                v = self.node_to_value(ctx, n.value)
                if isinstance(v, YamlError):
                    return v

                return {key: v}

            elif isinstance(n, MappingYamlNode):
                if self.use_ordered_map:
                    m3 = MapSlice()
                    for value2 in n.values:
                        if (err := self.set_to_ordered_map_value(ctx, value2, m3)) is not None:
                            return err
                    return m3

                m4: ta.Dict[str, ta.Any] = {}
                for value3 in n.values:
                    if (err := self.set_to_map_value(ctx, value3, m4)) is not None:
                        return err
                return m4

            elif isinstance(n, SequenceYamlNode):
                v2: ta.List[ta.Any] = []
                for value4 in n.values:
                    vv = self.node_to_value(ctx, check.not_none(value4))
                    if isinstance(vv, YamlError):
                        return vv
                    v2.append(vv)
                return v2

            return None

        finally:
            self.step_out()

    def cast_to_time(self, ctx: Context, src: YamlNode) -> YamlErrorOr[datetime.datetime]:
        raise NotImplementedError

    def get_map_node(self, node: YamlNode, is_merge: bool) -> YamlErrorOr[MapYamlNode]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            if isinstance(n := node, MapYamlNode):
                return n

            elif isinstance(n, AnchorYamlNode):
                anchor_name = check.not_none(check.not_none(n.name).get_token()).value
                self.anchor_node_map[anchor_name] = n.value
                return self.get_map_node(check.not_none(n.value), is_merge)

            elif isinstance(n, AliasYamlNode):
                alias_name = check.not_none(check.not_none(n.value).get_token()).value
                node2 = self.anchor_node_map[alias_name]
                if node2 is None:
                    return yaml_error(f'cannot find anchor by alias name {alias_name}')
                return self.get_map_node(node2, is_merge)

            elif isinstance(n, SequenceYamlNode):
                if not is_merge:
                    return UnexpectedNodeTypeYamlError(node.type(), YamlNodeType.MAPPING, check.not_none(node.get_token()))  # noqa
                map_nodes: ta.List[MapYamlNode] = []
                for value in n.values:
                    map_node = self.get_map_node(check.not_none(value), False)
                    if isinstance(map_node, YamlError):
                        return map_node
                    map_nodes.append(map_node)
                return yaml_sequence_merge_value(*map_nodes)

            return UnexpectedNodeTypeYamlError(node.type(), YamlNodeType.MAPPING, check.not_none(node.get_token()))

        finally:
            self.step_out()

    def get_array_node(self, node: YamlNode) -> YamlErrorOr[ta.Optional[ArrayYamlNode]]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            if isinstance(node, NullYamlNode):
                return None

            if isinstance(anchor := node, AnchorYamlNode):
                if isinstance(array_node := anchor.value, ArrayYamlNode):
                    return array_node

                return UnexpectedNodeTypeYamlError(check.not_none(anchor.value).type(), YamlNodeType.SEQUENCE, check.not_none(node.get_token()))  # noqa

            if isinstance(alias := node, AliasYamlNode):
                alias_name = check.not_none(check.not_none(alias.value).get_token()).value
                node2 = self.anchor_node_map[alias_name]
                if node2 is None:
                    return yaml_error(f'cannot find anchor by alias name {alias_name}')
                if isinstance(array_node := node2, ArrayYamlNode):
                    return array_node
                return UnexpectedNodeTypeYamlError(node2.type(), YamlNodeType.SEQUENCE, check.not_none(node2.get_token()))  # noqa

            if not isinstance(array_node := node, ArrayYamlNode):
                return UnexpectedNodeTypeYamlError(node.type(), YamlNodeType.SEQUENCE, check.not_none(node.get_token()))  # noqa

            return array_node

        finally:
            self.step_out()

    def decode_value(self, ctx: Context, dst: YamlValueBox, src: YamlNode) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH
            if not dst.is_valid:
                return None

            if src.type() == YamlNodeType.ANCHOR:
                anchor = check.isinstance(src, AnchorYamlNode)
                anchor_name = check.not_none(check.not_none(anchor.name).get_token()).value
                if (err := self.decode_value(with_anchor(ctx, anchor_name), dst, check.not_none(anchor.value))) is not None:  # noqa
                    return err
                self.anchor_value_map[anchor_name] = dst
                return None

            value_type = dst.ty

            if value_type == YamlNode:
                dst.v = src
                return None

            elif value_type is None or value_type is ta.Any:
                src_val = self.node_to_value(ctx, src)
                if isinstance(src_val, YamlError):
                    return src_val

                dst.v = src_val
                return None

            else:
                raise NotImplementedError

        finally:
            self.step_out()

    def key_to_node_map(
        self,
        ctx: Context,
        node: YamlNode,
        ignore_merge_key: bool,
        get_key_or_value_node: ta.Callable[[MapYamlNodeIter], YamlNode],
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            map_node = self.get_map_node(node, False)
            if isinstance(map_node, YamlError):
                return map_node
            key_map: ta.Dict[str, None] = {}
            key_to_node_map: ta.Dict[str, YamlNode] = {}
            map_iter = map_node.map_range()
            while map_iter.next():
                key_node = map_iter.key()
                if key_node.is_merge_key():
                    if ignore_merge_key:
                        continue
                    merge_map = self.key_to_node_map(ctx, map_iter.value(), ignore_merge_key, get_key_or_value_node)
                    if isinstance(merge_map, YamlError):
                        return merge_map
                    for k, v in merge_map.items():
                        if (err := self.validate_duplicate_key(key_map, k, v)) is not None:
                            return err
                        key_to_node_map[k] = v
                else:
                    key_val = self.node_to_value(ctx, key_node)
                    if isinstance(key_val, YamlError):
                        return key_val
                    if not isinstance(key := key_val, str):
                        return yaml_error('???')
                    if (err := self.validate_duplicate_key(key_map, key, key_node)) is not None:
                        return err
                    key_to_node_map[key] = get_key_or_value_node(map_iter)
            return key_to_node_map

        finally:
            self.step_out()

    def key_to_key_node_map(
        self,
        ctx: Context,
        node: YamlNode,
        ignore_merge_key: bool,
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        m = self.key_to_node_map(ctx, node, ignore_merge_key, lambda node_map: node_map.key())
        if isinstance(m, YamlError):
            return m
        return m

    def key_to_value_node_map(
        self,
        ctx: Context,
        node: YamlNode,
        ignore_merge_key: bool,
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        m = self.key_to_node_map(ctx, node, ignore_merge_key, lambda node_map: node_map.value())
        if isinstance(m, YamlError):
            return m
        return m

    # getParentMapTokenIfExists if the NodeType is a container type such as MappingType or SequenceType,
    # it is necessary to return the parent MapNode's colon token to represent the entire container.
    def get_parent_map_token_if_exists_for_validation_error(self, typ: YamlNodeType, tk: ta.Optional[YamlToken]) -> ta.Optional[YamlToken]:  # noqa
        if tk is None:
            return None
        if typ == YamlNodeType.MAPPING:
            # map:
            #   key: value
            #      ^ current token ( colon )
            if tk.prev is None:
                return tk
            key = tk.prev
            if key.prev is None:
                return tk
            return key.prev
        if typ == YamlNodeType.SEQUENCE:
            # map:
            #   - value
            #   ^ current token ( sequence entry )
            if tk.prev is None:
                return tk
            return tk.prev
        return tk

    def validate_duplicate_key(self, key_map: ta.Dict[str, None], key: ta.Any, key_node: YamlNode) -> ta.Optional[YamlError]:  # noqa
        if not isinstance(k := key, str):
            return None
        if not self.allow_duplicate_map_key:
            if k in key_map:
                return DuplicateKeyYamlError(f'duplicate key "{k}"', check.not_none(key_node.get_token()))
        key_map[k] = None
        return None

    def file_to_reader(self, file: str) -> YamlErrorOr[Reader]:
        with open(file, 'rb') as f:
            bs = f.read()
        return ImmediateBytesReader(bs)

    def is_yaml_file(self, file: str) -> bool:
        ext = file.rsplit('.', maxsplit=1)[-1]
        if ext == '.yml':
            return True
        if ext == '.yaml':
            return True
        return False

    def readers_under_dir(self, d: str) -> YamlErrorOr[ta.List[Reader]]:
        pattern = f'{d}/*'
        matches = glob.glob(pattern)
        readers: ta.List[Reader] = []
        for match in matches:
            if not self.is_yaml_file(match):
                continue
            if isinstance(reader := self.file_to_reader(match), YamlError):
                return reader
            readers.append(reader)
        return readers

    def readers_under_dir_recursive(self, d: str) -> YamlErrorOr[ta.List[Reader]]:
        readers: ta.List[Reader] = []
        for dp, _, fns in os.walk(d):
            for fn in fns:
                path = os.path.join(dp, fn)
                if not os.path.isfile(path):
                    continue
                if not self.is_yaml_file(path):
                    continue
                if isinstance(reader := self.file_to_reader(path), YamlError):
                    return reader
                readers.append(reader)
        return readers

    def resolve_reference(self, ctx: Context) -> ta.Optional[YamlError]:
        for opt in self.opts:
            if (err := opt(self)) is not None:
                return err
        for file in self.reference_files:
            if isinstance(reader := self.file_to_reader(file), YamlError):
                return reader
            self.reference_readers.append(reader)
        for d in self.reference_dirs:
            if not self.is_recursive_dir:
                if isinstance(readers := self.readers_under_dir(d), YamlError):
                    return readers
                self.reference_readers.extend(readers)
            else:
                if isinstance(readers := self.readers_under_dir_recursive(d), YamlError):
                    return readers
                self.reference_readers.extend(readers)
        for reader in self.reference_readers:
            bs = reader.read()
            # assign new anchor definition to anchorMap
            if isinstance(err2 := self.parse(ctx, bs), YamlError):
                return err2
        self.is_resolved_reference = True
        return None

    def parse(self, ctx: Context, bs: bytes) -> YamlErrorOr[YamlFile]:
        parse_mode: YamlParseMode = 0
        if self.to_comment_map is not None:
            parse_mode |= YAML_PARSE_COMMENTS
        opts: ta.List[YamlOption] = []
        if self.allow_duplicate_map_key:
            opts.append(yaml_allow_duplicate_map_key())
        if isinstance(f := yaml_parse_str(bs.decode(), parse_mode, *opts), YamlError):
            return f
        normalized_file = YamlFile()
        for doc in f.docs:
            # try to decode YamlNode to value and map anchor value to anchorMap
            if isinstance(v := self.node_to_value(ctx, check.not_none(doc.body)), YamlError):
                return v
            if v is not None or (doc.body is not None and doc.body.type() == YamlNodeType.NULL):
                normalized_file.docs.append(doc)
                cm = CommentMap()
                cm.update(self.to_comment_map or {})
                self.comment_maps.append(cm)
            if self.to_comment_map is not None:
                self.to_comment_map.clear()
        return normalized_file

    def is_initialized(self) -> bool:
        return self.parsed_file is not None

    def decode_init(self, ctx: Context) -> ta.Optional[YamlError]:
        if not self.is_resolved_reference:
            if (err := self.resolve_reference(ctx)) is not None:
                return err
        buf = self.reader.read()
        if isinstance(file := self.parse(ctx, buf), YamlError):
            return file
        self.parsed_file = file
        return None

    def _decode(self, ctx: Context, v: YamlValueBox) -> ta.Optional[YamlError]:
        self.decode_depth = 0
        self.anchor_value_map = {}
        pf = check.not_none(self.parsed_file)
        if len(pf.docs) == 0:
            # empty document.
            # dst := v.Elem()
            # if dst.IsValid():
            #     dst.Set(reflect.Zero(dst.Type()))
            v.v = None
        if len(pf.docs) <= self.stream_index:
            return EofYamlError()
        body = pf.docs[self.stream_index].body
        if body is None:
            return None
        if len(self.comment_maps) > self.stream_index:
            if (scm := self.comment_maps[self.stream_index]):
                check.not_none(self.to_comment_map).update(scm)
        if (err := self.decode_value(ctx, v, body)) is not None:
            return err
        self.stream_index += 1
        return None

    # Decode reads the next YAML-encoded value from its input
    # and stores it in the value pointed to by v.
    #
    # See the documentation for Unmarshal for details about the
    # conversion of YAML into a Go value.
    def decode(self) -> YamlErrorOr[YamlValueBox]:
        return self.decode_context(Context())

    # decode_context reads the next YAML-encoded value from its input
    # and stores it in the value pointed to by v with Context.
    def decode_context(self, ctx: Context) -> YamlErrorOr[YamlValueBox]:
        rv = YamlValueBox(None)
        # if not rv.IsValid() || rv.Type().Kind() != reflect.Ptr:
        #     return ErrDecodeRequiredPointerType
        if self.is_initialized():
            if (err := self._decode(ctx, rv)) is not None:
                return err
            return rv
        if (err := self.decode_init(ctx)) is not None:
            return err
        if (err := self._decode(ctx, rv)) is not None:
            return err
        return rv

    # decode_from_node decodes node into the value pointed to by v.
    def decode_from_node(self, node: YamlNode) -> YamlErrorOr[YamlValueBox]:
        return self.decode_from_node_context(Context(), node)

    # decode_from_node_context decodes node into the value pointed to by v with Context.
    def decode_from_node_context(self, ctx: Context, node: YamlNode) -> YamlErrorOr[YamlValueBox]:
        rv = YamlValueBox(None)
        # if rv.Type().Kind() != reflect.Ptr:
        #     return ErrDecodeRequiredPointerType
        if not self.is_initialized():
            if (err := self.decode_init(ctx)) is not None:
                return err
        # resolve references to the anchor on the same file
        if (err := self.node_to_value(ctx, node)) is not None:
            return err
        if (err := self.decode_value(ctx, rv, node)) is not None:
            return err
        return rv
