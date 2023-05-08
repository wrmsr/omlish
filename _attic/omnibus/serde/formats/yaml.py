"""
TODO:
 - yaml.g4? yeesh
  - just a simplified one?
 - !! shared 'object format' node hierarchy
  - fuse yaml and hocon - marks, *COMMENTS*, etc
 - goal: perfect rewrites (comments, whitespace)
  - or at least comments
 - rename 'objects'? codecs/serde interplay still unresolved
 - just fuckin vendor?
"""
import datetime
import types
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import properties

if ta.TYPE_CHECKING:
    import yaml
    import yaml.nodes as yaml_nodes
else:
    yaml = lang.proxy_import('yaml')
    yaml_nodes = lang.proxy_import('yaml.nodes')


T = ta.TypeVar('T')


class NodeWrapped(dc.Data, ta.Generic[T], final=True, frozen=True):
    value: T
    node: 'yaml_nodes.Node'

    def __post_init__(self) -> None:
        if isinstance(self.value, NodeWrapped):
            raise TypeError(self.value)
        if not isinstance(self.node, yaml_nodes.Node):
            raise TypeError(self.node)


class NodeUnwrapper:

    seq_types = (
        list,
        set,
        tuple,
    )

    def unwrap_seq(self, nw: NodeWrapped[T]) -> T:
        return type(nw.value)(map(self.unwrap, nw.value))

    map_types = (
        dict,
    )

    def unwrap_map(self, nw: NodeWrapped[T]) -> T:
        return type(nw.value)({self.unwrap(k): self.unwrap(v) for k, v in nw.value.items()})

    scalar_types = (
        bool,
        bytes,
        datetime.datetime,
        float,
        int,
        str,
        type(None),
    )

    def unwrap_scalar(self, nw: NodeWrapped[T]) -> T:
        return nw.value

    def unwrap_unknown(self, nw: NodeWrapped[T]) -> T:
        raise TypeError(nw.value)

    def unwrap(self, nw: NodeWrapped[T]) -> T:
        check.isinstance(nw, NodeWrapped)
        if isinstance(nw.value, self.seq_types):
            return self.unwrap_seq(nw)
        elif isinstance(nw.value, self.map_types):
            return self.unwrap_map(nw)
        elif isinstance(nw.value, self.scalar_types):
            return self.unwrap_scalar(nw)
        else:
            return self.unwrap_unknown(nw)


def unwrap(nw: NodeWrapped[T]) -> T:
    return NodeUnwrapper().unwrap(nw)


class NodeWrappingConstructorMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ctors = {fn.__name__: fn for fn in [
            type(self).construct_yaml_omap,
            type(self).construct_yaml_pairs,
        ]}
        self.yaml_constructors = {
            tag: ctors.get(ctor.__name__, ctor)
            for tag, ctor in self.yaml_constructors.items()
        }

    def construct_object(self, node, deep=False):
        value = super().construct_object(node, deep=deep)
        return NodeWrapped(value, node)

    def __construct_yaml_pairs(self, node, fn):
        omap = []
        gen = check.isinstance(fn(node), types.GeneratorType)
        yield omap
        uomap = next(gen)
        lang.exhaust(gen)
        for key, value in uomap:
            omap.append(NodeWrapped((key, value), node))

    def construct_yaml_omap(self, node):
        return self.__construct_yaml_pairs(node, super().construct_yaml_omap)

    def construct_yaml_pairs(self, node):
        return self.__construct_yaml_pairs(node, super().construct_yaml_pairs)


class WrappedLoaders(lang.Namespace):

    @staticmethod
    def _wrap(cls):
        return type('NodeWrapping$' + cls.__name__, (NodeWrappingConstructorMixin, cls), {})

    @properties.cached_class
    def Base(cls) -> ta.Type['yaml.BaseLoader']:
        return cls._wrap(yaml.BaseLoader)

    @classmethod
    def base(cls, *args, **kwargs) -> 'yaml.BaseLoader':
        return cls.Base(*args, **kwargs)

    @properties.cached_class
    def Full(cls) -> ta.Type['yaml.FullLoader']:
        return cls._wrap(yaml.FullLoader)

    @classmethod
    def full(cls, *args, **kwargs) -> 'yaml.FullLoader':
        return cls.Full(*args, **kwargs)

    @properties.cached_class
    def Safe(cls) -> ta.Type['yaml.SafeLoader']:
        return cls._wrap(yaml.SafeLoader)

    @classmethod
    def safe(cls, *args, **kwargs) -> 'yaml.SafeLoader':
        return cls.Safe(*args, **kwargs)

    @properties.cached_class
    def Unsafe(cls) -> ta.Type['yaml.UnsafeLoader']:
        return cls._wrap(yaml.UnsafeLoader)

    @classmethod
    def unsafe(cls, *args, **kwargs) -> 'yaml.UnsafeLoader':
        return cls.Unsafe(*args, **kwargs)

    @properties.cached_class
    def CBase(cls) -> ta.Type['yaml.CBaseLoader']:
        return cls._wrap(yaml.CBaseLoader)

    @classmethod
    def cbase(cls, *args, **kwargs) -> 'yaml.CBaseLoader':
        return cls.CBase(*args, **kwargs)

    @properties.cached_class
    def CFull(cls) -> ta.Type['yaml.CFullLoader']:
        return cls._wrap(yaml.CFullLoader)

    @classmethod
    def cfull(cls, *args, **kwargs) -> 'yaml.CFullLoader':
        return cls.CFull(*args, **kwargs)

    @properties.cached_class
    def CSafe(cls) -> ta.Type['yaml.CSafeLoader']:
        return cls._wrap(yaml.CSafeLoader)

    @classmethod
    def csafe(cls, *args, **kwargs) -> 'yaml.CSafeLoader':
        return cls.CSafe(*args, **kwargs)

    @properties.cached_class
    def CUnsafe(cls) -> ta.Type['yaml.CUnsafeLoader']:
        return cls._wrap(yaml.CUnsafeLoader)

    @classmethod
    def cunsafe(cls, *args, **kwargs) -> 'yaml.CUnsafeLoader':
        return cls.CUnsafe(*args, **kwargs)


def load(stream, Loader):
    with lang.disposing(Loader(stream)) as loader:
        return loader.get_single_data()


def load_all(stream, Loader):
    with lang.disposing(Loader(stream)) as loader:
        while loader.check_data():
            yield loader.get_data()


def full_load(stream):
    return load(stream, yaml.FullLoader)


def full_load_all(stream):
    return load_all(stream, yaml.FullLoader)
