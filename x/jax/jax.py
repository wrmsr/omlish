##


from typing import NamedTuple

import numpy as np


class Primitive(NamedTuple):
    name: str


add_p = Primitive('add')
mul_p = Primitive('mul')
neg_p = Primitive("neg")
sin_p = Primitive("sin")
cos_p = Primitive("cos")
reduce_sum_p = Primitive("reduce_sum")
greater_p = Primitive("greater")
less_p = Primitive("less")
transpose_p = Primitive("transpose")
broadcast_p = Primitive("broadcast")


def add(x, y):
    return bind1(add_p, x, y)


def mul(x, y):
    return bind1(mul_p, x, y)


def neg(x):
    return bind1(neg_p, x)


def sin(x):
    return bind1(sin_p, x)


def cos(x):
    return bind1(cos_p, x)


def greater(x, y):
    return bind1(greater_p, x, y)


def less(x, y):
    return bind1(less_p, x, y)


def transpose(x, perm):
    return bind1(transpose_p, x, perm=perm)


def broadcast(x, shape, axes):
    return bind1(broadcast_p, x, shape=shape, axes=axes)


def reduce_sum(x, axis=None):
    if axis is None:
        axis = tuple(range(np.ndim(x)))
    if type(axis) is int:
        axis = (axis,)
    return bind1(reduce_sum_p, x, axis=axis)


def bind1(prim, *args, **params):
    out, = bind(prim, *args, **params)
    return out


##


from contextlib import contextmanager
from typing import Type, List, Tuple, Sequence, Optional, Any


class MainTrace(NamedTuple):
    level: int
    trace_type: Type['Trace']
    global_data: Optional[Any]


trace_stack: List[MainTrace] = []
dynamic_trace: Optional[MainTrace] = None  # to be employed in Part 3


@contextmanager
def new_main(trace_type: Type['Trace'], global_data=None):
    level = len(trace_stack)
    main = MainTrace(level, trace_type, global_data)
    trace_stack.append(main)

    try:
        yield main
    finally:
        trace_stack.pop()


##


class Trace:
    main: MainTrace

    def __init__(self, main: MainTrace) -> None:
        self.main = main

    def pure(self, val): assert False  # must override

    def lift(self, val): assert False  # must override

    def process_primitive(self, primitive, tracers, params):
        assert False  # must override


##


class Tracer:
    _trace: Trace

    __array_priority__ = 1000

    @property
    def aval(self):
        assert False  # must override

    def full_lower(self):
        return self  # default implementation

    def __neg__(self):
        return self.aval._neg(self)

    def __add__(self, other):
        return self.aval._add(self, other)

    def __radd__(self, other):
        return self.aval._radd(self, other)

    def __mul__(self, other):
        return self.aval._mul(self, other)

    def __rmul__(self, other):
        return self.aval._rmul(self, other)

    def __gt__(self, other):
        return self.aval._gt(self, other)

    def __lt__(self, other):
        return self.aval._lt(self, other)

    def __bool__(self):
        return self.aval._bool(self)

    def __nonzero__(self):
        return self.aval._nonzero(self)

    def __getattr__(self, name):
        try:
            return getattr(self.aval, name)
        except AttributeError:
            raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")


def swap(f):
    return lambda x, y: f(y, x)


##


class ShapedArray:
    array_abstraction_level = 1
    shape: Tuple[int, ...]
    dtype: np.dtype

    def __init__(self, shape, dtype):
        self.shape = shape
        self.dtype = dtype

    @property
    def ndim(self):
        return len(self.shape)

    _neg = staticmethod(neg)
    _add = staticmethod(add)
    _radd = staticmethod(swap(add))
    _mul = staticmethod(mul)
    _rmul = staticmethod(swap(mul))
    _gt = staticmethod(greater)
    _lt = staticmethod(less)

    @staticmethod
    def _bool(tracer):
        raise Exception("ShapedArray can't be unambiguously converted to bool")

    @staticmethod
    def _nonzero(tracer):
        raise Exception("ShapedArray can't be unambiguously converted to bool")

    def str_short(self):
        return f'{self.dtype.name}[{",".join(str(d) for d in self.shape)}]'

    def __hash__(self):
        return hash((self.shape, self.dtype))

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.shape == other.shape and self.dtype == other.dtype)

    def __repr__(self):
        return f"ShapedArray(shape={self.shape}, dtype={self.dtype})"


