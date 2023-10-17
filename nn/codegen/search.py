import collections
import typing as ta
import copy

from ..codegen.linearizer import Linearizer
from ..codegen.optimizer import Opt
from ..codegen.optimizer import OptOps
from ..devices import Device
from ..execution import Compiled
from ..execution import MemBuffer
from ..helpers import prod
from ..lazy import vars_from_ast
from ..runtime.lib import RawBuffer
from ..shape.symbolic import sym_infer


actions = [
    Opt(op=OptOps.UPCAST, axis=1, amt=21), Opt(op=OptOps.UPCAST, axis=3, amt=27),
    Opt(op=OptOps.LOCAL, axis=1, amt=2), Opt(op=OptOps.UPCAST, axis=4, amt=10),
    Opt(op=OptOps.UPCAST, axis=5, amt=9), Opt(op=OptOps.UPCAST, axis=5, amt=27),
    Opt(op=OptOps.UPCAST, axis=2, amt=3), Opt(op=OptOps.LOCAL, axis=0, amt=3),
    Opt(op=OptOps.UPCAST, axis=3, amt=2), Opt(op=OptOps.UPCAST, axis=1, amt=5),
    Opt(op=OptOps.GROUPTOP, axis=0, amt=256), Opt(op=OptOps.UPCAST, axis=2, amt=12),
    Opt(op=OptOps.UPCAST, axis=1, amt=14), Opt(op=OptOps.UPCAST, axis=3, amt=11),
    Opt(op=OptOps.UPCAST, axis=1, amt=32), Opt(op=OptOps.UPCAST, axis=4, amt=3),
    Opt(op=OptOps.LOCAL, axis=2, amt=3), Opt(op=OptOps.UPCAST, axis=5, amt=2),
    Opt(op=OptOps.UPCAST, axis=6, amt=31), Opt(op=OptOps.UPCAST, axis=5, amt=11),
    Opt(op=OptOps.UPCAST, axis=0, amt=24), Opt(op=OptOps.LOCAL, axis=1, amt=16),
    Opt(op=OptOps.UPCAST, axis=2, amt=5), Opt(op=OptOps.UPCAST, axis=1, amt=7),
    Opt(op=OptOps.UPCAST, axis=3, amt=4), Opt(op=OptOps.UPCAST, axis=6, amt=3),
    Opt(op=OptOps.UPCAST, axis=1, amt=16), Opt(op=OptOps.UPCAST, axis=3, amt=13),
    Opt(op=OptOps.UPCAST, axis=1, amt=25), Opt(op=OptOps.UPCAST, axis=4, amt=5),
    Opt(op=OptOps.UPCAST, axis=6, amt=24), Opt(op=OptOps.UPCAST, axis=5, amt=4),
    Opt(op=OptOps.UPCAST, axis=5, amt=13), Opt(op=OptOps.UPCAST, axis=4, amt=26),
    Opt(op=OptOps.UPCAST, axis=3, amt=6), Opt(op=OptOps.UPCAST, axis=1, amt=9),
    Opt(op=OptOps.UPCAST, axis=3, amt=15), Opt(op=OptOps.UPCAST, axis=2, amt=28),
    Opt(op=OptOps.UPCAST, axis=0, amt=10), Opt(op=OptOps.UPCAST, axis=6, amt=26),
    Opt(op=OptOps.UPCAST, axis=5, amt=6), Opt(op=OptOps.UPCAST, axis=7, amt=3),
    Opt(op=OptOps.LOCAL, axis=3, amt=8), Opt(op=OptOps.UPCAST, axis=1, amt=2),
    Opt(op=OptOps.LOCAL, axis=4, amt=16), Opt(op=OptOps.UPCAST, axis=1, amt=11),
    Opt(op=OptOps.UPCAST, axis=3, amt=8), Opt(op=OptOps.GROUPTOP, axis=1, amt=16),
    Opt(op=OptOps.UPCAST, axis=4, amt=28), Opt(op=OptOps.UPCAST, axis=1, amt=20),
    Opt(op=OptOps.UPCAST, axis=2, amt=21), Opt(op=OptOps.UPCAST, axis=0, amt=3),
    Opt(op=OptOps.GROUP, axis=1, amt=8), Opt(op=OptOps.UPCAST, axis=2, amt=30),
    Opt(op=OptOps.UPCAST, axis=0, amt=12), Opt(op=OptOps.UPCAST, axis=5, amt=8),
    Opt(op=OptOps.LOCAL, axis=1, amt=4), Opt(op=OptOps.UPCAST, axis=4, amt=12),
    Opt(op=OptOps.LOCAL, axis=0, amt=2), Opt(op=OptOps.UPCAST, axis=1, amt=4),
    Opt(op=OptOps.UPCAST, axis=1, amt=13), Opt(op=OptOps.UPCAST, axis=3, amt=10),
    Opt(op=OptOps.UPCAST, axis=4, amt=30), Opt(op=OptOps.GROUPTOP, axis=1, amt=256),
    Opt(op=OptOps.UPCAST, axis=2, amt=14), Opt(op=OptOps.UPCAST, axis=0, amt=5),
    Opt(op=OptOps.LOCAL, axis=0, amt=32), Opt(op=OptOps.UPCAST, axis=2, amt=32),
    Opt(op=OptOps.LOCAL, axis=3, amt=3), Opt(op=OptOps.LOCAL, axis=4, amt=2),
    Opt(op=OptOps.UPCAST, axis=4, amt=14), Opt(op=OptOps.UPCAST, axis=1, amt=6),
    Opt(op=OptOps.UPCAST, axis=3, amt=3), Opt(op=OptOps.UPCAST, axis=1, amt=15),
    Opt(op=OptOps.UPCAST, axis=4, amt=32), Opt(op=OptOps.UPCAST, axis=2, amt=7),
    Opt(op=OptOps.UPCAST, axis=6, amt=5), Opt(op=OptOps.LOCAL, axis=0, amt=16),
    Opt(op=OptOps.UPCAST, axis=2, amt=16), Opt(op=OptOps.UPCAST, axis=2, amt=25),
    Opt(op=OptOps.UPCAST, axis=0, amt=7), Opt(op=OptOps.UPCAST, axis=3, amt=24),
    Opt(op=OptOps.LOCAL, axis=1, amt=8), Opt(op=OptOps.UPCAST, axis=4, amt=7),
    Opt(op=OptOps.LOCAL, axis=2, amt=16), Opt(op=OptOps.UPCAST, axis=4, amt=16),
    Opt(op=OptOps.UPCAST, axis=1, amt=8), Opt(op=OptOps.UPCAST, axis=5, amt=24),
    Opt(op=OptOps.UPCAST, axis=2, amt=9), Opt(op=OptOps.UPCAST, axis=6, amt=7),
    Opt(op=OptOps.UPCAST, axis=6, amt=16), Opt(op=OptOps.UPCAST, axis=2, amt=27),
    Opt(op=OptOps.UPCAST, axis=0, amt=9), Opt(op=OptOps.UPCAST, axis=3, amt=26),
    Opt(op=OptOps.UPCAST, axis=4, amt=9), Opt(op=OptOps.LOCAL, axis=3, amt=16),
    Opt(op=OptOps.UPCAST, axis=4, amt=27), Opt(op=OptOps.UPCAST, axis=5, amt=26),
    Opt(op=OptOps.UPCAST, axis=2, amt=2), Opt(op=OptOps.UPCAST, axis=2, amt=11),
    Opt(op=OptOps.UPCAST, axis=2, amt=20), Opt(op=OptOps.UPCAST, axis=0, amt=2),
    Opt(op=OptOps.UPCAST, axis=3, amt=28), Opt(op=OptOps.UPCAST, axis=6, amt=27),
    Opt(op=OptOps.LOCAL, axis=1, amt=3), Opt(op=OptOps.UPCAST, axis=4, amt=2),
    Opt(op=OptOps.LOCAL, axis=2, amt=2), Opt(op=OptOps.UPCAST, axis=4, amt=11),
    Opt(op=OptOps.UPCAST, axis=7, amt=7), Opt(op=OptOps.UPCAST, axis=1, amt=3),
    Opt(op=OptOps.UPCAST, axis=4, amt=20), Opt(op=OptOps.GROUPTOP, axis=2, amt=16),
    Opt(op=OptOps.UPCAST, axis=2, amt=4), Opt(op=OptOps.LOCAL, axis=0, amt=4),
    Opt(op=OptOps.UPCAST, axis=6, amt=2), Opt(op=OptOps.UPCAST, axis=3, amt=12),
    Opt(op=OptOps.UPCAST, axis=1, amt=24), Opt(op=OptOps.UPCAST, axis=0, amt=4),
    Opt(op=OptOps.UPCAST, axis=2, amt=31), Opt(op=OptOps.LOCAL, axis=3, amt=2),
    Opt(op=OptOps.UPCAST, axis=4, amt=4), Opt(op=OptOps.LOCAL, axis=2, amt=4),
    Opt(op=OptOps.UPCAST, axis=5, amt=3), Opt(op=OptOps.UPCAST, axis=4, amt=13),
    Opt(op=OptOps.UPCAST, axis=2, amt=6), Opt(op=OptOps.GROUPTOP, axis=2, amt=256),
    Opt(op=OptOps.UPCAST, axis=3, amt=5), Opt(op=OptOps.UPCAST, axis=6, amt=4),
    Opt(op=OptOps.UPCAST, axis=2, amt=15), Opt(op=OptOps.UPCAST, axis=1, amt=17),
    Opt(op=OptOps.UPCAST, axis=3, amt=14), Opt(op=OptOps.UPCAST, axis=6, amt=13),
    Opt(op=OptOps.UPCAST, axis=2, amt=24), Opt(op=OptOps.UPCAST, axis=0, amt=6),
    Opt(op=OptOps.UPCAST, axis=3, amt=32), Opt(op=OptOps.LOCAL, axis=3, amt=4),
    Opt(op=OptOps.UPCAST, axis=4, amt=6), Opt(op=OptOps.LOCAL, axis=4, amt=3),
    Opt(op=OptOps.UPCAST, axis=5, amt=5), Opt(op=OptOps.UPCAST, axis=7, amt=2),
    Opt(op=OptOps.UPCAST, axis=4, amt=15), Opt(op=OptOps.UPCAST, axis=4, amt=24),
    Opt(op=OptOps.LOCAL, axis=0, amt=8), Opt(op=OptOps.UPCAST, axis=2, amt=8),
    Opt(op=OptOps.UPCAST, axis=3, amt=7), Opt(op=OptOps.UPCAST, axis=1, amt=10),
    Opt(op=OptOps.UPCAST, axis=6, amt=6), Opt(op=OptOps.UPCAST, axis=2, amt=17),
    Opt(op=OptOps.UPCAST, axis=3, amt=16), Opt(op=OptOps.GROUP, axis=1, amt=4),
    Opt(op=OptOps.UPCAST, axis=1, amt=28), Opt(op=OptOps.LOCAL, axis=2, amt=8),
    Opt(op=OptOps.UPCAST, axis=4, amt=8), Opt(op=OptOps.UPCAST, axis=5, amt=7),
    Opt(op=OptOps.UPCAST, axis=7, amt=4), Opt(op=OptOps.UPCAST, axis=5, amt=16),
    Opt(op=OptOps.GROUPTOP, axis=0, amt=16), Opt(op=OptOps.UPCAST, axis=2, amt=10),
    Opt(op=OptOps.UPCAST, axis=1, amt=12), Opt(op=OptOps.UPCAST, axis=3, amt=9),
]

