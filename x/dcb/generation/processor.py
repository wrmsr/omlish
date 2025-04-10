"""
TODO:
 - populate linecache
"""
import abc
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
    class Mode(abc.ABC):
        @abc.abstractmethod
        def _process(self, gp: 'GeneratorProcessor', cls: type) -> None:
            raise NotImplementedError

    class ExecutorMode(Mode):
        def _process(self, gp: 'GeneratorProcessor', cls: type) -> None:
            opx = OpExecutor(
                cls,
                gp.prepare().ref_map,
            )

            for op in gp.ops():
                opx.execute(op)

    class CompilerMode(Mode):
        def _process(self, gp: 'GeneratorProcessor', cls: type) -> None:
            compiler = OpCompiler(
                OpCompiler.AotStyle(),
                # OpCompiler.JitStyle(),
            )

            comp = compiler.compile(
                '_transform_dataclass',
                gp.ops(),
            )

            # print(repr(gp.prepare().plans))
            # print(comp.src)

            ns: dict = {}
            ns.update(compiler.style.globals_ns())  # noqa

            exec(comp.src, ns)
            fn = ns[comp.fn_name]

            kw: dict = {CLS_IDENT: cls}
            kw.update({k: v for k, v in FN_GLOBALS.items() if v.src.startswith('.')})
            orm = gp.prepare().ref_map
            for r in comp.refs:
                kw[r.ident()] = orm[r]

            fn(**kw)

    #

    def __init__(
            self,
            ctx: ProcessingContext,
            *,
            mode: Mode = CompilerMode(),
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

    #

    def process(self, cls: type) -> type:
        self._mode._process(self, cls)  # noqa
        return cls
