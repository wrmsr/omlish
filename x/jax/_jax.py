"""
pip install jax jaxlib
"""
import dataclasses as dc
import functools
import operator as op
import typing as ta
import weakref

import numpy as np

from .arrays import ShapedArray
from .arrays import get_aval
from .arrays import raise_to_shaped
from .batches import BatchAxis
from .batches import not_mapped
from .batches import vmap
from .batches import vmap_rules
from .eval import impl_rules
from .jaxprs import Atom
from .jaxprs import Jaxpr
from .jaxprs import JaxprEqn
from .jaxprs import Lit
from .jaxprs import Var
from .jaxprs import abstract_eval_rules
from .jaxprs import eval_jaxpr
from .jaxprs import jaxpr_as_fun
from .jaxprs import make_jaxpr
from .jaxprs import typecheck_jaxpr
from .jvp import jvp
from .jvp import jvp_rules
from .prims import Primitive
from .prims import add
from .prims import add_p
from .prims import broadcast
from .prims import broadcast_p
from .prims import cos
from .prims import cos_p
from .prims import greater
from .prims import greater_p
from .prims import jax_types
from .prims import less
from .prims import less_p
from .prims import mul
from .prims import mul_p
from .prims import neg
from .prims import neg_p
from .prims import reduce_sum
from .prims import reduce_sum_p
from .prims import sin
from .prims import sin_p
from .prims import transpose
from .traces import Trace
from .traces import Tracer
from .traces import bind
from .traces import full_lower
from .traces import full_raise
from .traces import new_main
from .trees import flatten_fun
from .trees import register_pytree_node
from .trees import tree_flatten
from .trees import tree_unflatten
from .utils import IDHashable
from .utils import map_
from .utils import merge_lists
from .utils import partition_list
from .utils import split_half
from .utils import split_list
from .utils import unzip2


##


def jit(f):
    def f_jitted(*args):
        avals_in = [raise_to_shaped(get_aval(x)) for x in args]
        jaxpr, consts, out_tree = make_jaxpr(f, *avals_in)
        outs = bind(xla_call_p, *consts, *args, jaxpr=jaxpr, num_consts=len(consts))
        return tree_unflatten(out_tree, outs)

    return f_jitted


xla_call_p = Primitive('xla_call')


##


from jax._src import xla_bridge as xb
from jax._src.lib import xla_client as xc


xe = xc._xla
xops = xc._xla.ops


def xla_call_impl(*args, jaxpr: Jaxpr, num_consts: int):
    consts, args = args[:num_consts], args[num_consts:]
    hashable_consts = tuple(map(IDHashable, consts))
    execute = xla_callable(IDHashable(jaxpr), hashable_consts)
    return execute(*args)


impl_rules[xla_call_p] = xla_call_impl


@functools.lru_cache()
def xla_callable(hashable_jaxpr: IDHashable, hashable_consts: ta.Tuple[IDHashable, ...]):
    jaxpr: Jaxpr = hashable_jaxpr.val
    typecheck_jaxpr(jaxpr)
    consts = [x.val for x in hashable_consts]
    in_avals = [v.aval for v in jaxpr.in_binders[len(consts):]]
    c = xc.XlaBuilder('xla_call')
    xla_consts = _xla_consts(c, consts)
    xla_params = _xla_params(c, in_avals)
    outs = jaxpr_subcomp(c, jaxpr, xla_consts + xla_params)
    out = xops.Tuple(c, outs)
    compiled = xb.get_backend(None).compile(xc._xla.mlir.xla_computation_to_mlir_module(c.build(out)))
    return functools.partial(execute_compiled, compiled, [v.aval for v in jaxpr.outs])


def _xla_consts(c: xe.XlaBuilder, consts: ta.List[ta.Any]) -> ta.List[xe.XlaOp]:
    unique_consts = {id(cnst): cnst for cnst in consts}
    xla_consts = {
        id_: xops.ConstantLiteral(c, cnst)
        for id_, cnst in unique_consts.items()
    }
    return [xla_consts[id(cnst)] for cnst in consts]


def _xla_params(c: xe.XlaBuilder, avals_in: ta.List[ShapedArray]) -> ta.List[xe.XlaOp]:
    return [xops.Parameter(c, i, _xla_shape(a)) for i, a in enumerate(avals_in)]


def _xla_shape(aval: ShapedArray) -> xe.Shape:
    return xc.Shape.array_shape(xc.dtype_to_etype(aval.dtype), aval.shape)


##


def jaxpr_subcomp(c: xe.XlaBuilder, jaxpr: Jaxpr, args: ta.List[xe.XlaOp]) -> ta.List[xe.XlaOp]:
    env: ta.Dict[Var, xe.XlaOp] = {}

    def read(x: Atom) -> xe.XlaOp:
        return env[x] if type(x) is Var else xops.Constant(c, np.asarray(x.val))

    def write(v: Var, val: xe.XlaOp) -> None:
        env[v] = val

    map_(write, jaxpr.in_binders, args)
    for eqn in jaxpr.eqns:
        in_avals = [x.aval for x in eqn.inputs]
        in_vals = map_(read, eqn.inputs)
        rule = xla_translations[eqn.primitive]
        out_vals = rule(c, in_avals, in_vals, **eqn.params)
        map_(write, eqn.out_binders, out_vals)
    return map_(read, jaxpr.outs)


def execute_compiled(compiled, out_avals, *args):
    input_bufs = [input_handlers[type(x)](x) for x in args]
    out_bufs = compiled.execute(input_bufs)
    return [handle_result(aval, buf) for aval, buf in zip(out_avals, out_bufs)]


default_input_handler = xb.get_backend(None).buffer_from_pyval

input_handlers = {ty: default_input_handler for ty in [bool, int, float, np.ndarray, np.float64, np.float32]}


def handle_result(aval: ShapedArray, buf):
    del aval  # Unused for now
    return np.asarray(buf)


xla_translations = {}


##


def direct_translation(op, c, in_avals, in_vals):
    del c, in_avals
    return [op(*in_vals)]


xla_translations[add_p] = functools.partial(direct_translation, xops.Add)
xla_translations[mul_p] = functools.partial(direct_translation, xops.Mul)
xla_translations[neg_p] = functools.partial(direct_translation, xops.Neg)
xla_translations[sin_p] = functools.partial(direct_translation, xops.Sin)
xla_translations[cos_p] = functools.partial(direct_translation, xops.Cos)
xla_translations[greater_p] = functools.partial(direct_translation, xops.Gt)
xla_translations[less_p] = functools.partial(direct_translation, xops.Lt)


