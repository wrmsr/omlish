from . import prims
from .arrays import get_aval
from .arrays import zeros_like
from .traces import Trace
from .traces import Tracer
from .traces import full_raise
from .traces import new_main
from .utils import unzip2


class JVPTracer(Tracer):
    def __init__(self, trace, primal, tangent):
        self._trace = trace
        self.primal = primal
        self.tangent = tangent

    @property
    def aval(self):
        return get_aval(self.primal)


class JVPTrace(Trace):
    pure = lift = lambda self, val: JVPTracer(self, val, zeros_like(val))

    def process_primitive(self, primitive, tracers, params):
        primals_in, tangents_in = unzip2((t.primal, t.tangent) for t in tracers)
        jvp_rule = jvp_rules[primitive]
        primal_outs, tangent_outs = jvp_rule(primals_in, tangents_in, **params)
        return [JVPTracer(self, x, t) for x, t in zip(primal_outs, tangent_outs)]


jvp_rules = {}


def add_jvp(primals, tangents):
    (x, y), (x_dot, y_dot) = primals, tangents
    return [x + y], [x_dot + y_dot]


jvp_rules[prims.add_p] = add_jvp


def mul_jvp(primals, tangents):
    (x, y), (x_dot, y_dot) = primals, tangents
    return [x * y], [x_dot * y + x * y_dot]


jvp_rules[prims.mul_p] = mul_jvp


def sin_jvp(primals, tangents):
    (x,), (x_dot,) = primals, tangents
    return [prims.sin(x)], [prims.cos(x) * x_dot]


jvp_rules[prims.sin_p] = sin_jvp


def cos_jvp(primals, tangents):
    (x,), (x_dot,) = primals, tangents
    return [prims.cos(x)], [-prims.sin(x) * x_dot]


jvp_rules[prims.cos_p] = cos_jvp


def neg_jvp(primals, tangents):
    (x,), (x_dot,) = primals, tangents
    return [prims.neg(x)], [prims.neg(x_dot)]


jvp_rules[prims.neg_p] = neg_jvp


def reduce_sum_jvp(primals, tangents, *, axis):
    (x,), (x_dot,) = primals, tangents
    return [prims.reduce_sum(x, axis)], [prims.reduce_sum(x_dot, axis)]


jvp_rules[prims.reduce_sum_p] = reduce_sum_jvp


def greater_jvp(primals, tangents):
    (x, y), _ = primals, tangents
    out_primal = prims.greater(x, y)
    return [out_primal], [zeros_like(out_primal)]


jvp_rules[prims.greater_p] = greater_jvp


def less_jvp(primals, tangents):
    (x, y), _ = primals, tangents
    out_primal = prims.less(x, y)
    return [out_primal], [zeros_like(out_primal)]


jvp_rules[prims.less_p] = less_jvp


def jvp_v1(f, primals, tangents):
    with new_main(JVPTrace) as main:
        trace = JVPTrace(main)
        tracers_in = [JVPTracer(trace, x, t) for x, t in zip(primals, tangents)]
        out = f(*tracers_in)
        tracer_out = full_raise(trace, out)
        primal_out, tangent_out = tracer_out.primal, tracer_out.tangent
    return primal_out, tangent_out
