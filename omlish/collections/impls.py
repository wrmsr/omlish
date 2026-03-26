# import typing as ta
#
# from .. import lang
#
#
# with lang.auto_proxy_import(globals()):
#     from .hamt import hamtmap
#     from . import skiplist
#     from .treap import treapmap
#
#
# if ta.TYPE_CHECKING:
#     from .sorted import SortedMapping
#     from .sorted import SortedMutableMapping
#     from .persistent import PersistentMapping
#
#
# K = ta.TypeVar('K')
# V = ta.TypeVar('V')
#
#
# ##
#
#
# def new_persistent_map(
#         items: ta.Iterable[tuple[K, V]] | None = None,
# ) -> 'PersistentMapping[K, V]':
#     return treapmap.new_treap_map()
#
#
# #
#
#
# def new_sorted_map(
#         items: ta.Iterable[tuple[K, V]] | None = None,
# ) -> 'SortedMapping[K, V]':
#     return skiplist.new_skip_list_map()
#
#
# def new_sorted_mutable_map(
#         items: ta.Iterable[tuple[K, V]] | None = None,
# ) -> 'SortedMutableMapping[K, V]':
#     return skiplist.new_skip_list_map()
#
#
# #
#
#
# def new_persistent_sorted_map(
#         items: ta.Iterable[tuple[K, V]] | None = None,
# )
