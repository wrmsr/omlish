"""
TODO:
 - !! shared 'object format' node hierarchy
  - fuse yaml and hocon - marks, *COMMENTS*, etc
 - goal: perfect rewrites (comments, whitespace)
  - or at least comments
 - rename 'objects'? codecs/serde interplay still unresolved
 - look ma, a monad
"""
import datetime
import types
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang


if ta.TYPE_CHECKING:
    import yaml
    import yaml.nodes as yaml_nodes
else:
    yaml = lang.proxy_import('yaml')
    yaml_nodes = lang.proxy_import('yaml.nodes')


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class NodeWrapped(lang.Final, ta.Generic[T]):
    value: T
    node: 'yaml_nodes.Node'

    def __post_init__(self) -> None:
        if isinstance(self.value, NodeWrapped):
            raise TypeError(self.value)
        if not isinstance(self.node, yaml_nodes.Node):
            raise TypeError(self.node)


class NodeUnwrapper:

    seq_types: tuple[type, ...] = (
        list,
        set,
        tuple,
    )

    def unwrap_seq(self, nw: NodeWrapped[T]) -> T:
        return nw.value.__class__(map(self.unwrap, nw.value))  # type: ignore

    map_types: tuple[type, ...] = (
        dict,
    )

    def unwrap_map(self, nw: NodeWrapped[T]) -> T:
        return nw.value.__class__({self.unwrap(k): self.unwrap(v) for k, v in nw.value.items()})  # type: ignore

    scalar_types: tuple[type, ...] = (
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

        ctors = {
            fn.__name__: fn for fn in [
                self.__class__.construct_yaml_omap,
                self.__class__.construct_yaml_pairs,
            ]
        }
        self.yaml_constructors = {
            tag: ctors.get(ctor.__name__, ctor)
            for tag, ctor in self.yaml_constructors.items()  # type: ignore  # noqa
        }

    def construct_object(self, node, deep=False):
        value = super().construct_object(node, deep=deep)  # type: ignore
        return NodeWrapped(value, node)

    def __construct_yaml_pairs(self, node, fn):
        omap = []  # type: ignore
        gen = check.isinstance(fn(node), types.GeneratorType)
        yield omap
        uomap = next(gen)
        lang.exhaust(gen)
        for key, value in uomap:
            omap.append(NodeWrapped((key, value), node))

    def construct_yaml_omap(self, node):
        return self.__construct_yaml_pairs(node, super().construct_yaml_omap)  # type: ignore  # noqa

    def construct_yaml_pairs(self, node):
        return self.__construct_yaml_pairs(node, super().construct_yaml_pairs)  # type: ignore  # noqa


##


class _cached_class_property:  # noqa
    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._attr = None

    def __call__(self, *args, **kwargs):
        raise TypeError

    def __set_name__(self, owner, name):
        self._attr = '_' + name

    def __get__(self, instance, owner=None):
        if owner is None:
            if instance is None:
                raise RuntimeError
            owner = instance.__class__
        try:
            return owner.__dict__[self._attr]
        except KeyError:
            ret = self._fn(owner)
            setattr(owner, self._attr, ret)  # type: ignore
            return ret


class WrappedLoaders(lang.Namespace):

    @staticmethod
    def _wrap(cls):  # noqa
        return type('NodeWrapping$' + cls.__name__, (NodeWrappingConstructorMixin, cls), {})

    Base: type['yaml.BaseLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.BaseLoader))  # type: ignore

    @classmethod
    def base(cls, *args, **kwargs) -> 'yaml.BaseLoader':
        return cls.Base(*args, **kwargs)

    Full: type['yaml.FullLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.FullLoader))  # type: ignore

    @classmethod
    def full(cls, *args, **kwargs) -> 'yaml.FullLoader':
        return cls.Full(*args, **kwargs)

    Safe: type['yaml.SafeLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.SafeLoader))  # type: ignore

    @classmethod
    def safe(cls, *args, **kwargs) -> 'yaml.SafeLoader':
        return cls.Safe(*args, **kwargs)

    Unsafe: type['yaml.UnsafeLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.UnsafeLoader))  # type: ignore

    @classmethod
    def unsafe(cls, *args, **kwargs) -> 'yaml.UnsafeLoader':
        return cls.Unsafe(*args, **kwargs)

    CBase: type['yaml.CBaseLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.CBaseLoader))  # type: ignore

    @classmethod
    def cbase(cls, *args, **kwargs) -> 'yaml.CBaseLoader':
        return cls.CBase(*args, **kwargs)

    CFull: type['yaml.CFullLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.CFullLoader))  # type: ignore

    @classmethod
    def cfull(cls, *args, **kwargs) -> 'yaml.CFullLoader':
        return cls.CFull(*args, **kwargs)

    CSafe: type['yaml.CSafeLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.CSafeLoader))  # type: ignore

    @classmethod
    def csafe(cls, *args, **kwargs) -> 'yaml.CSafeLoader':
        return cls.CSafe(*args, **kwargs)

    CUnsafe: type['yaml.CUnsafeLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.CUnsafeLoader))  # type: ignore  # noqa

    @classmethod
    def cunsafe(cls, *args, **kwargs) -> 'yaml.CUnsafeLoader':
        return cls.CUnsafe(*args, **kwargs)


##


def load(stream, Loader):  # noqa
    with lang.disposing(Loader(stream)) as loader:
        return loader.get_single_data()


def load_all(stream, Loader):  # noqa
    with lang.disposing(Loader(stream)) as loader:
        while loader.check_data():
            yield loader.get_data()


def safe_load(stream):  # noqa
    return load(stream, yaml.SafeLoader)


def safe_load_all(stream):  # noqa  # noqa
    return load_all(stream, yaml.SafeLoader)


def full_load(stream):  # noqa
    return load(stream, yaml.FullLoader)


def full_load_all(stream):  # noqa  # noqa
    return load_all(stream, yaml.FullLoader)
