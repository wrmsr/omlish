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
CommentMap = ta.Dict[str, ta.List[Comment]]


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
    is_valid: bool


##


class YamlDecodeErrors:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    EXCEEDED_MAX_DEPTH = yaml_error('exceeded max depth')


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
                self.anchor_value_map[anchor_name] = YamlValueBox(anchor_value, True)
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

    r"""
    def convert_value(self, v: YamlValueBox, typ: ta.Any, src: YamlNode) -> YamlErrorOr[YamlValueBox]:
        if typ.Kind() != reflect.String:
            if not v.Type().ConvertibleTo(typ):
                # Special case for "strings -> floats" aka scientific notation
                # If the destination type is a float and the source type is a string, check if we can
                # use strconv.ParseFloat to convert the string to a float.
                if (typ.Kind() == reflect.Float32 || typ.Kind() == reflect.Float64) &&
                    v.Type().Kind() == reflect.String:
                    if f, err := strconv.ParseFloat(v.String(), 64); err is None:
                        if typ.Kind() == reflect.Float32:
                            return reflect.ValueOf(float32(f)), nil
                            
                        elif typ.Kind() == reflect.Float64:
                            return reflect.ValueOf(f), nil
                            
                        # else, fall through to the error below
                        
                return reflect.Zero(typ), errors.ErrTypeMismatch(typ, v.Type(), src.get_token())
                
            return v.Convert(typ), nil
            
        # cast value to string
        var strVal str
        switch v.Type().Kind():
        case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
            strVal = strconv.FormatInt(v.Int(), 10)
            
        case reflect.Float32, reflect.Float64:
            strVal = str(v.Float())
            
        case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
            strVal = strconv.FormatUint(v.Uint(), 10)
            
        case reflect.Bool:
            strVal = strconv.FormatBool(v.Bool())
            
        default:
            if not v.Type().ConvertibleTo(typ):
                return reflect.Zero(typ), errors.ErrTypeMismatch(typ, v.Type(), src.get_token())
            return v.Convert(typ), nil

        val := reflect.ValueOf(strVal)
        if val.Type() != typ:
            # Handle named types, e.g., `type MyString string`
            val = val.Convert(typ)
            
        return val, nil

    def delete_struct_keys(self, struct_type: type, unknown_fields: ta.Dict[str, YamlNode]) -> ta.Optional[YamlError]:
        if struct_type.Kind() == reflect.Ptr:
            struct_type = struct_type.Elem()
            
        structFieldMap, err := structFieldMap(struct_type)
        if err is not None:
            return err

        for j := 0; j < struct_type.NumField(); j++:
            field := struct_type.Field(j)
            if isIgnoredStructField(field):
                continue

            structField, exists := structFieldMap[field.Name]
            if not exists:
                continue

            if structField.IsInline:
                _ = self.delete_struct_keys(field.Type, unknown_fields)
            else:
                delete(unknown_fields, structField.RenderName)
        return nil

    def unmarshalable_document(self, node: YamlNode) -> YamlErrorOr[bytes]:
        doc := format.FormatNodeWithResolvedAlias(node, self.anchor_node_map)
        return []byte(doc), nil

    def unmarshalable_text(self, node: YamlNode) -> ta.Tuple[bytes, bool]:
        doc := format.FormatNodeWithResolvedAlias(node, self.anchor_node_map)
        var v str
        if err := Unmarshal([]byte(doc), &v); err is not None:
            return nil, False
        return []byte(v), True

    type JsonUnmarshaler interface {
        UnmarshalJSON([]byte) -> ta.Optional[YamlError]:

    def exists_type_in_custom_unmarshaler_map(self, t: type) -> bool:
        if _, exists := self.custom_unmarshaler_map[t]; exists:
            return True

        globalCustomUnmarshalerMu.Lock()
        defer globalCustomUnmarshalerMu.Unlock()
        if _, exists := globalCustomUnmarshalerMap[t]; exists:
            return True
        return False

    def unmarshaler_from_custom_unmarshaler_map(self, t: type) -> (func(Context, ta.Any, []byte) error, bool):
        if unmarshaler, exists := self.custom_unmarshaler_map[t]; exists:
            return unmarshaler, exists

        globalCustomUnmarshalerMu.Lock()
        defer globalCustomUnmarshalerMu.Unlock()
        if unmarshaler, exists := globalCustomUnmarshalerMap[t]; exists:
            return unmarshaler, exists
        return nil, False

    def can_decode_by_unmarshaler(self, dst: YamlValueBox) -> bool:
        ptrValue := dst.Addr()
        if self.exists_type_in_custom_unmarshaler_map(ptrValue.Type()):
            return True
            
        iface := ptrValue.Interface()
        switch iface.(type):
        case BytesUnmarshalerContext,
            BytesUnmarshaler,
            InterfaceUnmarshalerContext,
            InterfaceUnmarshaler,
            NodeUnmarshaler,
            NodeUnmarshalerContext,
            datetime.datetime,
            *datetime.timedelta,
            encoding.TextUnmarshaler:
            return True
        case JsonUnmarshaler:
            return self.use_json_unmarshaler
        return False

    def decode_by_unmarshaler(self, ctx: Context, dst: YamlValueBox, src: YamlNode) -> ta.Optional[YamlError]:
        ptrValue := dst.Addr()
        if unmarshaler, exists := self.unmarshaler_from_custom_unmarshaler_map(ptrValue.Type()); exists:
            b, err := self.unmarshalable_document(src)
            if err is not None:
                return err
            if err := unmarshaler(ctx, ptrValue.Interface(), b); err is not None:
                return err
            return nil
        iface := ptrValue.Interface()

        if unmarshaler, ok := iface.(BytesUnmarshalerContext); ok:
            b, err := self.unmarshalable_document(src)
            if err is not None:
                return err
            if err := unmarshaler.UnmarshalYAML(ctx, b); err is not None:
                return err
            return nil

        if unmarshaler, ok := iface.(BytesUnmarshaler); ok:
            b, err := self.unmarshalable_document(src)
            if err is not None:
                return err
            if err := unmarshaler.UnmarshalYAML(b); err is not None:
                return err
            return nil

        if unmarshaler, ok := iface.(InterfaceUnmarshalerContext); ok:
            if err := unmarshaler.UnmarshalYAML(ctx, func(v ta.Any) error:
                rv := reflect.ValueOf(v)
                if rv.Type().Kind() != reflect.Ptr:
                    return ErrDecodeRequiredPointerType
                if err := self.decode_value(ctx, rv.Elem(), src); err is not None:
                    return err
                return nil
            }); err is not None:
                return err
            return nil

        if unmarshaler, ok := iface.(InterfaceUnmarshaler); ok:
            if err := unmarshaler.UnmarshalYAML(func(v ta.Any) error:
                rv := reflect.ValueOf(v)
                if rv.Type().Kind() != reflect.Ptr:
                    return ErrDecodeRequiredPointerType
                if err := self.decode_value(ctx, rv.Elem(), src); err is not None:
                    return err
                return nil
            }); err is not None:
                return err
            return nil

        if unmarshaler, ok := iface.(NodeUnmarshaler); ok:
            if err := unmarshaler.UnmarshalYAML(src); err is not None:
                return err

            return nil

        if unmarshaler, ok := iface.(NodeUnmarshalerContext); ok:
            if err := unmarshaler.UnmarshalYAML(ctx, src); err is not None:
                return err

            return nil

        if _, ok := iface.(*datetime.datetime); ok:
            return self.decode_time(ctx, dst, src)

        if _, ok := iface.(*datetime.timedelta); ok:
            return self.decode_duration(ctx, dst, src)

        if unmarshaler, isText := iface.(encoding.TextUnmarshaler); isText:
            b, ok := self.unmarshalable_text(src)
            if ok:
                if err := unmarshaler.UnmarshalText(b); err is not None:
                    return err
                return nil

        if self.use_json_unmarshaler:
            if unmarshaler, ok := iface.(JsonUnmarshaler); ok:
                b, err := self.unmarshalable_document(src)
                if err is not None:
                    return err
                jsonBytes, err := YAMLToJSON(b)
                if err is not None:
                    return err
                jsonBytes = bytes.TrimRight(jsonBytes, "\n")
                if err := unmarshaler.UnmarshalJSON(jsonBytes); err is not None:
                    return err
                return nil

        return errors.New("does not implemented Unmarshaler")

    astNodeType = reflect.TypeOf((*YamlNode)(nil)).Elem()

    def decode_value(self, ctx: Context, dst: YamlValueBox, src: YamlNode) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH
            if not dst.is_value:
                return None

            if src.type() == YamlNodeType.ANCHOR:
                anchor, _ := src.(AnchorYamlNode)
                anchor_name := anchor.Name.get_token().Value
                if err := self.decode_value(with_anchor(ctx, anchor_name), dst, anchor.Value); err is not None:
                    return err
                self.anchor_value_map[anchor_name] = dst
                return nil
                
            if self.can_decode_by_unmarshaler(dst):
                if err := self.decode_by_unmarshaler(ctx, dst, src); err is not None:
                    return err
                return nil
                
            value_type := dst.Type()
            switch value_type.Kind():
            case reflect.Ptr:
                if dst.IsNil():
                    return nil
                    
                if src.Type() == YamlNodeType.NULL:
                    # set nil value to pointer
                    dst.Set(reflect.Zero(value_type))
                    return nil
                    
                v := self.create_decodable_value(dst.Type())
                if err := self.decode_value(ctx, v, src); err is not None:
                    return err
                    
                castedValue, err := self.cast_to_assignable_value(v, dst.Type(), src)
                if err is not None:
                    return err
                    
                dst.Set(castedValue)
                
            case reflect.Interface:
                if dst.Type() == astNodeType:
                    dst.Set(reflect.ValueOf(src))
                    return nil
                    
                srcVal, err := self.node_to_value(ctx, src)
                if err is not None:
                    return err
                    
                v := reflect.ValueOf(srcVal)
                if v.IsValid():
                    dst.Set(v)
                else:
                    dst.Set(reflect.Zero(value_type))
                    
            case reflect.Map:
                return self.decode_map(ctx, dst, src)
                
            case reflect.Array:
                return self.decode_array(ctx, dst, src)
                
            case reflect.Slice:
                if map_slice, ok := dst.Addr().Interface().(*MapSlice); ok:
                    return self.decode_map_slice(ctx, map_slice, src)
                return self.decode_slice(ctx, dst, src)
                
            case reflect.Struct:
                if mapItem, ok := dst.Addr().Interface().(*MapItem); ok:
                    return self.decode_map_item(ctx, mapItem, src)
                return self.decode_struct(ctx, dst, src)
                
            case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
                v, err := self.node_to_value(ctx, src)
                if err is not None:
                    return err
                switch vv := v.(type):
                case int64:
                    if not dst.OverflowInt(vv):
                        dst.SetInt(vv)
                        return nil
                case uint64:
                    if vv <= math.MaxInt64 && !dst.OverflowInt(int64(vv)):
                        dst.SetInt(int64(vv))
                        return nil
                case float64:
                    if vv <= math.MaxInt64 && !dst.OverflowInt(int64(vv)):
                        dst.SetInt(int64(vv))
                        return nil
                case str: # handle scientific notation
                    if i, err := strconv.ParseFloat(vv, 64); err is None:
                        if 0 <= i && i <= math.MaxUint64 && !dst.OverflowInt(int64(i)):
                            dst.SetInt(int64(i))
                            return nil
                    else { # couldn't be parsed as float
                        return errors.ErrTypeMismatch(value_type, reflect.TypeOf(v), src.get_token())
                default:
                    return errors.ErrTypeMismatch(value_type, reflect.TypeOf(v), src.get_token())
                return errors.ErrOverflow(value_type, str(v), src.get_token())
                
            case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
                v, err := self.node_to_value(ctx, src)
                if err is not None:
                    return err
                switch vv := v.(type):
                case int64:
                    if 0 <= vv && !dst.OverflowUint(uint64(vv)):
                        dst.SetUint(uint64(vv))
                        return nil
                case uint64:
                    if not dst.OverflowUint(vv):
                        dst.SetUint(vv)
                        return nil
                case float64:
                    if 0 <= vv && vv <= math.MaxUint64 && !dst.OverflowUint(uint64(vv)):
                        dst.SetUint(uint64(vv))
                        return nil
                case str: # handle scientific notation
                    if i, err := strconv.ParseFloat(vv, 64); err is None:
                        if 0 <= i && i <= math.MaxUint64 && !dst.OverflowUint(uint64(i)):
                            dst.SetUint(uint64(i))
                            return nil
                    else { # couldn't be parsed as float
                        return errors.ErrTypeMismatch(value_type, reflect.TypeOf(v), src.get_token())

                default:
                    return errors.ErrTypeMismatch(value_type, reflect.TypeOf(v), src.get_token())
                return errors.ErrOverflow(value_type, str(v), src.get_token())
                
            srcVal, err := self.node_to_value(ctx, src)
            if err is not None:
                return err
                
            v := reflect.ValueOf(srcVal)
            if v.IsValid():
                convertedValue, err := self.convert_value(v, dst.Type(), src)
                if err is not None:
                    return err
                dst.Set(convertedValue)
                
            return nil
        
        finally:
            self.step_out()

    def create_decodable_value(self, typ: type) -> YamlValueBox:
        while True:
            if typ.Kind() == reflect.Ptr:
                typ = typ.Elem()
                continue
            break
        return reflect.New(typ).Elem()

    def cast_to_assignable_value(self, value: ta.Any, target: type, src: YamlNode) -> YamlErrorOr[ta.Any]:
        if target.Kind() != reflect.Ptr:
            if not value.Type().AssignableTo(target):
                return reflect.Value{}, errors.ErrTypeMismatch(target, value.Type(), src.get_token())
            return value, nil

        max_addr_count = 5

        for i := 0; i < maxAddrCount; i++:
            if value.Type().AssignableTo(target):
                break
            if not value.CanAddr():
                break
            value = value.Addr()
        if not value.Type().AssignableTo(target):
            return reflect.Value{}, errors.ErrTypeMismatch(target, value.Type(), src.get_token())
        return value, nil

    def create_decoded_new_value(
        self,
        ctx: Context,
        typ: type,
        default_val: ta.Any,
        node: YamlNode,
    ) -> YamlErrorOr[ta.Any]:
        if node.Type() == YamlNodeType.ALIAS:
            alias_name := node.(AliasYamlNode).Value.get_token().Value
            value := self.anchor_value_map[alias_name]
            if value.IsValid():
                v, err := self.cast_to_assignable_value(value, typ, node)
                if err is None:
                    return v, nil
            anchor, exists := self.anchor_node_map[alias_name]
            if exists:
                node = anchor
                
        var new_value reflect.Value
        if node.Type() == YamlNodeType.NULL:
            new_value = reflect.New(typ).Elem()
        else:
            new_value = self.create_decodable_value(typ)
            
        for default_val.Kind() == reflect.Ptr:
            default_val = default_val.Elem()
            
        if default_val.IsValid() && default_val.Type().AssignableTo(new_value.Type()):
            new_value.Set(default_val)
            
        if node.Type() != YamlNodeType.NULL:
            if err := self.decode_value(ctx, new_value, node); err is not None:
                return reflect.Value{}, err

        return self.cast_to_assignable_value(new_value, typ, node)

    def key_to_node_map(
        self,
        ctx: Context,
        node: YamlNode,
        ignore_merge_key: bool,
        get_key_or_value_node: func(*ast.MapNodeIter) YamlNode,
    ) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            map_node, err := self.get_map_node(node, False)
            if err is not None:
                return nil, err
            key_map: ta.Dict[str, None] {}
            key_to_node_map: ta.Dict[str, YamlNode] = {}
            map_iter := map_node.map_range()
            for map_iter.Next():
                key_node := map_iter.Key()
                if key_node.is_merge_key():
                    if ignore_merge_key:
                        continue
                    mergeMap, err := self.key_to_node_map(ctx, map_iter.Value(), ignore_merge_key, get_key_or_value_node)
                    if err is not None:
                        return nil, err
                    for k, v := range mergeMap:
                        if err := self.validate_duplicate_key(key_map, k, v); err is not None:
                            return nil, err
                        key_to_node_map[k] = v
                else:
                    keyVal, err := self.node_to_value(ctx, key_node)
                    if err is not None:
                        return nil, err
                    key, ok := keyVal.(str)
                    if not ok:
                        return nil, err
                    if err := self.validate_duplicate_key(key_map, key, key_node); err is not None:
                        return nil, err
                    key_to_node_map[key] = get_key_or_value_node(map_iter)
            return key_to_node_map, nil
        
        finally:
            self.step_out()

    def key_to_key_node_map(self, ctx: Context, node: YamlNode, ignore_merge_key: bool) -> YamlOrError[ta.Dict[str, YamlNode]]:
        m, err := self.key_to_node_map(ctx, node, ignore_merge_key, func(nodeMap *ast.MapNodeIter) YamlNode { return nodeMap.Key() })
        if err is not None:
            return nil, err
        return m, nil

    def key_to_value_node_map(self, ctx: Context, node: YamlNode, ignore_merge_key: bool) -> YamlErrorOr[ta.Dict[str, YamlNode]]:
        m, err := self.key_to_node_map(ctx, node, ignore_merge_key, func(nodeMap *ast.MapNodeIter) YamlNode { return nodeMap.Value() })
        if err is not None:
            return nil, err
        return m, nil

    def set_default_value_if_conflicted(self, v: ta.Any, field_map: StructFieldMap) -> ta.Optional[YamlError]:
        for v.Type().Kind() == reflect.Ptr:
            v = v.Elem()
        typ := v.Type()
        if typ.Kind() != reflect.Struct:
            return nil
        embeddedStructFieldMap, err := structFieldMap(typ)
        if err is not None:
            return err
        for i := 0; i < typ.NumField(); i++:
            field := typ.Field(i)
            if isIgnoredStructField(field):
                continue
            structField := embeddedStructFieldMap[field.Name]
            if not field_map.isIncludedRenderName(structField.RenderName):
                continue
            # if declared same key name, set default value
            field_value := v.Field(i)
            if field_value.CanSet():
                field_value.Set(reflect.Zero(field_value.Type()))
        return nil

    # This is a subset of the formats allowed by the regular expression
    # defined at http:#yaml.org/type/timestamp.html.
    ALLOWED_TIMESTAMP_FORMATS = []str{
        "2006-1-2T15:4:5.999999999Z07:00", # RCF3339Nano with short date fields.
        "2006-1-2t15:4:5.999999999Z07:00", # RFC3339Nano with short date fields and lower-case "t".
        "2006-1-2 15:4:5.999999999",       # space separated with no time zone
        "2006-1-2",                        # date only
    }

    def cast_to_time(self, ctx: Context, src: YamlNode) -> YamlErrorOr[datetime.datetime]:
        if src is None:
            return datetime.datetime{}, nil
        v, err := self.node_to_value(ctx, src)
        if err is not None:
            return datetime.datetime{}, err
        if t, ok := v.(datetime.datetime); ok:
            return t, nil
        s, ok := v.(str)
        if not ok:
            return datetime.datetime{}, errors.ErrTypeMismatch(reflect.TypeOf(datetime.datetime{}), reflect.TypeOf(v), src.get_token())
        for _, format := range ALLOWED_TIMESTAMP_FORMATS:
            t, err := time.Parse(format, s)
            if err is not None:
                # invalid format
                continue
            return t, nil
        return datetime.datetime{}, nil

    def decode_time(self, ctx: Context, dst: YamlValueBox, src: YamlNode) -> ta.Optional[YamlError]:
        t, err := self.cast_to_time(ctx, src)
        if err is not None:
            return err
        dst.Set(reflect.ValueOf(t))
        return nil

    def cast_to_duration(self, ctx: Context, src: YamlNode) -> YamlErrorOr[datetime.timedelta]:
        if src is None:
            return 0, nil
        v, err := self.node_to_value(ctx, src)
        if err is not None:
            return 0, err
        if t, ok := v.(datetime.timedelta); ok:
            return t, nil
        s, ok := v.(str)
        if not ok:
            return 0, errors.ErrTypeMismatch(reflect.TypeOf(datetime.timedelta(0)), reflect.TypeOf(v), src.get_token())
        t, err := time.ParseDuration(s)
        if err is not None:
            return 0, err
        return t, nil

    def decode_duration(self, ctx: Context, dst: YamlValueBox, src: YamlNode) -> ta.Optional[YamlError]:
        t, err := self.cast_to_duration(ctx, src)
        if err is not None:
            return err
        dst.Set(reflect.ValueOf(t))
        return nil

    # get_merge_alias_name support single alias only
    def get_merge_alias_name(self, src: YamlNode) -> str:
        map_node, err := self.get_map_node(src, True)
        if err is not None:
            return ""
        map_iter := map_node.map_range()
        for map_iter.Next():
            key := map_iter.Key()
            value := map_iter.Value()
            if key.is_merge_key() && value.Type() == YamlNodeType.ALIAS:
                return value.(AliasYamlNode).Value.get_token().Value
        return ""

    def decode_struct(self, ctx: Context, dst: YamlValueBox, src: YamlNode) -> ta.Optional[YamlError]:
        if src is None:
            return nil
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            struct_type := dst.Type()
            src_value := reflect.ValueOf(src)
            src_type := src_value.Type()
            if src_type.Kind() == reflect.Ptr:
                src_type = src_type.Elem()
                src_value = src_value.Elem()
            if struct_type == src_type:
                # dst value implements YamlNode
                dst.Set(src_value)
                return nil
            structFieldMap, err := structFieldMap(struct_type)
            if err is not None:
                return err
            ignore_merge_key := structFieldMap.hasMergeProperty()
            key_to_node_map, err := self.key_to_value_node_map(ctx, src, ignore_merge_key)
            if err is not None:
                return err
            unknown_fields: ta.Dict[str, YamlNode]
            if self.disallow_unknown_field:
                unknown_fields, err = self.key_to_key_node_map(ctx, src, ignore_merge_key)
                if err is not None:
                    return err

            alias_name := self.get_merge_alias_name(src)
            var found_err error

            for i := 0; i < struct_type.NumField(); i++:
                field := struct_type.Field(i)
                if isIgnoredStructField(field):
                    continue
                structField := structFieldMap[field.Name]
                if structField.IsInline:
                    field_value := dst.FieldByName(field.Name)
                    if structField.IsAutoAlias:
                        if alias_name != "":
                            newFieldValue := self.anchor_value_map[alias_name]
                            if newFieldValue.IsValid():
                                value, err := self.cast_to_assignable_value(
                                    newFieldValue,
                                    field_value.Type(),
                                    self.anchor_node_map[alias_name],
                                )
                                if err is not None:
                                    return err
                                field_value.Set(value)
                        continue
                    if not field_value.CanSet():
                        return fmt.Errorf("cannot set embedded type as unexported field %s.%s", field.PkgPath, field.Name)
                    if field_value.Type().Kind() == reflect.Ptr && src.Type() == YamlNodeType.NULL:
                        # set nil value to pointer
                        field_value.Set(reflect.Zero(field_value.Type()))
                        continue
                    map_node := ast.Mapping(nil, False)
                    for k, v := range key_to_node_map:
                        key := StringYamlNode{BaseNode: BaseYamlNode, Value: k}
                        map_node.Values = append(map_node.Values, ast.MappingValue(nil, key, v))
                    newFieldValue, err := self.create_decoded_new_value(ctx, field_value.Type(), field_value, map_node)
                    if self.disallow_unknown_field:
                        if err := self.delete_struct_keys(field_value.Type(), unknown_fields); err is not None:
                            return err

                    if err is not None:
                        if found_err is not None:
                            continue
                        var te *errors.TypeError
                        if errors.As(err, &te):
                            if te.StructFieldName is not None:
                                fieldName := fmt.Sprintf("%s.%s", struct_type.Name(), *te.StructFieldName)
                                te.StructFieldName = &fieldName
                            else:
                                fieldName := fmt.Sprintf("%s.%s", struct_type.Name(), field.Name)
                                te.StructFieldName = &fieldName
                            found_err = te
                            continue
                        else:
                            found_err = err
                        continue
                    _ = self.set_default_value_if_conflicted(newFieldValue, structFieldMap)
                    field_value.Set(newFieldValue)
                    continue
                v, exists := key_to_node_map[structField.RenderName]
                if not exists:
                    continue
                delete(unknown_fields, structField.RenderName)
                field_value := dst.FieldByName(field.Name)
                if field_value.Type().Kind() == reflect.Ptr && src.Type() == YamlNodeType.NULL:
                    # set nil value to pointer
                    field_value.Set(reflect.Zero(field_value.Type()))
                    continue
                newFieldValue, err := self.create_decoded_new_value(ctx, field_value.Type(), field_value, v)
                if err is not None:
                    if found_err is not None:
                        continue
                    var te *errors.TypeError
                    if errors.As(err, &te):
                        fieldName := fmt.Sprintf("%s.%s", struct_type.Name(), field.Name)
                        te.StructFieldName = &fieldName
                        found_err = te
                    else:
                        found_err = err
                    continue
                field_value.Set(newFieldValue)
            if found_err is not None:
                return found_err

            # Ignore unknown fields when parsing an inline struct (recognized by a nil token).
            # Unknown fields are expected (they could be fields from the parent struct).
            if len(unknown_fields) != 0 && self.disallow_unknown_field && src.get_token() is not None:
                for key, node := range unknown_fields:
                    var ok bool
                    for _, prefix := range self.allowed_field_prefixes:
                        if strings.HasPrefix(key, prefix):
                            ok = True
                            break
                    if not ok:
                        return errors.ErrUnknownField(fmt.Sprintf(`unknown field "%s"`, key), node.get_token())

            if self.validator is not None:
                if err := self.validator.Struct(dst.Interface()); err is not None:
                    ev := reflect.ValueOf(err)
                    if ev.Type().Kind() == reflect.Slice:
                        for i := 0; i < ev.Len(); i++:
                            fieldErr, ok := ev.Index(i).Interface().(FieldError)
                            if not ok:
                                continue
                            fieldName := fieldErr.StructField()
                            structField, exists := structFieldMap[fieldName]
                            if not exists:
                                continue
                            node, exists := key_to_node_map[structField.RenderName]
                            if exists:
                                # TODO: to make FieldError message cutomizable
                                return errors.ErrSyntax(
                                    fmt.Sprintf("%s", err),
                                    self.get_parent_map_token_if_exists_for_validation_error(node.Type(), node.get_token()),
                                )
                            elif t := src.get_token(); t != nil && t.Prev != nil && t.Prev.Prev is not None:
                                # A missing required field will not be in the key_to_node_map
                                # the error needs to be associated with the parent of the source node
                                return errors.ErrSyntax(fmt.Sprintf("%s", err), t.Prev.Prev)
                    return err
            return nil
        
        finally:
            self.step_out()
    """ # noqa

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

    r"""
    def decode_array(self, ctx: Context, dst: YamlValueBox, src: YamlNode) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            array_node, err := self.get_array_node(src)
            if err is not None:
                return err
            if array_node is None:
                return nil
            it := array_node.ArrayRange()
            array_value := reflect.New(dst.Type()).Elem()
            array_type := dst.Type()
            elem_type := array_type.Elem()
            idx := 0

            var found_err error
            for it.Next():
                v := it.Value()
                if elem_type.Kind() == reflect.Ptr && v.Type() == YamlNodeType.NULL:
                    # set nil value to pointer
                    array_value.Index(idx).Set(reflect.Zero(elem_type))
                else:
                    dst_value, err := self.create_decoded_new_value(ctx, elem_type, reflect.Value{}, v)
                    if err is not None:
                        if found_err is None:
                            found_err = err
                        continue
                    array_value.Index(idx).Set(dst_value)
                idx++
            dst.Set(array_value)
            if found_err is not None:
                return found_err
            return nil
        
        finally:
            self.step_out()

    def decode_slice(self, ctx: Context, dst: YamlValueBox, src: YamlNode) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            array_node, err := self.get_array_node(src)
            if err is not None:
                return err
            if array_node is None:
                return nil
            it := array_node.ArrayRange()
            slice_type := dst.Type()
            slice_value := reflect.MakeSlice(slice_type, 0, it.Len())
            elem_type := slice_type.Elem()

            var found_err error
            for it.Next():
                v := it.Value()
                if elem_type.Kind() == reflect.Ptr && v.Type() == YamlNodeType.NULL:
                    # set nil value to pointer
                    slice_value = reflect.Append(slice_value, reflect.Zero(elem_type))
                    continue
                dst_value, err := self.create_decoded_new_value(ctx, elem_type, reflect.Value{}, v)
                if err is not None:
                    if found_err is None:
                        found_err = err
                    continue
                slice_value = reflect.Append(slice_value, dst_value)
            dst.Set(slice_value)
            if found_err is not None:
                return found_err
            return nil
        
        finally:
            self.step_out

    def decode_map_item(self, ctx: Context, dst: MapItem, src: YamlNode) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            map_node, err := self.get_map_node(src, is_merge(ctx))
            if err is not None:
                return err
            map_iter := map_node.map_range()
            if not map_iter.Next():
                return nil
            key := map_iter.Key()
            value := map_iter.Value()
            if key.is_merge_key():
                if err := self.decode_map_item(with_merge(ctx), dst, value); err is not None:
                    return err
                return nil
            k, err := self.node_to_value(ctx, key)
            if err is not None:
                return err
            v, err := self.node_to_value(ctx, value)
            if err is not None:
                return err
            *dst = MapItem{Key: k, Value: v}
            return nil
        
        finally:
            self.step_out()

    def validate_duplicate_key(self, key_map: ta.Dict[str, None], key: ta.Any, key_node: YamlNode) -> ta.Optional[YamlError]:
        if not isinstance(k := key, str):
            return None
        if not self.allow_duplicate_map_key:
            if _, exists := key_map[k]; exists:
                return errors.ErrDuplicateKey(fmt.Sprintf(`duplicate key "%s"`, k), key_node.get_token())
        key_map[k] = struct{}{}
        return nil

    def decode_map_slice(self, ctx: Context, dst: MapSlice, src: YamlNode) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            map_node, err := self.get_map_node(src, is_merge(ctx))
            if err is not None:
                return err
            map_slice := MapSlice{}
            map_iter := map_node.map_range()
            key_map: ta.Dict[str, None] = {}
            for map_iter.Next():
                key := map_iter.Key()
                value := map_iter.Value()
                if key.is_merge_key():
                    var m MapSlice
                    if err := self.decode_map_slice(with_merge(ctx), &m, value); err is not None:
                        return err
                    for _, v := range m:
                        if err := self.validate_duplicate_key(key_map, v.Key, value); err is not None:
                            return err
                        map_slice = append(map_slice, v)
                    continue
                k, err := self.node_to_value(ctx, key)
                if err is not None:
                    return err
                if err := self.validate_duplicate_key(key_map, k, key); err is not None:
                    return err
                v, err := self.node_to_value(ctx, value)
                if err is not None:
                    return err
                map_slice = append(map_slice, MapItem{Key: k, Value: v})
            *dst = map_slice
            return nil
        
        finally:
            self.step_out()

    def decode_map(self, ctx: Context, dst: YamlValueBox, src: YamlNode) -> ta.Optional[YamlError]:
        self.step_in()
        try:
            if self.is_exceeded_max_depth():
                return YamlDecodeErrors.EXCEEDED_MAX_DEPTH

            map_node, err := self.get_map_node(src, is_merge(ctx))
            if err is not None:
                return err
            map_type := dst.Type()
            map_value := reflect.MakeMap(map_type)
            key_type := map_value.Type().Key()
            value_type := map_value.Type().Elem()
            map_iter := map_node.map_range()
            key_map: ta.Dict[str, None] = {}
            var found_err error
            for map_iter.Next():
                key := map_iter.Key()
                value := map_iter.Value()
                if key.is_merge_key():
                    if err := self.decode_map(with_merge(ctx), dst, value); err is not None:
                        return err
                    it := dst.map_range()
                    for it.Next():
                        if err := self.validate_duplicate_key(key_map, it.Key(), value); err is not None:
                            return err
                        map_value.SetMapIndex(it.Key(), it.Value())
                    continue

                k := self.create_decodable_value(key_type)
                if self.can_decode_by_unmarshaler(k):
                    if err := self.decode_by_unmarshaler(ctx, k, key); err is not None:
                        return err
                else:
                    keyVal, err := self.create_decoded_new_value(ctx, key_type, reflect.Value{}, key)
                    if err is not None:
                        return err
                    k = keyVal

                if k.IsValid():
                    if err := self.validate_duplicate_key(key_map, k.Interface(), key); err is not None:
                        return err
                if value_type.Kind() == reflect.Ptr && value.Type() == YamlNodeType.NULL:
                    # set nil value to pointer
                    map_value.SetMapIndex(k, reflect.Zero(value_type))
                    continue
                dst_value, err := self.create_decoded_new_value(ctx, value_type, reflect.Value{}, value)
                if err is not None:
                    if found_err is None:
                        found_err = err
                if not k.IsValid():
                    # expect nil key
                    map_value.SetMapIndex(self.create_decodable_value(key_type), dst_value)
                    continue
                if key_type.Kind() != k.Kind():
                    return errors.ErrSyntax(
                        fmt.Sprintf("cannot convert %q type to %q type", k.Kind(), key_type.Kind()),
                        key.get_token(),
                    )
                map_value.SetMapIndex(k, dst_value)
            dst.Set(map_value)
            if found_err is not None:
                return found_err
            return nil
        
        finally:
            self.step_out()
    """  # noqa

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
            check.not_none(self.to_comment_map).clear()
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

    r"""
    def _decode(self, ctx: Context, v: ta.Any) -> ta.Optional[YamlError]:
        self.decode_depth = 0
        self.anchor_value_map = {}
        if len(self.parsed_file.docs) == 0:
            # empty document.
            dst := v.Elem()
            if dst.IsValid():
                dst.Set(reflect.Zero(dst.Type()))
        if len(self.parsed_file.docs) <= self.stream_index:
            return io.EOF
        body := self.parsed_file.docs[self.stream_index].Body
        if body is None:
            return nil
        if len(self.comment_maps) > self.stream_index:
            maps.Copy(self.to_comment_map, self.comment_maps[self.stream_index])
        if err := self.decode_value(ctx, v.Elem(), body); err is not None:
            return err
        self.stream_index++
        return nil

    # Decode reads the next YAML-encoded value from its input
    # and stores it in the value pointed to by v.
    #
    # See the documentation for Unmarshal for details about the
    # conversion of YAML into a Go value.
    def decode(self, v: ta.Any) -> ta.Optional[YamlError]:
        return self.decode_context(context.Background(), v)

    # decode_context reads the next YAML-encoded value from its input
    # and stores it in the value pointed to by v with Context.
    def decode_context(self, ctx: Context, v: ta.Any) -> ta.Optional[YamlError]:
        rv := reflect.ValueOf(v)
        if not rv.IsValid() || rv.Type().Kind() != reflect.Ptr:
            return ErrDecodeRequiredPointerType
        if self.is_initialized():
            if err := self._decode(ctx, rv); err is not None:
                return err
            return nil
        if err := self.decode_init(ctx); err is not None:
            return err
        if err := self._decode(ctx, rv); err is not None:
            return err
        return nil

    # decode_from_node decodes node into the value pointed to by v.
    def decode_from_nodel(self, node: YamlNode, v: ta.Any) -> ta.Optional[YamlError]:
        return self.decode_from_node_context(context.Background(), node, v)

    # decode_from_node_context decodes node into the value pointed to by v with Context.
    def decode_from_node_context(self, ctx: Context, node: YamlNode, v: ta.Any) -> ta.Optional[YamlError]:
        rv := reflect.ValueOf(v)
        if rv.Type().Kind() != reflect.Ptr:
            return ErrDecodeRequiredPointerType
        if not self.is_initialized():
            if err := self.decode_init(ctx); err is not None:
                return err
        # resolve references to the anchor on the same file
        if _, err := self.node_to_value(ctx, node); err is not None:
            return err
        if err := self.decode_value(ctx, rv.Elem(), node); err is not None:
            return err
        return nil
    """  # noqa