device: Compiled = ta.cast(Compiled, Device[Device.DEFAULT])


# returns time(s) and GFLOPS
def time_linearizer(
        lin: Linearizer,
        rawbufs: list[RawBuffer],
        allow_test_size=True,
        cnt=3,
        should_copy=True,
) -> tuple[float, float]:
    if should_copy:
        lin = copy.deepcopy(lin)  # TODO: remove the need for this
    var_vals = {k: k.min for k in vars_from_ast(lin.ast)}
    try:
        lin.linearize()
        prg = device.to_program(lin)
        real_global_size = prg.global_size[:]
        prg.global_size = [1, 1, 1]
        tm = prg(rawbufs, var_vals, force_wait=True)
    except Exception:
        print("FAILED")
        print(lin.ast)
        print(lin.applied_opts)
        return float('inf'), 0

    if allow_test_size:
        test_global_size = real_global_size[:]
        while prod(test_global_size) > 16384:
            for j in range(2, -1, -1):
                if test_global_size[j] > 1:
                    test_global_size[j] //= 2
                    break
        factor = prod(real_global_size) / prod(test_global_size)
        prg.global_size = test_global_size
    else:
        prg.global_size = real_global_size
        factor = 1

    tm = min([prg(rawbufs, var_vals, force_wait=True) for _ in range(cnt)])
    tm *= factor
    gflops = sym_infer(lin.info.flops, var_vals) * 1e-9 / tm
    return tm, gflops


# get (scrap) buffers for timing the linearizer
def bufs_from_lin(lin: Linearizer) -> list[RawBuffer]:
    bufsts: ta.DefaultDict[int, list[MemBuffer]] = collections.defaultdict(list)
    for x in lin.membufs: bufsts[x.idx].append(x)
    rawbufs: list[ta.Optional[RawBuffer]] = [None] * len(bufsts)
    for k, lx in bufsts.items():
        rawbufs[k] = device.buffer(max(y.st.size() for y in lx), lx[0].dtype)
    assert all(r is not None for r in rawbufs)
    return ta.cast(list[RawBuffer], rawbufs)


# get dictionary of all possible actions
def get_linearizer_actions(lin: Linearizer) -> dict[int, Linearizer]:
    acted_lins = {}
    for i, a in enumerate(actions):
        lin2 = copy.deepcopy(lin)
        try:
            lin2.apply_opt(a)
            up, lcl = 1, 1
            for s, c in zip(lin2.full_shape, lin2.colors()):
                if c in {"magenta", "yellow"}:
                    up *= s
                if c in {"cyan", "green", "white"}:
                    lcl *= s
            if up > 256 or lcl > 256:
                continue
            acted_lins[i] = lin2
        except Exception:
            pass
    return acted_lins