def reduce_sum_translation(c, in_avals, in_vals, *, axis):
    (x_aval,), (x,) = in_avals, in_vals
    zero = xops.ConstantLiteral(c, np.array(0, x_aval.dtype))
    subc = xc.XlaBuilder('add')
    shape = _xla_shape(ShapedArray((), x_aval.dtype))
    xops.Add(xops.Parameter(subc, 0, shape), xops.Parameter(subc, 1, shape))
    return [xops.Reduce(c, [x], [zero], subc.build(), axis)]


xla_translations[reduce_sum_p] = reduce_sum_translation


def broadcast_translation(c, in_avals, in_vals, *, shape, axes):
    x, = in_vals
    dims_complement = [i for i in range(len(shape)) if i not in axes]
    return [xops.BroadcastInDim(x, shape, dims_complement)]


xla_translations[broadcast_p] = broadcast_translation


##


def foo():
    @jit
    def f(x, y):
        print('tracing!')
        return sin(x) * cos(y)

    z = f(3., 4.)  # 'tracing!' prints the first time
    print(z)

    z = f(4., 5.)  # 'tracing!' doesn't print, compilation cache hit!
    print(z)

    @jit
    def f(x):
        return reduce_sum(x, axis=0)

    print(f(np.array([1., 2., 3.])))

    def f(x):
        y = sin(x) * 2.
        z = - y + x
        return z

    def deriv(f):
        return lambda x: jvp(f, (x,), (1.,))[1]

    print(deriv(deriv(f))(3.))
    print(jit(deriv(deriv(f)))(3.))

    print()


foo()


##


def xla_call_jvp_rule(primals, tangents, *, jaxpr, num_consts):
    del num_consts  # Unused
    new_jaxpr, new_consts = jvp_jaxpr(jaxpr)
    outs = bind(
        xla_call_p,
        *new_consts,
        *primals,
        *tangents,
        jaxpr=new_jaxpr,
        num_consts=len(new_consts),
    )
    n = len(outs) // 2
    primals_out, tangents_out = outs[:n], outs[n:]
    return primals_out, tangents_out


jvp_rules[xla_call_p] = xla_call_jvp_rule


@functools.lru_cache()
def jvp_jaxpr(jaxpr: Jaxpr) -> ta.Tuple[Jaxpr, ta.List[ta.Any]]:
    def jvp_traceable(*primals_and_tangents):
        n = len(primals_and_tangents) // 2
        primals, tangents = primals_and_tangents[:n], primals_and_tangents[n:]
        return jvp(jaxpr_as_fun(jaxpr), primals, tangents)

    in_avals = [v.aval for v in jaxpr.in_binders]
    new_jaxpr, new_consts, _ = make_jaxpr(jvp_traceable, *in_avals, *in_avals)
    return new_jaxpr, new_consts


def xla_call_vmap_rule(axis_size, vals_in, dims_in, *, jaxpr, num_consts):
    del num_consts  # Unused
    new_jaxpr, new_consts = vmap_jaxpr(jaxpr, axis_size, tuple(dims_in))
    outs = bind(
        xla_call_p,
        *new_consts,
        *vals_in,
        jaxpr=new_jaxpr,
        num_consts=len(new_consts),
    )
    return outs, [0] * len(outs)


vmap_rules[xla_call_p] = xla_call_vmap_rule


@functools.lru_cache()
def vmap_jaxpr(jaxpr: Jaxpr, axis_size: int, bdims_in: ta.Tuple[BatchAxis, ...]) -> ta.Tuple[Jaxpr, ta.List[ta.Any]]:
    vmap_traceable = vmap(jaxpr_as_fun(jaxpr), tuple(bdims_in))
    in_avals = [
        unmapped_aval(axis_size, d, v.aval)
        for v, d in zip(jaxpr.in_binders, bdims_in)
    ]
    new_jaxpr, new_consts, _ = make_jaxpr(vmap_traceable, *in_avals)
    return new_jaxpr, new_consts


def unmapped_aval(axis_size: int, batch_dim: BatchAxis, aval: ShapedArray) -> ShapedArray:
    if batch_dim is not_mapped:
        return aval
    else:
        shape = list(aval.shape)
        shape.insert(batch_dim, axis_size)
        return ShapedArray(tuple(shape), aval.dtype)


def xla_call_abstract_eval_rule(*in_types, jaxpr, num_consts):
    del num_consts  # Unused
    jaxpr_type = typecheck_jaxpr(jaxpr)
    if not all(t1 == t2 for t1, t2 in zip(jaxpr_type.in_types, in_types)):
        raise TypeError
    return jaxpr_type.out_types


abstract_eval_rules[xla_call_p] = xla_call_abstract_eval_rule


def xla_call_translation(c, in_avals, in_vals, *, jaxpr, num_consts):
    del num_consts  # Only used at top-level.
    # Calling jaxpr_subcomp directly would inline. We generate a Call HLO instead.
    subc = xc.XlaBuilder('inner xla_call')
    xla_params = _xla_params(subc, in_avals)
    outs = jaxpr_subcomp(subc, jaxpr, xla_params)
    subc = subc.build(xops.Tuple(subc, outs))
    return destructure_tuple(c, xops.Call(c, subc, in_vals))


xla_translations[xla_call_p] = xla_call_translation


def destructure_tuple(c, tup):
    num_elements = len(c.get_shape(tup).tuple_shapes())
    return [xops.GetTupleElement(tup, i) for i in range(num_elements)]


##


def foo():
    @jit
    def f(x):
        print('tracing!')
        y = sin(x) * 2.
        z = - y + x
        return z

    x, xdot = 3., 1.
    y, ydot = jvp(f, (x,), (xdot,))
    print(y)
    print(ydot)

    y, ydot = jvp(f, (x,), (xdot,))  # 'tracing!' not printed
    ys = vmap(f, (0,))(np.arange(3.))
    print(ys)

    print()


foo()


##


def handle_result(aval: ShapedArray, buf):  # noqa: F811
    return DeviceArray(aval, buf)


class DeviceArray:
    buf: ta.Any
    aval: ShapedArray

    def __init__(self, aval, buf):
        self.aval = aval
        self.buf = buf

    dtype = property(lambda self: self.aval.dtype)
    shape = property(lambda self: self.aval.shape)
    ndim = property(lambda self: self.aval.ndim)

    def __array__(self):
        return np.asarray(self.buf)

    def __repr__(self):
        return repr(np.asarray(self.buf))

    def __str__(self):
        return str(np.asarray(self.buf))

    _neg = staticmethod(neg)
    _add = staticmethod(add)
    _radd = staticmethod(add)
    _mul = staticmethod(mul)
    _rmul = staticmethod(mul)
    _gt = staticmethod(greater)
    _lt = staticmethod(less)


