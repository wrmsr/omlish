# import dataclasses as dc
# import typing as ta
#
# from ..generation.base import Generator
# from ..generation.base import Plan
# from ..generation.base import PlanContext
# from ..generation.base import PlanResult
# from ..generation.registry import register_generator_type
# from ..generation.ops import Op
#
#
# ##
#
#
# @dc.dataclass(frozen=True)
# class DocPlan(Plan):
#     fields: tuple[str, ...]
#
#
# @register_generator_type(DocPlan)
# class DocGenerator(Generator[DocPlan]):
#     def plan(self, ctx: PlanContext) -> PlanResult[DocPlan] | None:
#         # if getattr(self._cls, '__doc__'):
#         #     return
#         #
#         # try:
#         #     text_sig = str(inspect.signature(self._cls)).replace(' -> None', '')
#         # except (TypeError, ValueError):
#         #     text_sig = ''
#         # self._cls.__doc__ = (self._cls.__name__ + text_sig)
#
#         raise NotImplementedError
#
#     def generate(self, pl: DocPlan) -> ta.Iterable[Op]:
#         raise NotImplementedError
