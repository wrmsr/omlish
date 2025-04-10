# import dataclasses as dc
# import typing as ta
#
# from ..generators.base import Generator
# from ..generators.base import Plan
# from ..generators.base import PlanContext
# from ..generators.base import PlanResult
# from ..generators.registry import register_generator_type
# from ..generators.ops import Op
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