input_handlers[DeviceArray] = lambda x: x.buf

jax_types.add(DeviceArray)


##


def foo():
    @jit
    def f(x):
        y = sin(x) * 2.
        z = - y + x
        return z

    x, xdot = 3., 1.
    y, ydot = jvp(f, (x,), (xdot,))
    print(y)
    print(ydot)

    print()


foo()


##


##


def linearize_flat(f, *primals_in):
    pvals_in = (
            [PartialVal.known(x) for x in primals_in] +
            [PartialVal.unknown(vspace(get_aval(x))) for x in primals_in]
    )

    def f_jvp(*primals_tangents_in):
        primals_out, tangents_out = jvp(f, *split_half(primals_tangents_in))
        return [*primals_out, *tangents_out]

    jaxpr, pvals_out, consts = partial_eval_flat(f_jvp, pvals_in)
    primal_pvals, _ = split_half(pvals_out)
    assert all(pval.is_known for pval in primal_pvals)
    primals_out = [pval.const for pval in primal_pvals]
    f_lin = lambda *tangents: eval_jaxpr(jaxpr, [*consts, *tangents])
    return primals_out, f_lin


def linearize(f, *primals_in):
    primals_in_flat, in_tree = tree_flatten(primals_in)
    f, out_tree = flatten_fun(f, in_tree)
    primals_out_flat, f_lin_flat = linearize_flat(f, *primals_in_flat)
    primals_out = tree_unflatten(out_tree(), primals_out_flat)

    def f_lin(*tangents_in):
        tangents_in_flat, in_tree2 = tree_flatten(tangents_in)
        if in_tree != in_tree2:
            raise TypeError
        tangents_out_flat = f_lin_flat(*tangents_in_flat)
        return tree_unflatten(out_tree(), tangents_out_flat)

    return primals_out, f_lin


def vspace(aval: ShapedArray) -> ShapedArray:
    return raise_to_shaped(aval)  # TODO handle integers?


##


@dc.dataclass(frozen=True)
class PartialVal:
    aval: ShapedArray
    const: ta.Optional[ta.Any]

    @classmethod
    def known(cls, val: ta.Any):
        return PartialVal(get_aval(val), val)

    @classmethod
    def unknown(cls, aval: ShapedArray):
        return PartialVal(aval, None)

    is_known = property(lambda self: self.const is not None)
    is_unknown = property(lambda self: self.const is None)


##


def partial_eval_flat(
        f: ta.Callable,
        pvals_in: ta.List[PartialVal],
) -> ta.Tuple[Jaxpr, ta.List[PartialVal], ta.List[ta.Any]]:
    with new_main(PartialEvalTrace) as main:
        trace = PartialEvalTrace(main)
        tracers_in = [trace.new_arg(pval) for pval in pvals_in]
        outs = f(*tracers_in)
        tracers_out = [full_raise(trace, out) for out in outs]
        pvals_out = [t.pval for t in tracers_out]
        unk_tracers_in = [t for t in tracers_in if t.pval.is_unknown]
        unk_tracers_out = [t for t in tracers_out if t.pval.is_unknown]
        jaxpr, consts = tracers_to_jaxpr(unk_tracers_in, unk_tracers_out)
    return jaxpr, pvals_out, consts


##


@dc.dataclass(frozen=True)
class LambdaBindingRecipe:
    pass


@dc.dataclass(frozen=True)
class ConstRecipe:
    val: ta.Any


@dc.dataclass(frozen=True)
class JaxprEqnRecipe:
    prim: Primitive
    tracers_in: ta.List['PartialEvalTracer']
    params: ta.Dict[str, ta.Any]
    avals_out: ta.List[ShapedArray]
    tracer_refs_out: ta.List['weakref.ReferenceType[PartialEvalTracer]']


JaxprRecipe = ta.Union[LambdaBindingRecipe, ConstRecipe, JaxprEqnRecipe]


class PartialEvalTracer(Tracer):
    pval: PartialVal
    recipe: ta.Optional[JaxprRecipe]

    def __init__(self, trace, pval, recipe):
        self._trace = trace
        self.pval = pval
        self.recipe = recipe

    aval = property(lambda self: self.pval.aval)

    def full_lower(self):
        if self.pval.is_known:
            return full_lower(self.pval.const)
        return self


##


class PartialEvalTrace(Trace):
    def new_arg(self, pval: PartialVal) -> ta.Any:
        return PartialEvalTracer(self, pval, LambdaBindingRecipe())

    def lift(self, val: ta.Any) -> PartialEvalTracer:
        return PartialEvalTracer(self, PartialVal.known(val), None)

    pure = lift

    def instantiate_const(self, tracer: PartialEvalTracer) -> PartialEvalTracer:
        if tracer.pval.is_unknown:
            return tracer
        else:
            pval = PartialVal.unknown(raise_to_shaped(tracer.aval))
            return PartialEvalTracer(self, pval, ConstRecipe(tracer.pval.const))

    def process_primitive(self, primitive, tracers, params):
        if all(t.pval.is_known for t in tracers):
            return bind(primitive, *map(full_lower, tracers), **params)
        rule = partial_eval_rules.get(primitive)
        if rule:
            return rule(self, tracers, **params)
        tracers_in = [self.instantiate_const(t) for t in tracers]
        avals_in = [t.aval for t in tracers_in]
        avals_out = abstract_eval_rules[primitive](*avals_in, **params)
        tracers_out = [PartialEvalTracer(self, PartialVal.unknown(aval), None) for aval in avals_out]
        eqn = JaxprEqnRecipe(primitive, tracers_in, params, avals_out, map_(weakref.ref, tracers_out))
        for t in tracers_out:
            t.recipe = eqn
        return tracers_out


partial_eval_rules = {}


##


