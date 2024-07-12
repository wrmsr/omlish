"""
https://gist.github.com/amakelov/c48d1bfb2eec75385dd5df2d81dcd759
"""
import copy
import functools
import types
import typing as ta


class TracerState:
    current: ta.Optional['Tracer'] = None


CallableT = ta.TypeVar('CallableT', bound=ta.Callable)


def track(f: CallableT) -> CallableT:
    f = make_tracked_copy(f)

    @functools.wraps(f)  # to make the wrapped function look like `f`
    def wrapper(*args, **kwargs):
        tracer = TracerState.current
        if tracer is not None:
            tracer.register_call(func=f)  # put call to `f` on stack
            result = f(*args, **kwargs)
            tracer.register_return()  # pop call to `f` from stack
            return result
        else:
            return f(*args, **kwargs)

    return wrapper


class Tracer:
    class StackEntry(ta.NamedTuple):
        module_name: str
        qual_name: str

    class GraphCall(ta.NamedTuple):
        module_name: str
        qual_name: str

    class GraphGlobal(ta.NamedTuple):
        key: str
        value: ta.Any

    class GraphEntry(ta.NamedTuple):
        caller_module: str
        caller_qual_name: str
        op: ta.Union['Tracer.GraphCall', 'Tracer.GraphGlobal']

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[Tracer.StackEntry] = []
        self.graph: list[Tracer.GraphEntry] = []

    def register_call(self, func: ta.Callable) -> None:
        # Add a call to the stack and the graph
        module_name, qual_name = func.__module__, func.__qualname__
        self.stack.append(Tracer.StackEntry(module_name, qual_name))
        if len(self.stack) > 1:
            caller_module, caller_qual_name = self.stack[-2]
            self.graph.append(Tracer.GraphEntry(caller_module, caller_qual_name, Tracer.GraphCall(module_name, qual_name)))  # noqa

    def register_global_access(self, key: str, value: ta.Any) -> None:  # <- ADD THIS METHOD
        assert len(self.stack) > 0
        caller_module, caller_qual_name = self.stack[-1]
        self.graph.append(Tracer.GraphEntry(caller_module, caller_qual_name, Tracer.GraphGlobal(key, value)))

    def register_return(self) -> None:
        self.stack.pop()

    def __enter__(self) -> ta.Self:
        TracerState.current = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        TracerState.current = None


class TrackedDict(dict):
    def __init__(self, original: dict) -> None:
        super().__init__()
        self.__original__ = original

    def __getitem__(self, __key: str) -> ta.Any:
        value = self.__original__.__getitem__(__key)
        if TracerState.current is not None:
            tracer = TracerState.current
            tracer.register_global_access(key=__key, value=value)
        return value


def make_tracked_copy(f: types.FunctionType) -> types.FunctionType:
    result = types.FunctionType(
        code=f.__code__,
        globals=TrackedDict(f.__globals__),
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    functools.update_wrapper(result, f)
    result.__module__ = f.__module__
    result.__kwdefaults__ = copy.deepcopy(f.__kwdefaults__)
    result.__annotations__ = copy.deepcopy(f.__annotations__)
    return result


##


A = 23
B = 42


@track
def f(x):
    return x + A


class C:
    @track
    def __init__(self, x):
        self.x = x + B

    @track
    def m(self, y):
        return self.x + y

    class D:
        @track
        def __init__(self, x):
            self.x = x + f(x)

        @track
        def m(self, y):
            return y + A


@track
def g(x):
    if x % 2 == 0:
        return C(x).m(x)
    else:
        return C.D(x).m(x)


if __name__ == '__main__':
    import pprint
    with Tracer() as t:
        g(23)
    pprint.pprint(t.graph)
    with Tracer() as t:
        g(42)
    pprint.pprint(t.graph)
