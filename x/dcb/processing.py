import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from .compilation import OpCompiler
from .execution import OpExecutor
from .generators import Plan
from .generators import PlanContext
from .generators import all_generator_types
from .generators import generator_type_for_plan_type
from .ops import Op
from .ops import OpRef
from .ops import OpRefMap
from .specs import ClassSpec
from .specs import get_class_spec


##


class ClassProcessor:
    def __init__(
            self,
            cls: type,
            cs: ClassSpec | None = None,
    ) -> None:
        super().__init__()

        self._cls = cls
        if cs is None:
            cs = get_class_spec(cls)
        self._cs = cs

    @dc.dataclass(frozen=True)
    class Prepared:
        plans: tuple[Plan, ...]
        ref_map: OpRefMap

        def __post_init__(self) -> None:
            hash(self.plans)

    @lang.cached_function
    def prepare(self) -> Prepared:
        ctx = PlanContext(self._cls, self._cs)

        gs = [g_ty() for g_ty in all_generator_types()]

        pll: list[Plan] = []
        orm: dict[OpRef, ta.Any] = {}
        for g in gs:
            if (pr := g.plan(ctx)) is None:
                continue

            for k, v in (pr.ref_map or {}).items():
                if k in orm:
                    check.equal(orm[k], v)
                else:
                    orm[k] = v

            pll.append(pr.plan)

        return self.Prepared(
            tuple(pll),
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

    def process(self) -> None:
        self.compile()

        ops = self.ops()
        orm = self.prepare().ref_map

        opx = OpExecutor(self._cls, orm)
        for op in ops:
            opx.execute(op)

    def compile(self) -> None:
        ops = self.ops()

        opc = OpCompiler(self._cls.__qualname__)
        comp = opc.compile(ops)

        print(comp)