def tracers_to_jaxpr(
        tracers_in: ta.List[PartialEvalTracer],
        tracers_out: ta.List[PartialEvalTracer],
):
    tracer_to_var: ta.Dict[int, Var] = {id(t): Var(raise_to_shaped(t.aval)) for t in tracers_in}
    constvar_to_val: ta.Dict[int, ta.Any] = {}
    constid_to_var: ta.Dict[int, Var] = {}
    processed_eqns: ta.Set[int] = set()
    eqns: ta.List[JaxprEqn] = []
    for t in toposort(tracers_out, tracer_parents):
        if isinstance(t.recipe, LambdaBindingRecipe):
            assert id(t) in set(map(id, tracers_in))
        elif isinstance(t.recipe, ConstRecipe):
            val = t.recipe.val
            var = constid_to_var.get(id(val))
            if var is None:
                aval = raise_to_shaped(get_aval(val))
                var = constid_to_var[id(val)] = Var(aval)
                constvar_to_val[var] = val
            tracer_to_var[id(t)] = var
        elif isinstance(t.recipe, JaxprEqnRecipe):
            if id(t.recipe) not in processed_eqns:
                eqns.append(recipe_to_eqn(tracer_to_var, t.recipe))
                processed_eqns.add(id(t.recipe))
        else:
            raise TypeError(t.recipe)

    constvars, constvals = unzip2(constvar_to_val.items())
    in_binders = constvars + [tracer_to_var[id(t)] for t in tracers_in]
    out_vars = [tracer_to_var[id(t)] for t in tracers_out]
    jaxpr = Jaxpr(in_binders, eqns, out_vars)
    typecheck_jaxpr(jaxpr)
    return jaxpr, constvals


def recipe_to_eqn(tracer_to_var: ta.Dict[int, Var], recipe: JaxprEqnRecipe) -> JaxprEqn:
    inputs = [tracer_to_var[id(t)] for t in recipe.tracers_in]
    out_binders = [Var(aval) for aval in recipe.avals_out]
    for t_ref, var in zip(recipe.tracer_refs_out, out_binders):
        if t_ref() is not None:
            tracer_to_var[id(t_ref())] = var
    return JaxprEqn(recipe.prim, inputs, recipe.params, out_binders)


def tracer_parents(t: PartialEvalTracer) -> ta.List[PartialEvalTracer]:
    return t.recipe.tracers_in if isinstance(t.recipe, JaxprEqnRecipe) else []


##


def toposort(out_nodes: ta.List[ta.Any], parents: ta.Callable[[ta.Any], ta.List[ta.Any]]):
    if not out_nodes:
        return []
    out_nodes = remove_duplicates(out_nodes)

    child_counts = {}
    stack = list(out_nodes)
    while stack:
        node = stack.pop()
        if id(node) in child_counts:
            child_counts[id(node)] += 1
        else:
            child_counts[id(node)] = 1
            stack.extend(parents(node))
    for node in out_nodes:
        child_counts[id(node)] -= 1

    sorted_nodes = []
    childless_nodes = [node for node in out_nodes if not child_counts[id(node)]]
    while childless_nodes:
        node = childless_nodes.pop()
        sorted_nodes.append(node)
        for parent in parents(node):
            if child_counts[id(parent)] == 1:
                childless_nodes.append(parent)
            else:
                child_counts[id(parent)] -= 1

    sorted_nodes = sorted_nodes[::-1]
    check_toposort(sorted_nodes, parents)
    return sorted_nodes


def remove_duplicates(lst):
    seen = set()
    return [x for x in lst if id(x) not in seen and not seen.add(id(x))]


def check_toposort(nodes: ta.List[ta.Any], parents: ta.Callable[[ta.Any], ta.List[ta.Any]]):
    seen = set()
    for node in nodes:
        assert all(id(parent) in seen for parent in parents(node))
        seen.add(id(node))


##


def foo():
    y, sin_lin = linearize(sin, 3.)
    print(y, sin(3.))
    print(sin_lin(1.), cos(3.))
    print()


foo()


##


def xla_call_partial_eval(trace, tracers, *, jaxpr, num_consts):
    del num_consts  # Unused
    in_unknowns = [not t.pval.is_known for t in tracers]
    jaxpr1, jaxpr2, out_unknowns, num_res = partial_eval_jaxpr(jaxpr, in_unknowns)
    known_tracers, unknown_tracers = partition_list(in_unknowns, tracers)
    known_vals = [t.pval.const for t in known_tracers]
    outs1_res = bind(xla_call_p, *known_vals, jaxpr=jaxpr1, num_consts=0)
    outs1, res = split_list(outs1_res, len(jaxpr1.outs) - num_res)
    res_tracers = [trace.instantiate_const(full_raise(trace, x)) for x in res]
    outs2 = [PartialEvalTracer(trace, PartialVal.unknown(v.aval), None) for v in jaxpr2.outs]
    eqn = JaxprEqnRecipe(
        xla_call_p,
        res_tracers + unknown_tracers,
        dict(jaxpr=jaxpr2, num_consts=0),
        [v.aval for v in jaxpr2.outs],
        map_(weakref.ref, outs2),
    )
    for t in outs2:
        t.recipe = eqn
    return merge_lists(out_unknowns, outs1, outs2)


partial_eval_rules[xla_call_p] = xla_call_partial_eval


def partial_eval_jaxpr(
        jaxpr: Jaxpr,
        in_unknowns: ta.List[bool],
        instantiate: ta.Optional[ta.List[bool]] = None,
) -> ta.Tuple[Jaxpr, Jaxpr, ta.List[bool], int]:
    env: ta.Dict[Var, bool] = {}
    residuals: ta.Set[Var] = set()

    def read(x: Atom) -> bool:
        return type(x) is Var and env[x]

    def write(unk: bool, v: Var) -> None:
        env[v] = unk

    def new_res(x: Atom) -> Atom:
        if type(x) is Var:
            residuals.add(x)
        return x

    eqns1, eqns2 = [], []
    map_(write, in_unknowns, jaxpr.in_binders)
    for eqn in jaxpr.eqns:
        unks_in = map_(read, eqn.inputs)
        rule = partial_eval_jaxpr_rules.get(eqn.primitive)
        if rule:
            eqn1, eqn2, unks_out, res = rule(unks_in, eqn)
            eqns1.append(eqn1);
            eqns2.append(eqn2);
            residuals.update(res)
            map_(write, unks_out, eqn.out_binders)
        elif any(unks_in):
            inputs = [v if unk else new_res(v) for unk, v in zip(unks_in, eqn.inputs)]
            eqns2.append(JaxprEqn(eqn.primitive, inputs, eqn.params, eqn.out_binders))
            map_(functools.partial(write, True), eqn.out_binders)
        else:
            eqns1.append(eqn)
            map_(functools.partial(write, False), eqn.out_binders)
    out_unknowns = map_(read, jaxpr.outs)
    if instantiate is not None:
        for v, uk, inst in zip(jaxpr.outs, out_unknowns, instantiate):
            if inst and not uk:
                new_res(v)
        out_unknowns = map_(op.or_, out_unknowns, instantiate)

    residuals, num_res = list(residuals), len(residuals)
    assert all(type(v) is Var for v in residuals), residuals

    ins1, ins2 = partition_list(in_unknowns, jaxpr.in_binders)
    outs1, outs2 = partition_list(out_unknowns, jaxpr.outs)

    jaxpr1 = Jaxpr(ins1, eqns1, outs1 + residuals)
    jaxpr2 = Jaxpr(residuals + ins2, eqns2, outs2)
    typecheck_partial_eval_jaxpr(jaxpr, in_unknowns, out_unknowns, jaxpr1, jaxpr2)

    return jaxpr1, jaxpr2, out_unknowns, num_res


