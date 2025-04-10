import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ..processing import ProcessingContext
from ..processing import Processor
from .base import Plan
from .compilation import OpCompiler
from .execution import OpExecutor
from .idents import CLS_IDENT
from .idents import FN_GLOBAL_IMPORTS
from .idents import FN_GLOBALS
from .ops import Op
from .ops import OpRef
from .ops import OpRefMap
from .registry import all_generator_types
from .registry import generator_type_for_plan_type


##


class GeneratorProcessor(Processor):
    def __init__(
            self,
            ctx: ProcessingContext,
            *,
            set_global_kwarg_defaults: bool = True,
    ) -> None:
        super().__init__(ctx)

        self._set_global_kwarg_defaults = set_global_kwarg_defaults

    @dc.dataclass(frozen=True)
    class Prepared:
        plans: tuple[Plan, ...]
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
        print(repr(plans))

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
    def compile(self) -> OpCompiler.CompileResult:
        opc = OpCompiler(
            self._ctx.cls.__qualname__,
            set_global_kwarg_defaults=self._set_global_kwarg_defaults,
            import_global_modules=self._set_global_kwarg_defaults,
        )

        return opc.compile(
            self.ops(),
        )

    #

    def process_with_executor(self) -> None:
        opx = OpExecutor(
            self._ctx.cls,
            self.prepare().ref_map,
        )

        for op in self.ops():
            opx.execute(op)

    def process_with_compiler(self) -> None:
        comp = self.compile()

        ns: dict = {}
        if self._set_global_kwarg_defaults:
            ns.update(FN_GLOBAL_IMPORTS)
        print(comp.src)
        exec(comp.src, ns)
        fn = ns[comp.fn_name]

        kw: dict = {CLS_IDENT: self._ctx.cls}
        kw.update({k: v for k, v in FN_GLOBALS.items() if v.src is None})
        orm = self.prepare().ref_map
        for r in comp.refs:
            kw[r.ident()] = orm[r]

        fn(**kw)

    def _process(
            self,
            mode: ta.Literal['executor', 'compiler'] = 'compiler',
    ) -> None:
        if mode == 'compiler':
            self.process_with_compiler()
        elif mode == 'executor':
            self.process_with_executor()
        else:
            raise ValueError(mode)
