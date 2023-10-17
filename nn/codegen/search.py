import collections
import typing as ta
import copy

from ..codegen.linearizer import Linearizer
from ..codegen.optimizer import Opt
from ..codegen.optimizer import OptOps
from ..devices import Device
from ..execution import Compiled
from ..execution import MemBuffer
from ..helpers import flatten
from ..helpers import getenv
from ..helpers import prod
from ..lazy import vars_from_ast
from ..runtime.lib import RawBuffer


actions = flatten([[Opt(op=OptOps.UPCAST, axis=axis, amt=amt) for amt in [0, 2, 3, 4, 7]] for axis in range(6)])
actions += flatten([[Opt(op=OptOps.UNROLL, axis=axis, amt=amt) for amt in [0, 4]] for axis in range(4)])
actions += flatten([[Opt(op=OptOps.LOCAL, axis=axis, amt=amt) for amt in [2, 3, 4, 8, 16]] for axis in range(5)])
actions += [
    Opt(op=OptOps.LOCAL, axis=0, amt=32),
    Opt(op=OptOps.GROUP, axis=1, amt=4), Opt(op=OptOps.GROUP, axis=1, amt=8), Opt(op=OptOps.GROUP, axis=2, amt=8),
    Opt(op=OptOps.GROUPTOP, axis=0, amt=16), Opt(op=OptOps.GROUPTOP, axis=0, amt=256),
    Opt(op=OptOps.GROUPTOP, axis=1, amt=16), Opt(op=OptOps.GROUPTOP, axis=1, amt=256),
    Opt(op=OptOps.GROUPTOP, axis=2, amt=16), Opt(op=OptOps.GROUPTOP, axis=2, amt=256)
]

device: Compiled = ta.cast(Compiled, Device[Device.DEFAULT])


logtm = open(getenv("LOGTM", ""),"a") if getenv("LOGTM", "") else None


# returns time in seconds
def time_linearizer(
        lin: Linearizer,
        rawbufs: list[RawBuffer],
        allow_test_size=True,
        max_global_size=65536,
        cnt=3,
        should_copy=True,
) -> float:
    if should_copy:
        lin = copy.deepcopy(lin)  # TODO: remove the need for this
    var_vals = {k: k.min for k in vars_from_ast(lin.ast)}
    try:
        lin.linearize()
        prg = device.to_program(lin)
        real_global_size = prg.global_size[:]
        if allow_test_size:
            test_global_size = prg.global_size[:]
            while prod(test_global_size) > max_global_size:
                for j in range(2, -1, -1):
                    if test_global_size[j] > 16:
                        test_global_size[j] //= 2
                        break
            factor = prod(prg.global_size) / prod(test_global_size)
            prg.global_size = test_global_size
        else:
            factor = 1
        tms = [prg(rawbufs, var_vals, force_wait=True) * factor for _ in range(cnt)]
        prg.global_size = real_global_size
    except Exception:
        tms = [float('inf')]
    if logtm:
        logtm.write(str((lin.ast, lin.applied_opts, tms)) + "\n")
    return min(tms)


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
    acted_lins = {0: copy.deepcopy(lin)}
    for i, a in enumerate(actions):
        if a.axis >= lin.shape_len:
            continue
        if lin.full_shape[a.axis] == a.amt and Opt(a.op, a.axis, 0) in actions:
            continue
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
            acted_lins[i + 1] = lin2
        except Exception:
            pass
    return acted_lins
