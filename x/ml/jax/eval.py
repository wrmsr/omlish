import numpy as np

from . import prims
from .traces import MainTrace
from .traces import Trace
from .traces import trace_stack


class EvalTrace(Trace):
    pure = lift = lambda self, x: x  # no boxing in Tracers needed

    def process_primitive(self, primitive, tracers, params):
        return impl_rules[primitive](*tracers, **params)


trace_stack.append(MainTrace(0, EvalTrace, None))  # special bottom of the stack

# NB: in JAX, instead of a dict we attach impl rules to the Primitive instance
impl_rules = {}

impl_rules[prims.add_p] = lambda x, y: [np.add(x, y)]
impl_rules[prims.mul_p] = lambda x, y: [np.multiply(x, y)]
impl_rules[prims.neg_p] = lambda x: [np.negative(x)]
impl_rules[prims.sin_p] = lambda x: [np.sin(x)]
impl_rules[prims.cos_p] = lambda x: [np.cos(x)]
impl_rules[prims.reduce_sum_p] = lambda x, *, axis: [np.sum(x, axis)]
impl_rules[prims.greater_p] = lambda x, y: [np.greater(x, y)]
impl_rules[prims.less_p] = lambda x, y: [np.less(x, y)]
impl_rules[prims.transpose_p] = lambda x, *, perm: [np.transpose(x, perm)]


def broadcast_impl(x, *, shape, axes):
    for axis in sorted(axes):
        x = np.expand_dims(x, axis)
    return [np.broadcast_to(x, shape)]


impl_rules[prims.broadcast_p] = broadcast_impl
