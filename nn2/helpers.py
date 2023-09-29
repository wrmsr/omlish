from __future__ import annotations

import contextlib
import functools
import operator
import os
import pathlib
import platform
import re
import tempfile
import time
import typing as ta

if ta.TYPE_CHECKING:  # TODO: remove this and import TypeGuard from typing once minimum python supported version is 3.10
    from typing_extensions import TypeGuard


T = ta.TypeVar("T")


# NOTE: it returns int 1 if x is empty regardless of the type of x
def prod(x: ta.Iterable[T]) -> ta.Union[T, int]:
    return functools.reduce(operator.__mul__, x, 1)


# NOTE: helpers is not allowed to import from anything else in tinygrad
OSX = platform.system() == "Darwin"


def dedup(x):
    return list(dict.fromkeys(x))  # retains list order


def argfix(*x):
    return tuple(x[0]) if x and x[0].__class__ in (tuple, list) else x


def argsort(x):
    return type(x)(
        sorted(range(len(x)), key=x.__getitem__)
    )  # https://stackoverflow.com/questions/3382352/equivalent-of-numpy-argsort-in-basic-python


def all_same(items):
    return all(x == items[0] for x in items)


def all_int(t: tuple[ta.Any, ...]) -> TypeGuard[tuple[int, ...]]:
    return all(isinstance(s, int) for s in t)


def colored(st, color, background=False):
    return (
        f"\u001b[{10*background+60*(color.upper() == color)+30+['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'].index(color.lower())}m{st}\u001b[0m"  # noqa
        if color is not None
        else st
    )  # replace the termcolor library with one line


def ansilen(s):
    return len(re.sub("\x1b\\[(K|.*?m)", "", s))


def make_pair(x: ta.Union[int, tuple[int, ...]], cnt=2) -> tuple[int, ...]:
    return (x,) * cnt if isinstance(x, int) else x


def flatten(l: ta.Iterator):
    return [item for sublist in l for item in sublist]


def fromimport(mod, frm):
    return getattr(__import__(mod, fromlist=[frm]), frm)


def strip_parens(fst):
    return (
        fst[1:-1]
        if fst[0] == "("
        and fst[-1] == ")"
        and fst[1:-1].find("(") <= fst[1:-1].find(")")
        else fst
    )


def merge_dicts(ds: ta.Iterable[dict]) -> dict:
    assert len(kvs := set([(k, v) for d in ds for k, v in d.items()])) == len(
        set(kv[0] for kv in kvs)
    ), f"cannot merge, {kvs} contains different values for the same key"
    return {k: v for d in ds for k, v in d.items()}


def partition(lst, fxn):
    a: list[ta.Any] = []
    b: list[ta.Any] = []
    for s in lst:
        (a if fxn(s) else b).append(s)
    return a, b


@functools.lru_cache(maxsize=None)
def getenv(key, default=0):
    return type(default)(os.getenv(key, default))


class Context(contextlib.ContextDecorator):
    stack: ta.ClassVar[list[dict[str, int]]] = [{}]

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        Context.stack[-1] = {
            k: o.value for k, o in ContextVar._cache.items()
        }  # Store current state.
        for k, v in self.kwargs.items():
            ContextVar._cache[k].value = v  # Update to new temporary state.
        Context.stack.append(
            self.kwargs
        )  # Store the temporary state so we know what to undo later.

    def __exit__(self, *args):
        for k in Context.stack.pop():
            ContextVar._cache[k].value = Context.stack[-1].get(
                k, ContextVar._cache[k].value
            )


class ContextVar:
    _cache: ta.ClassVar[dict[str, ContextVar]] = {}
    value: int

    def __new__(cls, key, default_value):
        if key in ContextVar._cache:
            return ContextVar._cache[key]
        instance = ContextVar._cache[key] = super().__new__(cls)
        instance.value = getenv(key, default_value)
        return instance

    def __bool__(self):
        return bool(self.value)

    def __ge__(self, x):
        return self.value >= x

    def __gt__(self, x):
        return self.value > x

    def __lt__(self, x):
        return self.value < x


DEBUG, IMAGE = ContextVar("DEBUG", 0), ContextVar("IMAGE", 0)
GRAPH, PRUNEGRAPH, GRAPHPATH = (
    getenv("GRAPH", 0),
    getenv("PRUNEGRAPH", 0),
    getenv("GRAPHPATH", "/tmp/net"),
)


class Timing(contextlib.ContextDecorator):
    def __init__(self, prefix="", on_exit=None, enabled=True):
        self.prefix, self.on_exit, self.enabled = prefix, on_exit, enabled

    def __enter__(self):
        self.st = time.perf_counter_ns()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.et = time.perf_counter_ns() - self.st
        if self.enabled:
            print(
                f"{self.prefix}{self.et*1e-6:.2f} ms"
                + (self.on_exit(self.et) if self.on_exit else "")
            )


class GlobalCounters:
    global_ops: ta.ClassVar[int] = 0
    global_mem: ta.ClassVar[int] = 0
    time_sum_s: ta.ClassVar[float] = 0.0
    kernel_count: ta.ClassVar[int] = 0
    mem_used: ta.ClassVar[int] = 0  # NOTE: this is not reset
    mem_cached: ta.ClassVar[int] = 0  # NOTE: this is not reset

    @staticmethod
    def reset():
        (
            GlobalCounters.global_ops,
            GlobalCounters.global_mem,
            GlobalCounters.time_sum_s,
            GlobalCounters.kernel_count,
        ) = (0, 0, 0.0, 0)


def temp_file(x: str) -> str:
    return (pathlib.Path(tempfile.gettempdir()) / x).as_posix()
