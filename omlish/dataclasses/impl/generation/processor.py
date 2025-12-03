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
from .mangling import IDENT_MANGLER
from .ops import Op
from .ops import OpRef
from .ops import OpRefMap
from .plans import Plans
from .registry import all_generator_types
from .registry import generator_type_for_plan_type


##


@dc.dataclass(frozen=True)
class PlanOnly(ProcessingOption):
    b: bool


@dc.dataclass(frozen=True)
class Verbose(ProcessingOption):
    b: bool


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

    callback: CompileCallback | None = None


@register_processor_type(priority=ProcessorPriority.GENERATION)
class GeneratorProcessor(Processor):
    @classmethod
    def build_process_fn_name(cls, dc_cls) -> str:
        return '_process_dataclass__' + IDENT_MANGLER.mangle('.'.join([dc_cls.__module__, dc_cls.__qualname__]))

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

        # def build_proc_fn_kwargs(self, gp: 'GeneratorProcessor', cls: type) -> None:
        #     kw: dict = {CLS_IDENT: cls}
        #     kw.update({
        #         k.ident: v.value
        #         for k, v in FN_GLOBALS.items()
        #         # if v.src.startswith('.')
        #     })
        #     orm = gp.prepare().ref_map
        #     for r in comp.refs:
        #         if isinstance(r, OpRef):
        #             kw[r.ident()] = orm[r]
        #         elif isinstance(r, FnGlobal):
        #             pass
        #         else:
        #             raise TypeError(r)

        def _process(self, gp: 'GeneratorProcessor', cls: type) -> None:
            style: OpCompiler.Style = {
                'jit': OpCompiler.JitStyle,
                'aot': OpCompiler.AotStyle,
            }[self._codegen.style]()

            compiler = OpCompiler(style)

            fn_name = GeneratorProcessor.build_process_fn_name(cls)

            comp = compiler.compile(
                fn_name,
                gp.ops(),
            )

            comp_src = '\n'.join([
                *comp.hdr_lines,
                *(['', ''] if comp.hdr_lines else []),
                *comp.fn_lines,
            ])

            if (vo := gp._ctx.option(Verbose)) is not None and vo.b:  # noqa
                print(gp.prepare().plans.render(), file=sys.stderr)
                print(file=sys.stderr)
                print(comp_src, file=sys.stderr)
                print(file=sys.stderr)

            ns: dict = {}
            ns.update(compiler.style.globals_ns())  # noqa

            exec(comp_src, ns)
            o_fn = ns[comp.fn_name]

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

            kw: dict = {CLS_IDENT: cls}
            kw.update({
                k.ident: v.value
                for k, v in FN_GLOBALS.items()
                # if v.src.startswith('.')
            })
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
            # TODO: log
            return False

        cg_mod = sys.modules[cg_mod_spec]
        cg_fn_reg = cg_mod.REGISTRY

        #

        fn_name = GeneratorProcessor.build_process_fn_name(cls)

        try:
            cg_reg_item = cg_fn_reg[fn_name]
        except KeyError:
            # TODO: log
            return False

        (cg_plan_repr, cg_op_refs), cg_fn = cg_reg_item

        #

        prep = self.prepare()

        prep_plan_repr = repr(prep.plans)
        if prep_plan_repr != cg_plan_repr:
            # TODO: log
            return False

        # raise NotImplementedError
        return False

    #

    def process(self, cls: type) -> type:
        if (po := self._ctx.option(PlanOnly)) is not None and po.b:
            self.prepare()
            return cls

        if self._ctx.pkg_cfg.cfg.codegen:
            if self._process_from_codegen(cls):
                return cls

        mode: GeneratorProcessor.Mode
        if (cg := self._ctx.option(Codegen)) is not None:  # noqa
            mode = GeneratorProcessor.CompilerMode(codegen=cg)
        else:
            mode = GeneratorProcessor.ExecutorMode()

        mode._process(self, cls)  # noqa
        return cls
