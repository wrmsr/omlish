"""
TODO:
 - populate linecache
"""
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ..processing.base import ProcessingContext
from ..processing.base import Processor
from ..processing.priority import ProcessorPriority
from ..processing.registry import register_processor_type
from .base import Plan
from .base import Plans
from .compilation import OpCompiler
from .execution import OpExecutor
from .idents import CLS_IDENT
from .idents import FN_GLOBALS
from .ops import Op
from .ops import OpRef
from .ops import OpRefMap
from .registry import all_generator_types
from .registry import generator_type_for_plan_type


##


@register_processor_type(priority=ProcessorPriority.GENERATION)
class GeneratorProcessor(Processor):
    def __init__(
            self,
            ctx: ProcessingContext,
            *,
            mode: ta.Literal['executor', 'compiler'] = 'compiler',
    ) -> None:
        super().__init__(ctx)

        self._mode = mode

    @dc.dataclass(frozen=True)
    class Prepared:
        plans: Plans
        ref_map: OpRefMap

        def __post_init__(self) -> None:
            hash(self.plans)

    @lang.cached_function
    def prepare(self) -> Prepared:
        gs = [g_ty() for g_ty in all_generator_types()]

        pll: list[Plan] = []
        orm: dict[OpRef, ta.Any] = {}
        for g in gs:
            if (pr := g.plan(self._ctx)) is None:
                continue

            for k, v in (pr.ref_map or {}).items():
                if k in orm:
                    check.equal(orm[k], v)
                else:
                    orm[k] = v

            pll.append(pr.plan)

        plans = tuple(pll)

        return self.Prepared(
            plans,
            orm,
        )

    @lang.cached_function
    def ops(self) -> ta.Sequence[Op]:
        prepared = self.prepare()

        ops: list[Op] = []
        for pl in prepared.plans:
            g = generator_type_for_plan_type(type(pl))()
            ops.extend(g.generate(pl))

        return ops

    @lang.cached_function
    def compiler(self) -> OpCompiler:
        return OpCompiler(
            self._ctx.cls.__qualname__,
            # OpCompiler.AotStyle(),
            OpCompiler.JitStyle(),
        )

    @lang.cached_function
    def compile(self) -> OpCompiler.CompileResult:
        return self.compiler().compile(
            self.ops(),
        )

    #

    def process_with_executor(self, cls: type) -> None:
        opx = OpExecutor(
            cls,
            self.prepare().ref_map,
        )

        for op in self.ops():
            opx.execute(op)

    def process_with_compiler(self, cls: type) -> None:
        comp = self.compile()

        # print(repr(self.prepare().plans))
        # print(comp.src)

        ns: dict = {}
        ns.update(self.compiler().style.globals_ns())  # noqa

        exec(comp.src, ns)
        fn = ns[comp.fn_name]

        kw: dict = {CLS_IDENT: cls}
        kw.update({k: v for k, v in FN_GLOBALS.items() if v.src.startswith('.')})
        orm = self.prepare().ref_map
        for r in comp.refs:
            kw[r.ident()] = orm[r]

        fn(**kw)

    def process(self, cls: type) -> type:
        if self._mode == 'compiler':
            self.process_with_compiler(cls)
        elif self._mode == 'executor':
            self.process_with_executor(cls)
        else:
            raise ValueError(self._mode)
        return cls