def typecheck_partial_eval_jaxpr(jaxpr, unks_in, unks_out, jaxpr1, jaxpr2):
    jaxprty = typecheck_jaxpr(jaxpr)  # (a1,  a2) -> (b1, b2 )
    jaxpr1ty = typecheck_jaxpr(jaxpr1)  # a1       -> (b1, res)
    jaxpr2ty = typecheck_jaxpr(jaxpr2)  # (res, a2) -> b2

    a1, a2 = partition_list(unks_in, jaxprty.in_types)
    b1, b2 = partition_list(unks_out, jaxprty.out_types)
    b1_, res = split_list(jaxpr1ty.out_types, len(b1))
    res_, a2_ = split_list(jaxpr2ty.in_types, len(res))
    b2_ = jaxpr2ty.out_types

    if jaxpr1ty.in_types != a1:
        raise TypeError
    if jaxpr2ty.out_types != b2:
        raise TypeError
    if b1 != b1_:
        raise TypeError
    if res != res_:
        raise TypeError
    if a2 != a2_:
        raise TypeError
    if b2 != b2_:
        raise TypeError


partial_eval_jaxpr_rules = {}


def xla_call_peval_eqn(
        unks_in: ta.List[bool],
        eqn: JaxprEqn,
) -> ta.Tuple[JaxprEqn, JaxprEqn, ta.List[bool], ta.List[Var]]:
    jaxpr = eqn.params['jaxpr']
    jaxpr1, jaxpr2, unks_out, num_res = partial_eval_jaxpr(jaxpr, unks_in)
    ins1, ins2 = partition_list(unks_in, eqn.inputs)
    out_binders1, out_binders2 = partition_list(unks_out, eqn.out_binders)
    residuals = [Var(v.aval) for v in jaxpr2.in_binders[:num_res]]
    eqn1 = JaxprEqn(xla_call_p, ins1, dict(jaxpr=jaxpr1, num_consts=0), out_binders1 + residuals)
    eqn2 = JaxprEqn(xla_call_p, residuals + ins2, dict(jaxpr=jaxpr2, num_consts=0), out_binders2)
    return eqn1, eqn2, unks_out, residuals


partial_eval_jaxpr_rules[xla_call_p] = xla_call_peval_eqn


##


def foo():
    @jit
    def f(x):
        y = sin(x) * 2.
        z = - y + x
        return z

    y, f_lin = linearize(f, 3.)
    y_dot = f_lin(1.)
    print(y, y_dot)

    @jit
    def f(x):
        y = sin(x) * 2.
        z = g(x, y)
        return z

    @jit
    def g(x, y):
        return cos(x) + y

    y, f_lin = linearize(f, 3.)
    y_dot = f_lin(1.)
    print(y, y_dot)

    print()


foo()


##


def vjp(f, x):
    y, f_lin = linearize(f, x)
    f_vjp = lambda y_bar: transpose(f_lin)(y_bar)
    return y, f_vjp


##


def vjp_flat(f, *primals_in):
    pvals_in = (
            [PartialVal.known(x) for x in primals_in] +
            [PartialVal.unknown(vspace(get_aval(x))) for x in primals_in]
    )
    primal_pvals_in, tangent_pvals_in = split_half(pvals_in)

    def f_jvp(*primals_tangents_in):
        primals_out, tangents_out = jvp(f, *split_half(primals_tangents_in))
        return [*primals_out, *tangents_out]

    jaxpr, pvals_out, consts = partial_eval_flat(f_jvp, pvals_in)  # linearize
    primal_pvals, _ = split_half(pvals_out)
    assert all(pval.is_known for pval in primal_pvals)
    primals_out = [pval.const for pval in primal_pvals]
    transpose_inputs = consts + [UndefPrimal(p.aval) for p in tangent_pvals_in]
    f_vjp = lambda *cts: eval_jaxpr_transposed(jaxpr, transpose_inputs, cts)
    return primals_out, f_vjp


def vjp(f, *primals_in):
    primals_in_flat, in_tree = tree_flatten(primals_in)
    f, out_tree = flatten_fun(f, in_tree)
    primals_out_flat, f_vjp_flat = vjp_flat(f, *primals_in_flat)
    primals_out = tree_unflatten(out_tree(), primals_out_flat)

    def f_vjp(*cotangents_out):
        cotangents_out_flat, _ = tree_flatten(cotangents_out)
        cotangents_in_flat = f_vjp_flat(*cotangents_out_flat)
        return tree_unflatten(in_tree, cotangents_in_flat)

    return primals_out, f_vjp


@dc.dataclass(frozen=True)
class UndefPrimal:
    aval: ShapedArray


register_pytree_node(UndefPrimal, lambda u: (u.aval, ()), lambda aval, _: UndefPrimal(aval))


##


# NB: the analogous function in JAX is called 'backward_pass'
def eval_jaxpr_transposed(jaxpr: Jaxpr, args: ta.List[ta.Any], cotangents: ta.List[ta.Any]) -> ta.List[ta.Any]:
    primal_env: ta.Dict[Var, ta.Any] = {}
    ct_env: ta.Dict[Var, ta.Any] = {}

    def read_primal(x: Atom) -> ta.Any:
        return primal_env.get(x, UndefPrimal(x.aval)) if type(x) is Var else x.val

    def write_primal(v: Var, val: ta.Any) -> None:
        if type(val) is not UndefPrimal:
            primal_env[v] = val

    def read_cotangent(v: Var) -> ta.Any:
        return ct_env.pop(v, np.zeros(v.aval.shape, v.aval.dtype))

    def write_cotangent(x: Atom, val: ta.Any):
        if type(x) is Var and val is not None:
            ct_env[x] = add(ct_env[x], val) if x in ct_env else val

    map_(write_primal, jaxpr.in_binders, args)
    map_(write_cotangent, jaxpr.outs, cotangents)
    for eqn in jaxpr.eqns[::-1]:
        primals_in = map_(read_primal, eqn.inputs)
        cts_in = map_(read_cotangent, eqn.out_binders)
        rule = transpose_rules[eqn.primitive]
        cts_out = rule(cts_in, *primals_in, **eqn.params)
        map_(write_cotangent, eqn.inputs, cts_out)

    return [read_cotangent(v) for v, x in zip(jaxpr.in_binders, args) if type(x) is UndefPrimal]


