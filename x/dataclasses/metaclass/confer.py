# import dataclasses as dc
# import typing as ta
#
# from .specs import get_metaclass_spec
# from .params import get_params
# from .params import get_params_extras
#
#
# ##
#
#
# _CONFER_CLASS_PARAMS: tuple[str, ...] = (
#     'eq',
#     'frozen',
#     'kw_only',
#
#     'reorder',
#     'cache_hash',
#     'generic_init',
#     'override',
# )
#
# _CONFER_METACLASS_PARAMS: tuple[str, ...] = (
#     'confer',
#     'final_subclasses',
#     'abstract_immediate_subclasses',
# )
#
#
# def confer_kwarg(out: dict[str, ta.Any], k: str, v: ta.Any) -> None:
#     if k in out:
#         if out[k] != v:
#             raise ValueError
#     else:
#         out[k] = v
#
#
# def confer_kwargs(
#         bases: ta.Sequence[type],
#         kwargs: ta.Mapping[str, ta.Any],
# ) -> dict[str, ta.Any]:
#     out: dict[str, ta.Any] = {}
#     for base in bases:
#         if not dc.is_dataclass(base):
#             continue
#
#         if not (bmp := get_metaclass_spec(base)).confer:
#             continue
#
#         for ck in bmp.confer:
#             if ck in kwargs:
#                 continue
#
#             if ck in _CONFER_PARAMS:
#                 confer_kwarg(out, ck, getattr(get_params(base), ck))
#
#             elif ck in _CONFER_PARAMS_EXTRAS:
#                 confer_kwarg(out, ck, getattr(get_params_extras(base), ck))
#
#             elif ck in _CONFER_METACLASS_PARAMS:
#                 confer_kwarg(out, ck, getattr(bmp, ck))
#
#             else:
#                 raise KeyError(ck)
#
#     return out
