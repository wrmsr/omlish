import dataclasses as dc
import functools
import operator as op
import typing as ta

import numpy as np

from . import prims
from .arrays import ShapedArray
from .arrays import get_aval
from .arrays import raise_to_shaped
from .traces import Trace
from .traces import Tracer
from .traces import bind
from .traces import full_raise
from .traces import new_dynamic
from .traces import new_main
from .trees import PyTreeDef
from .trees import flatten_fun
from .trees import tree_flatten
from .utils import partition_list
from .utils import split_list
from .utils import unzip2


##


class Var:
    aval: ShapedArray

    def __init__(self, aval):
        self.aval = aval


class Lit:
    val: ta.Any
    aval: ShapedArray

    def __init__(self, val):
        self.aval = aval = raise_to_shaped(get_aval(val))
        self.val = np.array(val, aval.dtype)


Atom = ta.Union[Var, Lit]


@dc.dataclass(frozen=True)
class JaxprEqn:
    primitive: prims.Primitive
    inputs: ta.List[Atom]
    params: ta.Dict[str, ta.Any]
    out_binders: ta.List[Var]


@dc.dataclass(frozen=True)
class Jaxpr:
    in_binders: ta.List[Var]
    eqns: ta.List[JaxprEqn]
    outs: ta.List[Atom]

    def __hash__(self): return id(self)

    __eq__ = op.is_


##


@dc.dataclass(frozen=True)
class JaxprType:
    in_types: ta.List[ShapedArray]
    out_types: ta.List[ShapedArray]

    def __repr__(self):
        in_types = ', '.join(aval.str_short() for aval in self.in_types)
        out_types = ', '.join(aval.str_short() for aval in self.out_types)
        return f'({in_types}) -> ({out_types})'


def typecheck_jaxpr(jaxpr: Jaxpr) -> JaxprType:
    env: ta.Set[Var] = set()

    for v in jaxpr.in_binders:
        if v in env:
            raise TypeError
        env.add(v)

    for eqn in jaxpr.eqns:
        in_types = [typecheck_atom(env, x) for x in eqn.inputs]
        out_types = abstract_eval_rules[eqn.primitive](*in_types, **eqn.params)
        for out_binder, out_type in zip(eqn.out_binders, out_types):
            if not out_type == out_binder.aval:
                raise TypeError
        for out_binder in eqn.out_binders:
            if out_binder in env:
                raise TypeError
            env.add(out_binder)

    in_types = [v.aval for v in jaxpr.in_binders]
    out_types = [typecheck_atom(env, x) for x in jaxpr.outs]
    return JaxprType(in_types, out_types)


def typecheck_atom(env: ta.Set[Var], x: Atom) -> ShapedArray:
    if isinstance(x, Var):
        if x not in env:
            raise TypeError("unbound variable")
        return x.aval
    elif isinstance(x, Lit):
        return raise_to_shaped(get_aval(x.val))
    else:
        assert False


##


def eval_jaxpr(jaxpr: Jaxpr, args: ta.List[ta.Any]) -> ta.List[ta.Any]:
    env: ta.Dict[Var, ta.Any] = {}

    def read(x: Atom) -> ta.Any:
        return env[x] if type(x) is Var else x.val

    def write(v: Var, val: ta.Any) -> None:
        assert v not in env  # single-assignment
        env[v] = val

    map(write, jaxpr.in_binders, args)
    for eqn in jaxpr.eqns:
        in_vals = map(read, eqn.inputs)
        outs = bind(eqn.primitive, *in_vals, **eqn.params)
        map(write, eqn.out_binders, outs)
    return map(read, jaxpr.outs)


def jaxpr_as_fun(jaxpr: Jaxpr):
    return lambda *args: eval_jaxpr(jaxpr, args)


##


##


# NB: the analogous class in JAX is called 'DynamicJaxprTracer'
class JaxprTracer(Tracer):
    __slots__ = ['aval']
    aval: ShapedArray

    def __init__(self, trace, aval):
        self._trace = trace
        self.aval = aval


