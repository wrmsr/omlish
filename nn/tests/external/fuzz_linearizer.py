import random
import traceback

import numpy as np

from ...codegen.linearizer import Linearizer
from ...device import Compiled
from ...device import Device
from ...features.search import bufs_from_lin
from ...features.search import get_linearizer_actions
from ...features.search import tuplize_uops
from ...graph import print_tree
from ...ops import vars_from_ast

device = Device[Device.DEFAULT]


def run_linearizer(lin: Linearizer, rawbufs=None, var_vals=None):
    if rawbufs is None: rawbufs = bufs_from_lin(lin)
    if var_vals is None: var_vals = {v: v.min for v in vars_from_ast(lin.ast)}

    # TODO: images needs required_optimization
    try:
        if isinstance(device, Compiled):
            prg = device.to_program(lin)
        else:
            prg = device.get_runner(lin.ast)
    except Exception:
        print(lin.ast)
        traceback.print_exc()
        print("COMPILE FAILED!!")
        return "COMPILE_ERROR"

    try:
        prg.exec(rawbufs, var_vals)
    except Exception:
        print(lin.ast)
        traceback.print_exc()
        print("EXEC FAILED!!")
        return "EXEC_ERROR"

    return "PASS"


def fuzz_linearizer(lin: Linearizer):
    random.seed(42)
    np.random.seed(42)
    print_tree(lin.ast)
    print(lin.colored_shape())
    rawbufs = bufs_from_lin(lin)

    seen_uops = {}
    ground_truth = None
    while 1:
        if len(seen_uops) >= 20: break  # enough for this kernel
        actions = get_linearizer_actions(lin, include_0=False)
        if not actions: break
        lin = random.choice(list(actions.values()))
        if lin.applied_opts: print(f"applied action: {lin.applied_opts[-1]}")

        # stop if kernel uops repeat
        tuops = tuplize_uops(lin.linearize().uops)
        if tuops in seen_uops: break
        seen_uops[tuops] = tuple(lin.applied_opts)

        print(lin.colored_shape())
        # get a new output buffer
        rawbufs[0] = type(rawbufs[0])(Device.DEFAULT, rawbufs[0].size, rawbufs[0].dtype)
        var_vals = {v: random.randint(v.min, v.max) for v in vars_from_ast(lin.ast)}
        if (msg := run_linearizer(lin, rawbufs, var_vals)) != "PASS":
            print(f"{lin.applied_opts=}")
            return msg

        result = rawbufs[0].toCPU()
        if ground_truth is None:
            ground_truth = result
        else:
            try:
                np.testing.assert_allclose(result, ground_truth, rtol=1e-2, atol=1e-2)
            except AssertionError:
                print(lin.ast)
                traceback.print_exc()
                print(f"{lin.applied_opts=}")
                return "NOT_ALLCLOSE"
    return "PASS"
