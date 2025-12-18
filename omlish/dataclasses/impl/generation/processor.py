"""
TODO:
 - untangle compilation from here
 - populate linecache
"""
import abc
import dataclasses as dc
import sys
import typing as ta

from .... import check
from .... import lang
from ....logs import all as logs
from ..processing.base import ProcessingContext
from ..processing.base import ProcessingOption
from ..processing.base import Processor
from ..processing.priority import ProcessorPriority
from ..processing.registry import register_processor_type
from .base import Plan
from .compilation import OpCompiler
from .execution import OpExecutor
from .globals import FN_GLOBALS
from .globals import FnGlobal
from .idents import CLS_IDENT
from .ops import Op
from .ops import OpRef
from .ops import OpRefMap
from .plans import Plans
from .registry import all_generator_types
from .registry import generator_type_for_plan_type


log = logs.get_module_logger(globals())


##


@dc.dataclass(frozen=True)
class PlanOnly(ProcessingOption):
    b: bool


@dc.dataclass(frozen=True, kw_only=True)
class Verbosity(ProcessingOption):
    warn: bool = False
    debug: bool = False


class CompileCallback(ta.Protocol):
    def __call__(
            self,
            ctx: ProcessingContext,
            prepared: 'GeneratorProcessor.Prepared',
            comp: OpCompiler.CompileResult,
    ) -> None:
        ...


@dc.dataclass(frozen=True, kw_only=True)
class Codegen(ProcessingOption):
    style: ta.Literal['jit', 'aot'] = 'jit'

    force: bool = False
    callback: CompileCallback | None = None


##


@register_processor_type(priority=ProcessorPriority.GENERATION)
class GeneratorProcessor(Processor):
    PROCESS_FN_NAME: ta.ClassVar[str] = '_process_dataclass'

    class Mode(lang.Abstract):
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
        def __init__(
                self,
                *,
                codegen: Codegen,
        ) -> None:
            super().__init__()

            self._codegen = codegen

        @classmethod
        def build_standard_kwargs(cls, dc_cls: type) -> dict[str, ta.Any]:
            kw: dict = {CLS_IDENT: dc_cls}
            kw.update({
                k.ident: v.value
                for k, v in FN_GLOBALS.items()
            })
            return kw

        def _process(self, gp: 'GeneratorProcessor', cls: type) -> None:
            style: OpCompiler.Style = {
                'jit': OpCompiler.JitStyle,
                'aot': OpCompiler.AotStyle,
            }[self._codegen.style]()

            compiler = OpCompiler(style)

            comp = compiler.compile(
                GeneratorProcessor.PROCESS_FN_NAME,
                gp.ops(),
            )

            comp_src = '\n'.join([
                *comp.hdr_lines,
                *(['', ''] if comp.hdr_lines else []),
                *comp.fn_lines,
            ])

            if (vo := gp._ctx.option(Verbosity)) is not None and vo.debug:  # noqa
                print(gp.prepare().plans.repr(), file=sys.stderr)
                print(file=sys.stderr)
                print(comp_src, file=sys.stderr)
                print(file=sys.stderr)

            ns: dict = {}
            ns.update(compiler.style.globals_ns())  # noqa

            exec(comp_src, ns)
            o_fn = ns[GeneratorProcessor.PROCESS_FN_NAME]

            if cls.__module__ in sys.modules:
                gl = sys.modules[cls.__module__].__dict__
            else:
                gl = {}

            # TODO: comment why lol
            fn = lang.new_function(**{
                **lang.new_function_kwargs(o_fn),
                **dict(
                    globals=gl,
                ),
            })

            kw = self.build_standard_kwargs(cls)

            orm = gp.prepare().ref_map
            for r in comp.refs:
                if isinstance(r, OpRef):
                    kw[r.ident()] = orm[r]
                elif isinstance(r, FnGlobal):
                    pass
                else:
                    raise TypeError(r)

            fn(**kw)

            if (cg := self._codegen) is not None and (cb := cg.callback) is not None:
                cb(  # noqa
                    gp._ctx,  # noqa
                    gp.prepare(),
                    comp,
                )

    #

    @dc.dataclass(frozen=True)
    class Prepared:
        plans: Plans
        ref_map: OpRefMap

        def __post_init__(self) -> None:
            hash(self.plans)

    @lang.cached_function(no_wrapper_update=True)
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

        plans = Plans(tuple(pll))

        return self.Prepared(
            plans,
            orm,
        )

    @lang.cached_function(no_wrapper_update=True)
    def ops(self) -> ta.Sequence[Op]:
        prepared = self.prepare()

        ops: list[Op] = []
        for pl in prepared.plans:
            g = generator_type_for_plan_type(type(pl))()
            ops.extend(g.generate(pl))

        return ops

    #

    def _process_from_codegen(self, cls: type) -> bool:
        cg_pkg = check.not_none(self._ctx.pkg_cfg.pkg)
        cg_mod_spec = f'{cg_pkg}._dataclasses'

        try:
            __import__(cg_mod_spec)
        except ImportError:
            if (vo := self._ctx.option(Verbosity)) is not None and vo.warn:  # noqa
                log.warning(lambda: f'Codegen module missing for {cls.__module__}.{cls.__qualname__} at {cg_mod_spec}')
            return False

        cg_mod = sys.modules[cg_mod_spec]
        cg_fn_reg = cg_mod.REGISTRY

        #

        prep = self.prepare()
        prep_plan_repr = prep.plans.repr()

        #

        try:
            cg_reg_item = cg_fn_reg[prep_plan_repr]
        except KeyError:
            if (vo := self._ctx.option(Verbosity)) is not None and vo.warn:  # noqa
                log.warning(lambda: f'Codegen missing for {cls.__module__}.{cls.__qualname__} in {cg_mod_spec}')
            return False

        cg_kw, cg_fn = cg_reg_item

        #

        ref_map = {
            ref.ident(): v
            for ref, v in prep.ref_map.items()
        }

        #

        fn_kw = {
            **GeneratorProcessor.CompilerMode.build_standard_kwargs(cls),
            **{k: ref_map[k] for k in cg_kw['op_ref_idents']},
        }

        fn = cg_fn()
        fn(**fn_kw)

        return True

    #

    def process(self, cls: type) -> type:
        if (po := self._ctx.option(PlanOnly)) is not None and po.b:
            self.prepare()
            return cls

        cg = self._ctx.option(Codegen)

        if not (cg is not None and cg.force) and self._ctx.pkg_cfg.cfg.codegen:
            if self._process_from_codegen(cls):
                return cls

        mode: GeneratorProcessor.Mode
        if cg is not None:  # noqa
            mode = GeneratorProcessor.CompilerMode(codegen=cg)
        else:
            mode = GeneratorProcessor.ExecutorMode()

        mode._process(self, cls)  # noqa
        return cls