class ConcreteArray(ShapedArray):
    array_abstraction_level = 2
    val: np.ndarray

    def __init__(self, val):
        self.val = val
        self.shape = val.shape
        self.dtype = val.dtype

    @staticmethod
    def _bool(tracer):
        return bool(tracer.aval.val)

    @staticmethod
    def _nonzero(tracer):
        return bool(tracer.aval.val)


def get_aval(x):
    if isinstance(x, Tracer):
        return x.aval
    elif type(x) in jax_types:
        return ConcreteArray(np.asarray(x))
    else:
        raise TypeError(x)


jax_types = {bool, int, float,
             np.bool_, np.int32, np.int64, np.float32, np.float64, np.ndarray}


##


def bind(prim, *args, **params):
    top_trace = find_top_trace(args)
    tracers = [full_raise(top_trace, arg) for arg in args]
    outs = top_trace.process_primitive(prim, tracers, params)
    return [full_lower(out) for out in outs]


##


import operator as op


def find_top_trace(xs) -> Trace:
    top_main = max((x._trace.main for x in xs if isinstance(x, Tracer)),
                   default=trace_stack[0], key=op.attrgetter('level'))
    if dynamic_trace and dynamic_trace.level > top_main.level:
        top_main = dynamic_trace
    return top_main.trace_type(top_main)


def full_lower(val: Any):
    if isinstance(val, Tracer):
        return val.full_lower()
    else:
        return val


def full_raise(trace: Trace, val: Any) -> Tracer:
    if not isinstance(val, Tracer):
        assert type(val) in jax_types
        return trace.pure(val)
    level = trace.main.level
    if val._trace.main is trace.main:
        return val
    elif val._trace.main.level < level:
        return trace.lift(val)
    elif val._trace.main.level > level:
        raise Exception(f"Can't lift level {val._trace.main.level} to {level}.")
    else:  # val._trace.level == level
        raise Exception(f"Different traces at same level: {val._trace}, {trace}.")


##


class EvalTrace(Trace):
    pure = lift = lambda self, x: x  # no boxing in Tracers needed

    def process_primitive(self, primitive, tracers, params):
        return impl_rules[primitive](*tracers, **params)


trace_stack.append(MainTrace(0, EvalTrace, None))  # special bottom of the stack

# NB: in JAX, instead of a dict we attach impl rules to the Primitive instance
impl_rules = {}

impl_rules[add_p] = lambda x, y: [np.add(x, y)]
impl_rules[mul_p] = lambda x, y: [np.multiply(x, y)]
impl_rules[neg_p] = lambda x: [np.negative(x)]
impl_rules[sin_p] = lambda x: [np.sin(x)]
impl_rules[cos_p] = lambda x: [np.cos(x)]
impl_rules[reduce_sum_p] = lambda x, *, axis: [np.sum(x, axis)]
impl_rules[greater_p] = lambda x, y: [np.greater(x, y)]
impl_rules[less_p] = lambda x, y: [np.less(x, y)]
impl_rules[transpose_p] = lambda x, *, perm: [np.transpose(x, perm)]


def broadcast_impl(x, *, shape, axes):
    for axis in sorted(axes):
        x = np.expand_dims(x, axis)
    return [np.broadcast_to(x, shape)]


impl_rules[broadcast_p] = broadcast_impl


##


def f(x):
    y = sin(x) * 2.
    z = - y + x
    return z


print(f(3.0))
