import functools
import typing as ta

import numpy as np

from . import prims
from .arrays import get_aval
from .arrays import mapped_aval
from .arrays import moveaxis
from .traces import Trace
from .traces import Tracer
from .traces import full_lower
from .traces import full_raise
from .traces import new_main
from .trees import flatten_fun
from .trees import tree_flatten
from .trees import tree_unflatten
from .utils import unzip2


class NotMapped:
    pass


not_mapped = NotMapped()

BatchAxis = ta.Union[NotMapped, int]


class BatchTracer(Tracer):
    def __init__(self, trace, val, batch_dim: BatchAxis):
        self._trace = trace
        self.val = val
        self.batch_dim = batch_dim

    @property
    def aval(self):
        if self.batch_dim is not_mapped:
            return get_aval(self.val)
        else:
            return mapped_aval(self.batch_dim, get_aval(self.val))

    def full_lower(self):
        if self.batch_dim is not_mapped:
            return full_lower(self.val)
        else:
            return self


class BatchTrace(Trace):
    pure = lift = lambda self, val: BatchTracer(self, val, not_mapped)

    def process_primitive(self, primitive, tracers, params):
        vals_in, bdims_in = unzip2((t.val, t.batch_dim) for t in tracers)
        vmap_rule = vmap_rules[primitive]
        val_outs, bdim_outs = vmap_rule(self.axis_size, vals_in, bdims_in, **params)
        return [BatchTracer(self, x, bd) for x, bd in zip(val_outs, bdim_outs)]

    @property
    def axis_size(self):
        return self.main.global_data


vmap_rules = {}


def binop_batching_rule(op, axis_size, vals_in, dims_in):
    (x, y), (x_bdim, y_bdim) = vals_in, dims_in
    if x_bdim != y_bdim:
        if x_bdim is not_mapped:
            x = move_batch_axis(axis_size, x_bdim, y_bdim, x)
            x_bdim = y_bdim
        else:
            y = move_batch_axis(axis_size, y_bdim, x_bdim, y)
    return [op(x, y)], [x_bdim]


vmap_rules[prims.add_p] = functools.partial(binop_batching_rule, prims.add)
vmap_rules[prims.mul_p] = functools.partial(binop_batching_rule, prims.mul)


def vectorized_unop_batching_rule(op, axis_size, vals_in, dims_in):
    (x,), (x_bdim,) = vals_in, dims_in
    return [op(x)], [x_bdim]


vmap_rules[prims.sin_p] = functools.partial(vectorized_unop_batching_rule, prims.sin)
vmap_rules[prims.cos_p] = functools.partial(vectorized_unop_batching_rule, prims.cos)
vmap_rules[prims.neg_p] = functools.partial(vectorized_unop_batching_rule, prims.neg)


def reduce_sum_batching_rule(axis_size, vals_in, dims_in, *, axis):
    (x,), (x_bdim,) = vals_in, dims_in
    new_axis = tuple(ax + (x_bdim <= ax) for ax in axis)
    out_bdim = x_bdim - sum(ax < x_bdim for ax in axis)
    return [prims.reduce_sum(x, new_axis)], [out_bdim]


vmap_rules[prims.reduce_sum_p] = reduce_sum_batching_rule


def move_batch_axis(axis_size, src, dst, x):
    if src is not_mapped:
        target_shape = list(np.shape(x))
        target_shape.insert(dst, axis_size)
        return prims.broadcast(x, target_shape, [dst])
    elif src == dst:
        return x
    else:
        return moveaxis(x, src, dst)


def vmap_flat(f, in_axes, *args):
    axis_size, = {x.shape[ax] for x, ax in zip(args, in_axes) if ax is not not_mapped}
    with new_main(BatchTrace, axis_size) as main:
        trace = BatchTrace(main)
        tracers_in = [BatchTracer(trace, x, ax) if ax is not None else x for x, ax in zip(args, in_axes)]
        outs = f(*tracers_in)
        tracers_out = [full_raise(trace, out) for out in outs]
        vals_out, bdims_out = unzip2((t.val, t.batch_dim) for t in tracers_out)
    outs_transposed = [move_batch_axis(axis_size, bdim, 0, val_out) for val_out, bdim in zip(vals_out, bdims_out)]
    return outs_transposed


def vmap(f, in_axes):
    def batched_f(*args):
        args_flat, in_tree = tree_flatten(args)
        in_axes_flat, in_tree2 = tree_flatten(in_axes)
        if in_tree != in_tree2:
            raise TypeError
        f_flat, out_tree = flatten_fun(f, in_tree)
        outs_flat = vmap_flat(f_flat, in_axes_flat, *args_flat)
        return tree_unflatten(out_tree(), outs_flat)

    return batched_f