transpose_rules = {}


##


def mul_transpose_rule(cts, x, y):
    z_bar, = cts
    assert (type(x) is UndefPrimal) ^ (type(y) is UndefPrimal)
    return [mul(z_bar, y), None] if type(x) is UndefPrimal else [None, mul(x, z_bar)]


transpose_rules[mul_p] = mul_transpose_rule


def neg_transpose_rule(cts, x):
    ybar, = cts
    assert type(x) is UndefPrimal
    return [neg(ybar)]


transpose_rules[neg_p] = neg_transpose_rule


def add_transpose_rule(cts, x, y):
    z_bar, = cts
    return [z_bar, z_bar]


transpose_rules[add_p] = add_transpose_rule


def reduce_sum_transpose_rule(cts, x, *, axis):
    y_bar, = cts
    return [broadcast(y_bar, x.aval.shape, axis)]


transpose_rules[reduce_sum_p] = reduce_sum_transpose_rule


def xla_call_transpose_rule(cts, *invals, jaxpr, num_consts):
    del num_consts  # Unused
    undef_primals = [type(x) is UndefPrimal for x in invals]
    transposed_jaxpr, new_consts = transpose_jaxpr(jaxpr, tuple(undef_primals))
    residuals, _ = partition_list(undef_primals, invals)
    outs = bind(xla_call_p, *new_consts, *residuals, *cts, jaxpr=transposed_jaxpr, num_consts=len(new_consts))
    outs = iter(outs)
    return [next(outs) if undef else None for undef in undef_primals]


transpose_rules[xla_call_p] = xla_call_transpose_rule


@functools.lru_cache()
def transpose_jaxpr(jaxpr: Jaxpr, undef_primals: ta.Tuple[bool, ...]) -> ta.Tuple[Jaxpr, ta.List[ta.Any]]:
    avals_in, avals_out = (jt := typecheck_jaxpr(jaxpr)).in_types, jt.out_types
    traceable = functools.partial(eval_jaxpr_transposed, jaxpr)
    args = [UndefPrimal(a) if u else a for a, u in zip(avals_in, undef_primals)]
    trans_jaxpr, consts, _ = make_jaxpr(traceable, tuple(args), tuple(avals_out))
    typecheck_jaxpr(trans_jaxpr)
    return trans_jaxpr, consts


##


def grad(f):
    def gradfun(x, *xs):
        y, f_vjp = vjp(f, x, *xs)
        if np.shape(y) != ():
            raise TypeError
        x_bar, *_ = f_vjp(np.ones(np.shape(y), np.result_type(y)))
        return x_bar

    return gradfun


##


def foo():
    y, f_vjp = vjp(sin, 3.)
    print(f_vjp(1.), cos(3.))

    def f(x):
        y = sin(x) * 2.
        z = - y + x
        return z

    print(grad(f)(3.))

    @jit
    def f(x):
        y = x * 2.
        z = g(y)
        return z

    @jit
    def g(x):
        return cos(x) * 2.

    print(grad(f)(3.))

    # from core_test.py fun_with_nested_calls_2
    def foo(x):
        @jit
        def bar(y):
            def baz(w):
                q = jit(lambda x: y)(x)
                q = q + jit(lambda: y)()
                q = q + jit(lambda y: w + y)(y)
                q = jit(lambda w: jit(sin)(x) * y)(1.0) + q
                return q

            p, t = jvp(baz, (x + 1.0,), (y,))
            return t + (x * p)

        return bar(x)

    def assert_allclose(*vals):
        for v1, v2 in zip(vals[:-1], vals[1:]):
            np.testing.assert_allclose(v1, v2)

    ans1 = f(3.)
    ans2 = jit(f)(3.)
    ans3, _ = jvp(f, (3.,), (5.,))
    ans4, _ = jvp(jit(f), (3.,), (5.,))
    assert_allclose(ans1, ans2, ans3, ans4)

    deriv1 = grad(f)(3.)
    deriv2 = grad(jit(f))(3.)
    deriv3 = jit(grad(jit(f)))(3.)
    _, deriv4 = jvp(f, (3.,), (1.,))
    _, deriv5 = jvp(jit(f), (3.,), (1.,))
    assert_allclose(deriv1, deriv2, deriv3, deriv4, deriv5)

    hess1 = grad(grad(f))(3.)
    hess2 = grad(grad(jit(f)))(3.)
    hess3 = grad(jit(grad(f)))(3.)
    hess4 = jit(grad(grad(f)))(3.)
    _, hess5 = jvp(grad(f), (3.,), (1.,))
    _, hess6 = jvp(jit(grad(f)), (3.,), (1.,))
    _, hess7 = jvp(jit(grad(f)), (3.,), (1.,))
    assert_allclose(hess1, hess2, hess3, hess4, hess5, hess6, hess7)

    print()


foo()


##


def cond(pred, true_fn, false_fn, *operands):
    avals_in = [raise_to_shaped(get_aval(x)) for x in operands]
    true_jaxpr, true_consts, out_tree = make_jaxpr(true_fn, *avals_in)
    false_jaxpr, false_consts, out_tree_ = make_jaxpr(false_fn, *avals_in)
    if out_tree != out_tree_:
        raise TypeError
    true_jaxpr, false_jaxpr = _join_jaxpr_consts(
        true_jaxpr, false_jaxpr, len(true_consts), len(false_consts))
    if typecheck_jaxpr(true_jaxpr) != typecheck_jaxpr(false_jaxpr):
        raise TypeError
    outs = bind_cond(pred, *true_consts, *false_consts, *operands,
                     true_jaxpr=true_jaxpr, false_jaxpr=false_jaxpr)
    return tree_unflatten(out_tree, outs)


cond_p = Primitive('cond')


def _join_jaxpr_consts(jaxpr1: Jaxpr, jaxpr2: Jaxpr, n1: int, n2: int) -> ta.Tuple[Jaxpr, Jaxpr]:
    jaxpr1_type, jaxpr2_type = typecheck_jaxpr(jaxpr1), typecheck_jaxpr(jaxpr2)
    assert jaxpr1_type.in_types[n1:] == jaxpr2_type.in_types[n2:]
    consts1, rest1 = split_list(jaxpr1.in_binders, n1)
    consts2, rest2 = split_list(jaxpr2.in_binders, n2)
    new_jaxpr1 = Jaxpr(consts1 + consts2 + rest1, jaxpr1.eqns, jaxpr1.outs)
    new_jaxpr2 = Jaxpr(consts1 + consts2 + rest2, jaxpr2.eqns, jaxpr2.outs)
    return new_jaxpr1, new_jaxpr2


