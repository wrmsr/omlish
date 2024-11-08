"""
NOTE: This cannot be auto-imported as @omlish-lite usage of other modules in this package requires it be importable on
8.
"""
# import typing as ta
#
# from omlish import lang
# from omlish import marshal as msh
# from omlish import reflect as rfl
#
# from .requires import RequiresMarkerList
# from .requires import RequiresNode
# from .requires import RequiresOp
# from .requires import RequiresValue
# from .requires import RequiresVariable
#
#
# ##
#
#
# class MarshalRequiresMarkerList(lang.NotInstantiable, lang.Final):
#     pass
#
#
# ##
#
#
# @lang.static_init
# def _install_standard_marshalling() -> None:
#     requires_node_poly = msh.Polymorphism(
#         RequiresNode,
#         [
#             msh.Impl(RequiresVariable, 'variable'),
#             msh.Impl(RequiresValue, 'value'),
#             msh.Impl(RequiresOp, 'op'),
#         ],
#     )
#     msh.STANDARD_MARSHALER_FACTORIES[0:0] = [
#         msh.PolymorphismMarshalerFactory(requires_node_poly),
#     ]
#     msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [
#         msh.PolymorphismUnmarshalerFactory(requires_node_poly),
#     ]
#
#     msh.GLOBAL_REGISTRY.register(
#         RequiresMarkerList,
#         msh.ReflectOverride(MarshalRequiresMarkerList),
#         identity=True,
#     )
#
#     RequiresMarkerVar = ta.Union['RequiresVariable', 'RequiresValue']
#     RequiresMarkerItem = ta.Tuple['RequiresMarkerVar', 'RequiresOp', 'RequiresMarkerVar']
#     RequiresMarkerAtom = ta.Union['RequiresMarkerItem', ta.Sequence['RequiresMarkerAtom']]
#     RequiresMarkerList = ta.Sequence[ta.Union['RequiresMarkerList', 'RequiresMarkerAtom', str]]