# NB: the analogous class in JAX is called 'DynamicJaxprTrace'
class JaxprTrace(Trace):
    def new_arg(self, aval: ShapedArray) -> JaxprTracer:
        aval = raise_to_shaped(aval)
        tracer = self.builder.new_tracer(self, aval)
        self.builder.tracer_to_var[id(tracer)] = Var(aval)
        return tracer

    def get_or_make_const_tracer(self, val: ta.Any) -> JaxprTracer:
        tracer = self.builder.const_tracers.get(id(val))
        if tracer is None:
            tracer = self.builder.new_tracer(self, raise_to_shaped(get_aval(val)))
            self.builder.add_const(tracer, val)
        return tracer

    pure = lift = get_or_make_const_tracer

    def process_primitive(self, primitive, tracers, params):
        avals_in = [t.aval for t in tracers]
        avals_out = abstract_eval_rules[primitive](*avals_in, **params)
        out_tracers = [self.builder.new_tracer(self, a) for a in avals_out]
        inputs = [self.builder.getvar(t) for t in tracers]
        outvars = [self.builder.add_var(t) for t in out_tracers]
        self.builder.add_eqn(JaxprEqn(primitive, inputs, params, outvars))
        return out_tracers

    @property
    def builder(self):
        return self.main.global_data


# NB: in JAX, we instead attach abstract eval rules to Primitive instances
abstract_eval_rules = {}


##


class JaxprBuilder:
    eqns: ta.List[JaxprEqn]
    tracer_to_var: ta.Dict[int, Var]
    const_tracers: ta.Dict[int, JaxprTracer]
    constvals: ta.Dict[Var, ta.Any]
    tracers: ta.List[JaxprTracer]

    def __init__(self):
        self.eqns = []
        self.tracer_to_var = {}
        self.const_tracers = {}
        self.constvals = {}
        self.tracers = []

    def new_tracer(self, trace: JaxprTrace, aval: ShapedArray) -> JaxprTracer:
        tracer = JaxprTracer(trace, aval)
        self.tracers.append(tracer)
        return tracer

    def add_eqn(self, eqn: JaxprEqn) -> None:
        self.eqns.append(eqn)

    def add_var(self, tracer: JaxprTracer) -> Var:
        assert id(tracer) not in self.tracer_to_var
        var = self.tracer_to_var[id(tracer)] = Var(tracer.aval)
        return var

    def getvar(self, tracer: JaxprTracer) -> Var:
        var = self.tracer_to_var.get(id(tracer))
        assert var is not None
        return var

    def add_const(self, tracer: JaxprTracer, val: ta.Any) -> Var:
        var = self.add_var(tracer)
        self.const_tracers[id(val)] = tracer
        self.constvals[var] = val
        return var

    def build(
            self,
            in_tracers: ta.List[JaxprTracer],
            out_tracers: ta.List[JaxprTracer]
    ) -> ta.Tuple[Jaxpr, ta.List[ta.Any]]:
        constvars, constvals = unzip2(self.constvals.items())
        t2v = lambda t: self.tracer_to_var[id(t)]
        in_binders = constvars + [t2v(t) for t in in_tracers]
        out_vars = [t2v(t) for t in out_tracers]
        jaxpr = Jaxpr(in_binders, self.eqns, out_vars)
        typecheck_jaxpr(jaxpr)
        jaxpr, constvals = _inline_literals(jaxpr, constvals)
        return jaxpr, constvals


##


def _inline_literals(jaxpr: Jaxpr, consts: ta.List[ta.Any]) -> ta.Tuple[Jaxpr, ta.List[ta.Any]]:
    const_binders, other_binders = split_list(jaxpr.in_binders, len(consts))
    scalars = [type(x) in prims.jax_types and not get_aval(x).shape for x in consts]
    new_const_binders, lit_binders = partition_list(scalars, const_binders)
    new_consts, lit_vals = partition_list(scalars, consts)
    literals = dict(zip(lit_binders, map(Lit, lit_vals)))
    new_eqns = [
        JaxprEqn(eqn.primitive, [literals.get(x, x) for x in eqn.inputs], eqn.params, eqn.out_binders)
        for eqn in jaxpr.eqns
    ]
    new_outs = [literals.get(x, x) for x in jaxpr.outs]
    new_jaxpr = Jaxpr(new_const_binders + other_binders, new_eqns, new_outs)
    typecheck_jaxpr(new_jaxpr)
    return new_jaxpr, new_consts