def bind_cond(pred, *args, true_jaxpr, false_jaxpr):
    assert len(args) == len(true_jaxpr.in_binders) == len(false_jaxpr.in_binders)
    return bind(cond_p, pred, *args, true_jaxpr=true_jaxpr, false_jaxpr=false_jaxpr)


##


def cond_impl(pred, *operands, true_jaxpr, false_jaxpr):
    if pred:
        return eval_jaxpr(true_jaxpr, operands)
    else:
        return eval_jaxpr(false_jaxpr, operands)


impl_rules[cond_p] = cond_impl


##


def foo():
    out = cond(True, lambda: 3, lambda: 4)
    print(out)

    print()


foo()


##


def cond_jvp_rule(primals, tangents, *, true_jaxpr, false_jaxpr):
    pred, *primals = primals
    _, *tangents = tangents
    true_jaxpr, true_consts = jvp_jaxpr(true_jaxpr)
    false_jaxpr, false_consts = jvp_jaxpr(false_jaxpr)
    true_jaxpr, false_jaxpr = _join_jaxpr_consts(
        true_jaxpr, false_jaxpr, len(true_consts), len(false_consts))
    assert typecheck_jaxpr(true_jaxpr) == typecheck_jaxpr(false_jaxpr)
    outs = bind_cond(pred, *true_consts, *false_consts, *primals, *tangents,
                     true_jaxpr=true_jaxpr, false_jaxpr=false_jaxpr)
    primals_out, tangents_out = split_half(outs)
    return primals_out, tangents_out


jvp_rules[cond_p] = cond_jvp_rule


def foo():
    out, out_tan = jvp(lambda x: cond(True, lambda: x * x, lambda: 0.), (1.,), (1.,))
    print(out_tan)

    print()


foo()


##


def cond_vmap_rule(axis_size, vals_in, dims_in, *, true_jaxpr, false_jaxpr):
    pred, *vals_in = vals_in
    pred_dim, *dims_in = dims_in
    if pred_dim is not not_mapped:
        raise NotImplementedError  # TODO
    true_jaxpr, true_consts = vmap_jaxpr(true_jaxpr, axis_size, tuple(dims_in))
    false_jaxpr, false_consts = vmap_jaxpr(false_jaxpr, axis_size, tuple(dims_in))
    true_jaxpr, false_jaxpr = _join_jaxpr_consts(
        true_jaxpr, false_jaxpr, len(true_consts), len(false_consts))
    assert typecheck_jaxpr(true_jaxpr) == typecheck_jaxpr(false_jaxpr)
    outs = bind_cond(pred, *true_consts, *false_consts, *vals_in,
                     true_jaxpr=true_jaxpr, false_jaxpr=false_jaxpr)
    return outs, [0] * len(outs)


vmap_rules[cond_p] = cond_vmap_rule


def foo():
    xs = np.array([1., 2., 3])
    out = vmap(lambda x: cond(True, lambda: x + 1., lambda: 0.), (0,))(xs)
    print(out)

    print()


foo()


##


def cond_abstract_eval(pred_type, *in_types, true_jaxpr, false_jaxpr):
    if pred_type != ShapedArray((), np.dtype('bool')):
        raise TypeError
    jaxpr_type = typecheck_jaxpr(true_jaxpr)
    if jaxpr_type != typecheck_jaxpr(false_jaxpr):
        raise TypeError
    if not all(t1 == t2 for t1, t2 in zip(jaxpr_type.in_types, in_types)):
        raise TypeError
    return jaxpr_type.out_types


abstract_eval_rules[cond_p] = cond_abstract_eval


def cond_translation(c, in_avals, in_vals, *, true_jaxpr, false_jaxpr):
    del in_avals  # Unused
    pred, *in_vals = in_vals
    flat_vals, in_tree = tree_flatten(in_vals)
    operand = xops.Tuple(c, flat_vals)
    operand_shape = c.get_shape(operand)

    def make_comp(name: str, jaxpr: Jaxpr) -> xe.XlaComputation:
        c = xc.XlaBuilder(name)
        operand = xops.Parameter(c, 0, operand_shape)
        operands = tree_unflatten(in_tree, destructure_tuple(c, operand))
        outs = jaxpr_subcomp(c, jaxpr, operands)
        return c.build(xops.Tuple(c, outs))

    true_comp = make_comp('true_fn', true_jaxpr)
    false_comp = make_comp('false_fn', false_jaxpr)

    int_etype = xc.dtype_to_etype(np.dtype('int32'))
    out = xops.Conditional(xops.ConvertElementType(pred, int_etype),
                           [false_comp, true_comp], [operand] * 2)
    return destructure_tuple(c, out)


xla_translations[cond_p] = cond_translation


##


def foo():
    out = jit(lambda: cond(False, lambda: 1, lambda: 2))()
    print(out)

    print()


foo()


##


def cond_partial_eval(trace, tracers, *, true_jaxpr, false_jaxpr):
    pred_tracer, *tracers = tracers
    assert pred_tracer.pval.is_known
    pred = pred_tracer.pval.const
    in_uks = [not t.pval.is_known for t in tracers]

    *jaxprs, out_uks, num_res = _cond_partial_eval(true_jaxpr, false_jaxpr, in_uks)
    t_jaxpr1, f_jaxpr1, t_jaxpr2, f_jaxpr2 = jaxprs

    known_tracers, unknown_tracers = partition_list(in_uks, tracers)
    known_vals = [t.pval.const for t in known_tracers]
    outs1_res = bind_cond(pred, *known_vals,
                          true_jaxpr=t_jaxpr1, false_jaxpr=f_jaxpr1)
    outs1, res = split_list(outs1_res, len(outs1_res) - num_res)
    pred_tracer_ = trace.instantiate_const(full_raise(trace, pred_tracer))
    res_tracers = [trace.instantiate_const(full_raise(trace, x)) for x in res]
    outs2 = [PartialEvalTracer(trace, PartialVal.unknown(v.aval), None) for v in t_jaxpr2.outs]
    eqn = JaxprEqnRecipe(
        cond_p,
        [pred_tracer_, *res_tracers, *unknown_tracers],
        dict(true_jaxpr=t_jaxpr2, false_jaxpr=f_jaxpr2),
        [v.aval for v in t_jaxpr2.outs],
        map_(weakref.ref, outs2),
    )
    for t in outs2:
        t.recipe = eqn
    return merge_lists(out_uks, outs1, outs2)


partial_eval_rules[cond_p] = cond_partial_eval


