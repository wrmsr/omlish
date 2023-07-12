import contextlib
import dataclasses as dc
import operator as op
import typing as ta


@dc.dataclass(frozen=True)
class MainTrace:
    level: int
    trace_type: ta.Type['Trace']
    global_data: ta.Optional[ta.Any]


trace_stack: ta.List[MainTrace] = []
dynamic_trace: ta.Optional[MainTrace] = None  # to be employed in Part 3


@contextlib.contextmanager
def new_main(trace_type: ta.Type['Trace'], global_data=None):
    level = len(trace_stack)
    main = MainTrace(level, trace_type, global_data)
    trace_stack.append(main)

    try:
        yield main
    finally:
        trace_stack.pop()


class Trace:
    main: MainTrace

    def __init__(self, main: MainTrace) -> None:
        self.main = main

    # @abc.abstractmethod
    def pure(self, val) -> ta.Any:
        raise NotImplementedError

    # @abc.abstractmethod
    def lift(self, val) -> ta.Any:
        raise NotImplementedError

    # @abc.abstractmethod
    def process_primitive(self, primitive, tracers, params):
        raise NotImplementedError


class Tracer:
    _trace: Trace

    __array_priority__ = 1000

    @property
    # @abc.abstractmethod
    def aval(self) -> ta.Any:
        raise NotImplementedError

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


def bind(prim, *args, **params):
    top_trace = find_top_trace(args)
    tracers = [full_raise(top_trace, arg) for arg in args]
    outs = top_trace.process_primitive(prim, tracers, params)
    return [full_lower(out) for out in outs]


def bind1(prim, *args, **params):
    out, = bind(prim, *args, **params)
    return out


def find_top_trace(xs) -> Trace:
    top_main = max(
        (x._trace.main for x in xs if isinstance(x, Tracer)),
        default=trace_stack[0],
        key=op.attrgetter('level'),
    )
    if dynamic_trace and dynamic_trace.level > top_main.level:
        top_main = dynamic_trace
    return top_main.trace_type(top_main)


def full_lower(val: ta.Any):
    if isinstance(val, Tracer):
        return val.full_lower()
    else:
        return val


def full_raise(trace: Trace, val: ta.Any) -> Tracer:
    if not isinstance(val, Tracer):
        from .prims import jax_types
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
