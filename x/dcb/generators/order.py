# import dataclasses as dc
# import typing as ta
#
# from ..idents import CLS_IDENT
# from ..ops import AddMethodOp
# from ..ops import Op
# from ..specs import FieldType
# from .base import Generator
# from .base import Plan
# from .base import PlanContext
# from .base import PlanResult
# from .registry import register_generator_type
# from .utils import build_attr_kwargs_str
#
# from .processing import Processor
# from .utils import Namespace
# from .utils import create_fn
# from .utils import set_new_attribute
# from .utils import tuple_str
#
#
# ##
#
#
# def cmp_fn(
#         name: str,
#         op: str,
#         self_tuple: str,
#         other_tuple: str,
#         globals: Namespace,  # noqa
# ) -> ta.Callable:
#     return create_fn(
#         name,
#         ('self', 'other'),
#         [
#             'if other.__class__ is self.__class__:',
#             f' return {self_tuple}{op}{other_tuple}',
#             'return NotImplemented',
#         ],
#         globals=globals,
#     )
#
#
# class OrderProcessor(Processor):
#     def _process(self) -> None:
#         if not self._info.params.order:
#             return
#
#         flds = [f for f in self._info.instance_fields if f.compare]
#         self_tuple = tuple_str('self', flds)
#         other_tuple = tuple_str('other', flds)
#         for name, op in [
#             ('__lt__', '<'),
#             ('__le__', '<='),
#             ('__gt__', '>'),
#             ('__ge__', '>='),
#         ]:
#             if set_new_attribute(self._cls, name, cmp_fn(name, op, self_tuple, other_tuple, globals=self._info.globals)):  # noqa
#                 raise TypeError(
#                     f'Cannot overwrite attribute {name} in class {self._cls.__name__}. '
#                     f'Consider using functools.total_ordering',
#                 )
#
#
# ##
#
#
# @dc.dataclass(frozen=True)
# class OrderPlan(Plan):
#     fields: tuple[str, ...]
#
#
# @register_generator_type(OrderPlan)
# class OrderGenerator(Generator[OrderPlan]):
#     def plan(self, ctx: PlanContext) -> PlanResult[OrderPlan] | None:
#         if '__copy__' in ctx.cls.__dict__:
#             return None
#
#         return PlanResult(OrderPlan(
#             tuple(f.name for f in ctx.cs.fields if f.field_type is not FieldType.CLASS),
#         ))
#
#     def generate(self, pl: OrderPlan) -> ta.Iterable[Op]:
#         lines = [
#             f'def __copy__(self):',
#             f'    if self.__class__ is not {CLS_IDENT}:',
#             f'        raise TypeError(self)',
#             f'    return {CLS_IDENT}({build_attr_kwargs_str('self', *pl.fields)})',
#         ]
#
#         return [AddMethodOp('__copy__', '\n'.join(lines))]