def _cond_partial_eval(
        true_jaxpr: Jaxpr,
        false_jaxpr: Jaxpr,
        in_uks: ta.List[bool]
) -> ta.Tuple[Jaxpr, Jaxpr, Jaxpr, Jaxpr, ta.List[bool], int]:
    _, _, t_out_uks, _ = partial_eval_jaxpr(true_jaxpr, in_uks)
    _, _, f_out_uks, _ = partial_eval_jaxpr(false_jaxpr, in_uks)
    out_uks = map_(op.or_, t_out_uks, f_out_uks)

    t_jaxpr1, t_jaxpr2, _, t_nres = partial_eval_jaxpr(true_jaxpr, in_uks, out_uks)
    f_jaxpr1, f_jaxpr2, _, f_nres = partial_eval_jaxpr(false_jaxpr, in_uks, out_uks)

    t_jaxpr1, f_jaxpr1 = _join_jaxpr_res(t_jaxpr1, f_jaxpr1, t_nres, f_nres)
    t_jaxpr2, f_jaxpr2 = _join_jaxpr_consts(t_jaxpr2, f_jaxpr2, t_nres, f_nres)
    assert typecheck_jaxpr(t_jaxpr1) == typecheck_jaxpr(f_jaxpr1)
    assert typecheck_jaxpr(t_jaxpr2) == typecheck_jaxpr(f_jaxpr2)
    num_res = t_nres + f_nres

    return t_jaxpr1, f_jaxpr1, t_jaxpr2, f_jaxpr2, out_uks, num_res


def _join_jaxpr_res(jaxpr1: Jaxpr, jaxpr2: Jaxpr, n1: int, n2: int) -> ta.Tuple[Jaxpr, Jaxpr]:
    jaxpr1_type, jaxpr2_type = typecheck_jaxpr(jaxpr1), typecheck_jaxpr(jaxpr2)
    out_types1, _ = split_list(jaxpr1_type.out_types, len(jaxpr1.outs) - n1)
    out_types2, _ = split_list(jaxpr2_type.out_types, len(jaxpr2.outs) - n2)
    assert out_types1 == out_types2
    outs1, res1 = split_list(jaxpr1.outs, len(jaxpr1.outs) - n1)
    outs2, res2 = split_list(jaxpr2.outs, len(jaxpr2.outs) - n2)
    zeros_like1 = [Lit(np.zeros(v.aval.shape, v.aval.dtype)) for v in res1]
    zeros_like2 = [Lit(np.zeros(v.aval.shape, v.aval.dtype)) for v in res2]
    new_jaxpr1 = Jaxpr(jaxpr1.in_binders, jaxpr1.eqns, outs1 + res1 + zeros_like2)
    new_jaxpr2 = Jaxpr(jaxpr2.in_binders, jaxpr2.eqns, outs2 + zeros_like1 + res2)
    return new_jaxpr1, new_jaxpr2


##


def foo():
    _, f_lin = linearize(lambda x: cond(True, lambda: x, lambda: 0.), 1.)
    out = f_lin(3.14)
    print(out)

    print()


foo()


##


def cond_peval_eqn(
        unks_in: ta.List[bool],
        eqn: JaxprEqn,
) -> ta.Tuple[JaxprEqn, JaxprEqn, ta.List[bool], ta.List[Atom]]:
    pred_unk, *unks_in = unks_in
    assert not pred_unk
    true_jaxpr, false_jaxpr = eqn.params['true_jaxpr'], eqn.params['false_jaxpr']
    *jaxprs, unks_out, num_res = _cond_partial_eval(true_jaxpr, false_jaxpr, unks_in)
    t_jaxpr1, f_jaxpr1, t_jaxpr2, f_jaxpr2 = jaxprs
    ins1, ins2 = partition_list(unks_in, eqn.inputs[1:])
    outs1, outs2 = partition_list(unks_out, eqn.out_binders)
    residuals, _ = split_list(t_jaxpr2.in_binders, num_res)
    eqn1 = JaxprEqn(
        cond_p,
        [eqn.inputs[0], *ins1],
        dict(true_jaxpr=t_jaxpr1, false_jaxpr=f_jaxpr1),
        outs1 + residuals,
    )
    eqn2 = JaxprEqn(
        cond_p,
        [eqn.inputs[0], *residuals, *ins2],
        dict(true_jaxpr=t_jaxpr2, false_jaxpr=f_jaxpr2),
        outs2,
    )
    res = [eqn.inputs[0], *residuals] if type(eqn.inputs[0]) is Var else residuals
    return eqn1, eqn2, unks_out, res


partial_eval_jaxpr_rules[cond_p] = cond_peval_eqn


def foo():
    _, f_lin = linearize(jit(lambda x: cond(True, lambda: x, lambda: 0.)), 1.)
    out = f_lin(3.14)
    print(out)

    print()


foo()


##


def cond_transpose_rule(cts, pred, *invals, true_jaxpr, false_jaxpr):
    undef_primals = tuple(type(x) is UndefPrimal for x in invals)
    true_jaxpr, true_consts = transpose_jaxpr(true_jaxpr, undef_primals)
    false_jaxpr, false_consts = transpose_jaxpr(false_jaxpr, undef_primals)
    true_jaxpr, false_jaxpr = _join_jaxpr_consts(true_jaxpr, false_jaxpr, len(true_consts), len(false_consts))
    res = [x for x in invals if type(x) is not UndefPrimal]
    outs = bind_cond(pred, *true_consts, *false_consts, *res, *cts,
                     true_jaxpr=true_jaxpr, false_jaxpr=false_jaxpr)
    outs = iter(outs)
    return [None] + [next(outs) if type(x) is UndefPrimal else None for x in invals]


transpose_rules[cond_p] = cond_transpose_rule


def foo():
    out = grad(lambda x: cond(True, lambda: x * x, lambda: 0.))(1.)
    print(out)

    print()


foo()

##


# from typing import DefaultDict
#
#
# def pprint_cond(names: DefaultDict[Var, str], eqn: JaxprEqn) -> PPrint:
#     true_jaxpr, false_jaxpr = eqn.params['true_jaxpr'], eqn.params['false_jaxpr']
#     new_params = {k: v for k, v in eqn.params.items() if not k.endswith('jaxpr')}
#     lhs = pp(' '.join(var_str(names, v) for v in eqn.out_binders))
#     rhs = (pp(eqn.primitive.name) >> pp_params(new_params) >>
#            pp(' '.join(names[x] if isinstance(x, Var) else str(x.val)
#                        for x in eqn.inputs)))
#     return vcat([lhs >> pp(' = ') >> rhs,
#                  pp_jaxpr(true_jaxpr).indent(2),
#                  pp_jaxpr(false_jaxpr).indent(2)])
#
#
# pp_rules[cond_p] = pprint_cond
