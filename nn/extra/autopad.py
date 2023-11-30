from test.external.fuzz_linearizer import run_linearizer

from ..codegen.kernel import Opt
from ..codegen.kernel import OptOps
from ..codegen.linearizer import Linearizer
from ..ops import LoadOps
from ..tensor import Tensor

N = 17**3

a = Tensor.rand(N, N)
b = Tensor.rand(N, N)
c = a @ b
sched = [si for si in c.lazydata.schedule() if si.ast.op not in LoadOps]
assert len(sched) == 1
lin = Linearizer(sched[0].ast)

lin.apply_opt(Opt(op=OptOps.PADTO, axis=0, amt=32))
lin.apply_opt(Opt(op=OptOps.PADTO, axis=1, amt=32))
lin.apply_opt(Opt(op=OptOps.PADTO, axis=2, amt=32))
lin.hand_coded_optimizations()
lin.linearize()
print(f"{lin.applied_opts=}")

run_linearizer(lin)
quit()

###

a = Tensor.rand(61, 61).sum(axis=0)
sched = [si for si in a.lazydata.schedule() if si.ast.op not in LoadOps]
assert len(sched) == 1
lin = Linearizer(sched[0].ast)

# lin.apply_opt(Opt(op=OptOps.LOCAL, axis=0, amt=32))

lin.apply_opt(Opt(op=OptOps.PADTO, axis=0, amt=32))
lin.apply_opt(Opt(op=OptOps.PADTO, axis=1, amt=32))
lin.hand_coded_optimizations()
lin.linearize()

run_linearizer(lin)
