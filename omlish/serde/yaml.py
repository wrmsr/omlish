# """
# TODO:
#  - !! shared 'object format' node hierarchy
#   - fuse yaml and hocon - marks, *COMMENTS*, etc
#  - goal: perfect rewrites (comments, whitespace)
#   - or at least comments
#  - rename 'objects'? codecs/serde interplay still unresolved
# """
# import datetime
# import types
# import typing as ta
#
# from .. import check
# from .. import dataclasses as dc
# from .. import lang
#
# if ta.TYPE_CHECKING:
#     import yaml
#     import yaml.nodes as yaml_nodes
# else:
#     yaml = lang.proxy_import('yaml')
#     yaml_nodes = lang.proxy_import('yaml.nodes')
#
#
# T = ta.TypeVar('T')
#
#
# class NodeWrapped(dc.Data, ta.Generic[T], final=True, frozen=True):
#     value: T
#     node: 'yaml_nodes.Node'
#
#     def __post_init__(self) -> None:
#         if isinstance(self.value, NodeWrapped):
#             raise TypeError(self.value)
#         if not isinstance(self.node, yaml_nodes.Node):
#             raise TypeError(self.node)
#
#
# class NodeUnwrapper:
#
#     seq_types = (
#         list,
#         set,
#         tuple,
#     )
#
#     def unwrap_seq(self, nw: NodeWrapped[T]) -> T:
#         return type(nw.value)(map(self.unwrap, nw.value))
#
#     map_types = (
#         dict,
#     )
#
#     def unwrap_map(self, nw: NodeWrapped[T]) -> T:
#         return type(nw.value)({self.unwrap(k): self.unwrap(v) for k, v in nw.value.items()})
#
#     scalar_types = (
#         bool,
#         bytes,
#         datetime.datetime,
#         float,
#         int,
#         str,
#         type(None),
#     )
#
#     def unwrap_scalar(self, nw: NodeWrapped[T]) -> T:
#         return nw.value
#
#     def unwrap_unknown(self, nw: NodeWrapped[T]) -> T:
#         raise TypeError(nw.value)
#
#     def unwrap(self, nw: NodeWrapped[T]) -> T:
#         check.isinstance(nw, NodeWrapped)
#         if isinstance(nw.value, self.seq_types):
#             return self.unwrap_seq(nw)
#         elif isinstance(nw.value, self.map_types):
#             return self.unwrap_map(nw)
#         elif isinstance(nw.value, self.scalar_types):
#             return self.unwrap_scalar(nw)
#         else:
#             return self.unwrap_unknown(nw)
#
#
# def unwrap(nw: NodeWrapped[T]) -> T:
#     return NodeUnwrapper().unwrap(nw)
#
#
# class NodeWrappingConstructorMixin:
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         ctors = {
#             fn.__name__: fn for fn in [
#                 type(self).construct_yaml_omap,
#                 type(self).construct_yaml_pairs,
#             ]
#         }
#         self.yaml_constructors = {
#             tag: ctors.get(ctor.__name__, ctor)
#             for tag, ctor in self.yaml_constructors.items()  # noqa
#         }
#
#     def construct_object(self, node, deep=False):
#         value = super().construct_object(node, deep=deep)  # noqa
#         return NodeWrapped(value, node)
#
#     def __construct_yaml_pairs(self, node, fn):
#         omap = []
#         gen = check.isinstance(fn(node), types.GeneratorType)
#         yield omap
#         uomap = next(gen)
#         lang.exhaust(gen)
#         for key, value in uomap:
#             omap.append(NodeWrapped((key, value), node))
#
#     def construct_yaml_omap(self, node):
#         return self.__construct_yaml_pairs(node, super().construct_yaml_omap)  # noqa
#
#     def construct_yaml_pairs(self, node):
#         return self.__construct_yaml_pairs(node, super().construct_yaml_pairs)  # noqa
#
#
# class _cached_class_property:
#     def __init__(self, fn):
#         super().__init__()
#         self._fn = fn
#         self._name = None
#
#     def __call__(self, *args, **kwargs):
#         raise TypeError
#
#     def __set_name__(self, owner, name):
#         self._name = name
#
#     def __get__(self, instance, owner):
#         if owner is None:
#             if instance is None:
#                 raise RuntimeError
#             owner = type(instance)
#         try:
#             return getattr(owner, self._name)
#         except AttributeError:
#             ret = self._fn(owner)
#             owner.__dict__[self._name] = ret
#             return ret
#
#
# class WrappedLoaders(lang.Namespace):
#
#     @staticmethod
#     def _wrap(cls):
#         return type('NodeWrapping$' + cls.__name__, (NodeWrappingConstructorMixin, cls), {})
#
#     Base: type['yaml.BaseLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.BaseLoader))
#
#     @classmethod
#     def base(cls, *args, **kwargs) -> 'yaml.BaseLoader':
#         return cls.Base(*args, **kwargs)
#
#     Full: type['yaml.FullLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.FullLoader))
#
#     @classmethod
#     def full(cls, *args, **kwargs) -> 'yaml.FullLoader':
#         return cls.Full(*args, **kwargs)
#
#     Safe: type['yaml.SafeLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.SafeLoader))
#
#     @classmethod
#     def safe(cls, *args, **kwargs) -> 'yaml.SafeLoader':
#         return cls.Safe(*args, **kwargs)
#
#     Unsafe: type['yaml.UnsafeLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.UnsafeLoader))
#
#     @classmethod
#     def unsafe(cls, *args, **kwargs) -> 'yaml.UnsafeLoader':
#         return cls.Unsafe(*args, **kwargs)
#
#     CBase: type['yaml.CBaseLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.CBaseLoader))
#
#     @classmethod
#     def cbase(cls, *args, **kwargs) -> 'yaml.CBaseLoader':
#         return cls.CBase(*args, **kwargs)
#
#     CFull: type['yaml.CFullLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.CFullLoader))
#
#     @classmethod
#     def cfull(cls, *args, **kwargs) -> 'yaml.CFullLoader':
#         return cls.CFull(*args, **kwargs)
#
#     CSafe: type['yaml.CSafeLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.CSafeLoader))
#
#     @classmethod
#     def csafe(cls, *args, **kwargs) -> 'yaml.CSafeLoader':
#         return cls.CSafe(*args, **kwargs)
#
#     CUnsafe: type['yaml.CUnsafeLoader'] = _cached_class_property(lambda cls: cls._wrap(yaml.CUnsafeLoader))
#
#     @classmethod
#     def cunsafe(cls, *args, **kwargs) -> 'yaml.CUnsafeLoader':
#         return cls.CUnsafe(*args, **kwargs)
#
#
# def load(stream, Loader):
#     with lang.disposing(Loader(stream)) as loader:
#         return loader.get_single_data()
#
#
# def load_all(stream, Loader):
#     with lang.disposing(Loader(stream)) as loader:
#         while loader.check_data():
#             yield loader.get_data()
#
#
# def full_load(stream):
#     return load(stream, yaml.FullLoader)
#
#
# def full_load_all(stream):
#     return load_all(stream, yaml.FullLoader)
