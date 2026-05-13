# # ruff: noqa: UP037
# """This file is considered part of the marshal api """
# '''
# w(f'    msh.install_standard_factories(*msh.standard_polymorphism_factories(')
# w(f'        msh.polymorphism_from_subclasses(')
# w(f'            {union_name},')
# w(f'            naming=msh.Naming.SNAKE,')
# w(f'            strip_suffix=msh.AutoStripSuffix,')
# w(f'        ),')
# w(f'        msh.FieldTypeTagging({union_td.discriminator_field!r}),')
# w(f'    ))')
#
# out: list[MarshalerFactory | UnmarshalerFactory] = [
#     PolymorphismMarshalerFactory(poly, tt),
#     PolymorphismUnmarshalerFactory(poly, tt),
# ]
# '''
# import typing as ta
#
# from ... import lang
# from ..api.naming import Naming
# from ..api.vias import MarshalVia
# from ..api.vias import UnmarshalVia
# from .api import AutoStripSuffix
# from .api import TypeTagging
# from .api import WrapperTypeTagging
# from .api import PolymorphismOptions
# from .api import polymorphism_from_subclasses
# from ..api.vias import MarshalVia
# from ..api.vias import Unmarshaler
# from ..factories.lazy import LazyUnmarshalerFactory
# from ..factories.lazy import LazyMarshalerFactory
#
#
# with lang.auto_proxy_import(globals()):
#     from ... import dataclasses as dc
#     from . import marshal as _marshal
#     from . import unmarshal as _unmarshal
#
#
# T = ta.TypeVar('T')
#
#
# ##
#
#
# def set_polymorphic_from_subclasses(
#         *,
#         type_tagging: TypeTagging = WrapperTypeTagging(),
#         naming: Naming | None = None,
#         strip_suffix: bool | type[AutoStripSuffix] | str = False,
# ) -> ta.Callable[[type[T]], type[T]]:
#     opts = PolymorphismOptions(
#         type_tagging=type_tagging,
#         naming=naming,
#         strip_suffix=strip_suffix,
#     )
#
#     def inner(cls):
#         lmf = LazyMarshalerFactory(lambda: _marshal.PolymorphismMarshalerFactory(
#             polymorphism_from_subclasses(
#                 cls,
#                 naming=opts.naming,
#                 strip_suffix=opts.strip_suffix,
#             ),
#             type_tagging=opts.type_tagging,
#         ))
#
#         luf = LazyUnmarshalerFactory(lambda: _unmarshal.PolymorphismUnmarshalerFactory(
#             polymorphism_from_subclasses(
#                 cls,
#                 naming=opts.naming,
#                 strip_suffix=opts.strip_suffix,
#             ),
#             type_tagging=opts.type_tagging,
#         ))
#
#
#
#         return cls
#
#     return inner