##


def binop_abstract_eval(x: ShapedArray, y: ShapedArray) -> ta.List[ShapedArray]:
    if not isinstance(x, ShapedArray) or not isinstance(y, ShapedArray):
        raise TypeError
    if raise_to_shaped(x) != raise_to_shaped(y):
        raise TypeError
    return [ShapedArray(x.shape, x.dtype)]


abstract_eval_rules[prims.add_p] = binop_abstract_eval
abstract_eval_rules[prims.mul_p] = binop_abstract_eval


def compare_abstract_eval(x: ShapedArray, y: ShapedArray) -> ta.List[ShapedArray]:
    if not isinstance(x, ShapedArray) or not isinstance(y, ShapedArray):
        raise TypeError
    if x.shape != y.shape:
        raise TypeError
    return [ShapedArray(x.shape, np.dtype('bool'))]


abstract_eval_rules[prims.greater_p] = compare_abstract_eval
abstract_eval_rules[prims.less_p] = compare_abstract_eval


def vectorized_unop_abstract_eval(x: ShapedArray) -> ta.List[ShapedArray]:
    return [ShapedArray(x.shape, x.dtype)]


abstract_eval_rules[prims.sin_p] = vectorized_unop_abstract_eval
abstract_eval_rules[prims.cos_p] = vectorized_unop_abstract_eval
abstract_eval_rules[prims.neg_p] = vectorized_unop_abstract_eval


def reduce_sum_abstract_eval(x: ShapedArray, *, axis: ta.Tuple[int, ...]) -> ta.List[ShapedArray]:
    axis_ = set(axis)
    new_shape = [d for i, d in enumerate(x.shape) if i not in axis_]
    return [ShapedArray(tuple(new_shape), x.dtype)]


abstract_eval_rules[prims.reduce_sum_p] = reduce_sum_abstract_eval


def broadcast_abstract_eval(x: ShapedArray, *, shape: ta.Sequence[int], axes: ta.Sequence[int]) -> ta.List[ShapedArray]:
    return [ShapedArray(tuple(shape), x.dtype)]


abstract_eval_rules[prims.broadcast_p] = broadcast_abstract_eval


##


@functools.lru_cache()  # ShapedArrays are hashable
def make_jaxpr_v1(f, *avals_in):
    avals_in, in_tree = tree_flatten(avals_in)
    f, out_tree = flatten_fun(f, in_tree)

    builder = JaxprBuilder()
    with new_main(JaxprTrace, builder) as main:
        trace = JaxprTrace(main)
        tracers_in = [trace.new_arg(aval) for aval in avals_in]
        outs = f(*tracers_in)
        tracers_out = [full_raise(trace, out) for out in outs]
        jaxpr, consts = builder.build(tracers_in, tracers_out)
    return jaxpr, consts, out_tree()


@functools.lru_cache()
def make_jaxpr(f: ta.Callable, *avals_in: ShapedArray) -> ta.Tuple[Jaxpr, ta.List[ta.Any], PyTreeDef]:
    avals_in, in_tree = tree_flatten(avals_in)
    f, out_tree = flatten_fun(f, in_tree)

    builder = JaxprBuilder()
    with new_main(JaxprTrace, builder) as main:
        with new_dynamic(main):
            trace = JaxprTrace(main)
            tracers_in = [trace.new_arg(aval) for aval in avals_in]
            outs = f(*tracers_in)
            tracers_out = [full_raise(trace, out) for out in outs]
            jaxpr, consts = builder.build(tracers_in, tracers_out)
    return jaxpr, consts, out_tree()
