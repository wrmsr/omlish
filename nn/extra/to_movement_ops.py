import itertools

from .. import ops
from ..helpers import prod
from ..shape.shapetracker import ShapeTracker
from ..shape.view import View
from ..shape.symbolic import sym_infer


inf = float('inf')
nan = float('nan')


def get_real_view(shape, strides, offset, mask):
    real_shape = tuple(y - x for x, y in mask) if mask else shape
    offset = offset + sum(st * (s - 1) for s, st in zip(real_shape, strides) if st < 0)
    real_offset = offset + (sum(x * st for (x, _), st in zip(mask, strides)) if mask else 0)
    real_real_shape = [s for s, st in zip(real_shape, strides) if st]
    strides = [abs(st) if isinstance(st, int) else st for st in strides if st]
    return real_real_shape, strides, real_offset


def get_buffer_size(shape, strides, offset, mask):
    real_real_shape, strides, real_offset = get_real_view(shape, strides, offset, mask)
    return real_offset + sum((s - 1) * st for s, st in zip(real_real_shape, strides)) + 1


def st_equivalent(st1: ShapeTracker, st2: ShapeTracker):
    if (idxs1 := st1.expr_idxs()) == (idxs2 := st2.expr_idxs()):
        return True

    idx1, valid1 = idxs1
    idx2, valid2 = idxs2
    # always invalid
    if valid1 == 0 and valid2 == 0:
        return True

    var1 = set(idx1.vars() + valid1.vars())
    var2 = set(idx2.vars() + valid2.vars())
    # Maybe there are cases that vars are different yet the sts are the same?
    if var1 != var2:
        return False

    # brute force over the vars range
    vs = list(var1)
    for i, ranges in enumerate(itertools.product(*[range(v.min, v.max + 1) for v in vs])):
        if i > 1000:
            print("WARNING: did not search all possible combinations")
            # not happening for now
            break

        var_vals = {k: v for k, v in zip(vs, ranges)}
        r1 = sym_infer(idx1, var_vals) if sym_infer(valid1, var_vals) else 0
        r2 = sym_infer(idx2, var_vals) if sym_infer(valid2, var_vals) else 0
        if r1 != r2:
            return False

    return True


def test_rebuild(st: ShapeTracker):
    rebuilt_st = ShapeTracker.from_shape((
        get_buffer_size(
            st.views[0].shape,
            st.views[0].strides,
            st.views[0].offset,
            st.views[0].mask,
        ),
    ))

    for mop, arg in st.to_movement_ops():
        if mop is ops.Reshape:
            # shapetracker doesn't allow flattening with -1 but required for MovementOps.RESHAPE
            if arg == (-1,):
                rebuilt_st = rebuilt_st.reshape((prod(rebuilt_st.views[-1].shape),))
            else:
                rebuilt_st = rebuilt_st.reshape(arg)

        elif mop is ops.Permute:
            rebuilt_st = rebuilt_st.permute(arg)

        elif mop is ops.Expand:
            if len(arg) != len(rebuilt_st.shape):
                rebuilt_st = rebuilt_st.reshape((1, *rebuilt_st.shape))
            rebuilt_st = rebuilt_st.expand(arg)

        elif mop is ops.Pad:
            rebuilt_st = rebuilt_st.pad(arg)

        elif mop is ops.Shrink:
            rebuilt_st = rebuilt_st.shrink(arg)

        elif mop is ops.Restride:
            rebuilt_st = rebuilt_st.stride(arg)

        else:
            raise Exception("invalid mop")

    rebuilt_st = rebuilt_st.simplify()
    assert st_equivalent(st, rebuilt_st)
    last_v1 = st.views[-1]
    last_v2 = rebuilt_st.views[-1]
    assert last_v1.shape == last_v2.shape, f"{last_v1.shape} != {last_v2.shape}"
