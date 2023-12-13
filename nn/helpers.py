from __future__ import annotations

import cProfile
import contextlib
import ctypes
import functools
import hashlib
import operator
import os
import pathlib
import pickle
import platform
import pstats
import re
import sqlite3
import string
import tempfile
import time
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Dict
from typing import Final
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set
from typing import TYPE_CHECKING
from typing import Tuple
from typing import TypeVar
from typing import Union
from urllib import request

import numpy as np
from tqdm import tqdm

if (
    TYPE_CHECKING
):  # TODO: remove this and import TypeGuard from typing once minimum python supported version is 3.10
    from typing_extensions import TypeGuard

T = TypeVar("T")
U = TypeVar("U")


# NOTE: it returns int 1 if x is empty regardless of the type of x
def prod(x: Iterable[T]) -> Union[T, int]:
    return functools.reduce(operator.__mul__, x, 1)


# NOTE: helpers is not allowed to import from anything else in tinygrad
OSX = platform.system() == "Darwin"
CI = os.getenv("CI", "") != ""


def dedup(x: Iterable[T]):
    return list(dict.fromkeys(x))  # retains list order


def argfix(*x):
    return tuple(x[0]) if x and x[0].__class__ in (tuple, list) else x


def argsort(x):
    return type(x)(
        sorted(range(len(x)), key=x.__getitem__)
    )  # https://stackoverflow.com/questions/3382352/equivalent-of-numpy-argsort-in-basic-python


def all_same(items: List[T]):
    return all(x == items[0] for x in items)


def all_int(t: Tuple[Any, ...]) -> TypeGuard[Tuple[int, ...]]:
    return all(isinstance(s, int) for s in t)


def colored(st, color: Optional[str], background=False):
    return (
        f"\u001b[{10*background+60*(color.upper() == color)+30+['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'].index(color.lower())}m{st}\u001b[0m"
        if color is not None
        else st
    )  # replace the termcolor library with one line  # noqa: E501


def ansistrip(s: str):
    return re.sub("\x1b\\[(K|.*?m)", "", s)


def ansilen(s: str):
    return len(ansistrip(s))


def make_pair(x: Union[int, Tuple[int, ...]], cnt=2) -> Tuple[int, ...]:
    return (x,) * cnt if isinstance(x, int) else x


def flatten(l: Iterable[Iterable[T]]):
    return [item for sublist in l for item in sublist]


def fromimport(mod, frm):
    return getattr(__import__(mod, fromlist=[frm]), frm)


def strip_parens(fst: str):
    return (
        fst[1:-1]
        if fst[0] == "("
        and fst[-1] == ")"
        and fst[1:-1].find("(") <= fst[1:-1].find(")")
        else fst
    )


def round_up(num, amt: int):
    return (num + amt - 1) // amt * amt


def merge_dicts(ds: Iterable[Dict[T, U]]) -> Dict[T, U]:
    assert len(kvs := set([(k, v) for d in ds for k, v in d.items()])) == len(
        set(kv[0] for kv in kvs)
    ), f"cannot merge, {kvs} contains different values for the same key"  # noqa: E501
    return {k: v for d in ds for k, v in d.items()}


def partition(lst: List[T], fxn: Callable[[T], bool]):
    a: List[T] = []
    b: List[T] = []
    for s in lst:
        (a if fxn(s) else b).append(s)
    return a, b


def unwrap(x: Optional[T]) -> T:
    assert x is not None
    return x


def unwrap2(x: Tuple[T, Any]) -> T:
    ret, err = x
    assert err is None, str(err)
    return ret


def get_child(obj, key):
    for k in key.split("."):
        if k.isnumeric():
            obj = obj[int(k)]
        elif isinstance(obj, dict):
            obj = obj[k]
        else:
            obj = getattr(obj, k)
    return obj


@functools.lru_cache(maxsize=None)
def to_function_name(s: str):
    return "".join(
        [
            c if c in (string.ascii_letters + string.digits + "_") else f"{ord(c):02X}"
            for c in ansistrip(s)
        ]
    )


@functools.lru_cache(maxsize=None)
def getenv(key: str, default=0):
    return type(default)(os.getenv(key, default))


def temp(x: str) -> str:
    return (pathlib.Path(tempfile.gettempdir()) / x).as_posix()


class Context(contextlib.ContextDecorator):
    stack: ClassVar[List[dict[str, int]]] = [{}]

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
    _cache: ClassVar[Dict[str, ContextVar]] = {}
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


DEBUG, IMAGE, BEAM, NOOPT = (
    ContextVar("DEBUG", 0),
    ContextVar("IMAGE", 0),
    ContextVar("BEAM", 0),
    ContextVar("NOOPT", 0),
)
GRAPH, GRAPHPATH = getenv("GRAPH", 0), getenv("GRAPHPATH", "/tmp/net")


class Timing(contextlib.ContextDecorator):
    def __init__(self, prefix="", on_exit=None, enabled=True):
        self.prefix, self.on_exit, self.enabled = prefix, on_exit, enabled

    def __enter__(self):
        self.st = time.perf_counter_ns()

    def __exit__(self, *exc):
        self.et = time.perf_counter_ns() - self.st
        if self.enabled:
            print(
                f"{self.prefix}{self.et*1e-6:.2f} ms"
                + (self.on_exit(self.et) if self.on_exit else "")
            )


class Profiling(contextlib.ContextDecorator):
    def __init__(self, enabled=True, sort="cumtime", frac=0.2):
        self.enabled, self.sort, self.frac = enabled, sort, frac

    def __enter__(self):
        self.pr = cProfile.Profile(timer=lambda: int(time.time() * 1e9), timeunit=1e-6)
        if self.enabled:
            self.pr.enable()

    def __exit__(self, *exc):
        if self.enabled:
            self.pr.disable()
            pstats.Stats(self.pr).strip_dirs().sort_stats(self.sort).print_stats(
                self.frac
            )


# **** tinygrad now supports dtypes! *****


# TODO: migrate this from NamedTuple -> dataclass
class DType(NamedTuple):
    priority: int  # this determines when things get upcasted
    itemsize: int
    name: str
    np: Optional[
        type
    ]  # TODO: someday this will be removed with the "remove numpy" project
    sz: int = 1

    def __repr__(self):
        return (
            f"dtypes.{INVERSE_DTYPES_DICT[self]}"
            if self.sz == 1
            else f"dtypes._{INVERSE_DTYPES_DICT[self.scalar()]}{self.sz}"
        )

    def vec(self, sz: int):
        assert sz > 1 and self.sz == 1, f"can't vectorize {self} with size {sz}"
        return DType(
            self.priority,
            self.itemsize * sz,
            f"{INVERSE_DTYPES_DICT[self]}{str(sz)}",
            None,
            sz,
        )

    def scalar(self):
        return DTYPES_DICT[self.name[: -len(str(self.sz))]] if self.sz > 1 else self


# dependent typing?
class ImageDType(DType):
    def __new__(cls, priority, itemsize, name, np, shape, base):
        return super().__new__(cls, priority, itemsize, name, np)

    def __init__(self, priority, itemsize, name, np, shape, base):
        self.shape: Tuple[
            int, ...
        ] = shape  # arbitrary arg for the dtype, used in image for the shape
        self.base: DType = base
        super().__init__()

    def scalar(self):
        return self.base

    def vec(self, sz: int):
        return self.base.vec(sz)

    def __repr__(self):
        return f"dtypes.{self.name}({self.shape})"

    # TODO: fix this to not need these
    def __hash__(self):
        return hash((super().__hash__(), self.shape))

    def __eq__(self, x):
        return super().__eq__(x) and self.shape == x.shape

    def __ne__(self, x):
        return super().__ne__(x) or self.shape != x.shape


class PtrDType(DType):
    def __new__(cls, dt: DType):
        return super().__new__(cls, dt.priority, dt.itemsize, dt.name, dt.np, dt.sz)

    def __repr__(self):
        return f"ptr.{super().__repr__()}"


class dtypes:
    @staticmethod
    def is_float(x: DType) -> bool:
        return x.scalar() in (dtypes.float16, dtypes.float32, dtypes.float64)

    @staticmethod  # static methds on top, or bool in the type info will refer to dtypes.bool
    def is_int(x: DType) -> bool:
        return x.scalar() in (
            dtypes.int8,
            dtypes.int16,
            dtypes.int32,
            dtypes.int64,
        ) or dtypes.is_unsigned(x)

    @staticmethod
    def is_unsigned(x: DType) -> bool:
        return x.scalar() in (dtypes.uint8, dtypes.uint16, dtypes.uint32, dtypes.uint64)

    @staticmethod
    def from_np(x) -> DType:
        return DTYPES_DICT[np.dtype(x).name]

    @staticmethod
    def fields() -> Dict[str, DType]:
        return DTYPES_DICT

    bool: Final[DType] = DType(0, 1, "bool", np.bool_)
    float16: Final[DType] = DType(9, 2, "half", np.float16)
    half = float16
    float32: Final[DType] = DType(11, 4, "float", np.float32)
    float = float32
    float64: Final[DType] = DType(12, 8, "double", np.float64)
    double = float64
    int8: Final[DType] = DType(1, 1, "char", np.int8)
    char = int8
    int16: Final[DType] = DType(3, 2, "short", np.int16)
    short = int16
    int32: Final[DType] = DType(5, 4, "int", np.int32)
    int = int32
    int64: Final[DType] = DType(7, 8, "long", np.int64)
    long = int64
    uint8: Final[DType] = DType(2, 1, "unsigned char", np.uint8)
    uchar = uint8
    uint16: Final[DType] = DType(4, 2, "unsigned short", np.uint16)
    ushort = uint16
    uint32: Final[DType] = DType(6, 4, "unsigned int", np.uint32)
    uint = uint32
    uint64: Final[DType] = DType(8, 8, "unsigned long", np.uint64)
    ulong = uint64

    # NOTE: bfloat16 isn't supported in numpy
    # it has higher priority than float16, so least_upper_dtype(dtypes.int64, dtypes.uint64) = dtypes.float16
    bfloat16: Final[DType] = DType(10, 2, "__bf16", None)

    # NOTE: these are internal dtypes, should probably check for that
    _arg_int32: Final[DType] = DType(2, 4, "_arg_int32", None)

    # NOTE: these are image dtypes
    @staticmethod
    def imageh(shp):
        return ImageDType(100, 2, "imageh", np.float16, shp, dtypes.float32)

    @staticmethod
    def imagef(shp):
        return ImageDType(100, 4, "imagef", np.float32, shp, dtypes.float32)


# https://jax.readthedocs.io/en/latest/jep/9407-type-promotion.html
# we don't support weak type and complex type
promo_lattice = {
    dtypes.bool: [dtypes.int8, dtypes.uint8],
    dtypes.int8: [dtypes.int16],
    dtypes.int16: [dtypes.int32],
    dtypes.int32: [dtypes.int64],
    dtypes.int64: [dtypes.float16, dtypes.bfloat16],
    dtypes.uint8: [dtypes.int16, dtypes.uint16],
    dtypes.uint16: [dtypes.int32, dtypes.uint32],
    dtypes.uint32: [dtypes.int64, dtypes.uint64],
    dtypes.uint64: [dtypes.float16, dtypes.bfloat16],
    dtypes.float16: [dtypes.float32],
    dtypes.bfloat16: [dtypes.float32],
    dtypes.float32: [dtypes.float64],
}


@functools.lru_cache(None)
def _get_recursive_parents(dtype: DType) -> Set[DType]:
    return (
        set.union(*[_get_recursive_parents(d) for d in promo_lattice[dtype]], {dtype})
        if dtype != dtypes.float64
        else {dtypes.float64}
    )


@functools.lru_cache(None)
def least_upper_dtype(*ds: DType) -> DType:
    return (
        min(set.intersection(*[_get_recursive_parents(d) for d in ds]))
        if not (images := [d for d in ds if isinstance(d, ImageDType)])
        else images[0]
    )


# HACK: staticmethods are not callable in 3.8 so we have to compare the class
DTYPES_DICT = {
    k: v
    for k, v in dtypes.__dict__.items()
    if not k.startswith("__") and not callable(v) and v.__class__ is not staticmethod
}
INVERSE_DTYPES_DICT = {v: k for k, v in DTYPES_DICT.items()}


class GlobalCounters:
    global_ops: ClassVar[int] = 0
    global_mem: ClassVar[int] = 0
    time_sum_s: ClassVar[float] = 0.0
    kernel_count: ClassVar[int] = 0
    mem_used: ClassVar[int] = 0  # NOTE: this is not reset

    @staticmethod
    def reset():
        (
            GlobalCounters.global_ops,
            GlobalCounters.global_mem,
            GlobalCounters.time_sum_s,
            GlobalCounters.kernel_count,
        ) = (0, 0, 0.0, 0)


# *** universal database cache ***

_cache_dir: str = getenv(
    "XDG_CACHE_HOME", os.path.expanduser("~/Library/Caches" if OSX else "~/.cache")
)
CACHEDB: str = getenv(
    "CACHEDB", os.path.abspath(os.path.join(_cache_dir, "tinygrad", "cache.db"))
)
CACHELEVEL = getenv("CACHELEVEL", 2)

VERSION = 10
_db_connection = None


def db_connection():
    global _db_connection
    if _db_connection is None:
        os.makedirs(CACHEDB.rsplit(os.sep, 1)[0], exist_ok=True)
        _db_connection = sqlite3.connect(CACHEDB)
        if DEBUG >= 7:
            _db_connection.set_trace_callback(print)
    return _db_connection


def diskcache_get(table: str, key: Union[Dict, str, int]) -> Any:
    if CACHELEVEL == 0:
        return None
    if isinstance(key, (str, int)):
        key = {"key": key}
    conn = db_connection()
    cur = conn.cursor()
    try:
        res = cur.execute(
            f"SELECT val FROM {table}_{VERSION} WHERE {' AND '.join([f'{x}=?' for x in key.keys()])}",
            tuple(key.values()),
        )
    except sqlite3.OperationalError:
        return None  # table doesn't exist
    if (val := res.fetchone()) is not None:
        return pickle.loads(val[0])
    return None


_db_tables = set()


def diskcache_put(table: str, key: Union[Dict, str, int], val: Any):
    if CACHELEVEL == 0:
        return val
    if isinstance(key, (str, int)):
        key = {"key": key}
    conn = db_connection()
    cur = conn.cursor()
    if table not in _db_tables:
        TYPES = {
            str: "text",
            bool: "integer",
            int: "integer",
            float: "numeric",
            bytes: "blob",
        }
        ltypes = ", ".join(f"{k} {TYPES[type(key[k])]}" for k in key.keys())
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {table}_{VERSION} ({ltypes}, val blob, PRIMARY KEY ({', '.join(key.keys())}))"
        )
        _db_tables.add(table)
    cur.execute(
        f"REPLACE INTO {table}_{VERSION} ({', '.join(key.keys())}, val) VALUES ({', '.join(['?']*len(key.keys()))}, ?)",
        tuple(key.values()) + (pickle.dumps(val),),
    )  # noqa: E501
    conn.commit()
    cur.close()
    return val


def diskcache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> bytes:
        table, key = (
            f"cache_{func.__name__}",
            hashlib.sha256(pickle.dumps((args, kwargs))).hexdigest(),
        )
        if ret := diskcache_get(table, key):
            return ret
        return diskcache_put(table, key, func(*args, **kwargs))

    setattr(wrapper, "__wrapped__", func)
    return wrapper


# *** http support ***


def fetch(
    url: str,
    name: Optional[Union[pathlib.Path, str]] = None,
    allow_caching=not getenv("DISABLE_HTTP_CACHE"),
) -> pathlib.Path:
    if url.startswith("/") or url.startswith("."):
        return pathlib.Path(url)
    fp = (
        pathlib.Path(name)
        if name is not None and (isinstance(name, pathlib.Path) or "/" in name)
        else pathlib.Path(_cache_dir)
        / "tinygrad"
        / "downloads"
        / (name if name else hashlib.md5(url.encode("utf-8")).hexdigest())
    )  # noqa: E501
    if not fp.is_file() or not allow_caching:
        with request.urlopen(url, timeout=10) as r:
            assert r.status == 200
            total_length = int(r.headers.get("content-length", 0))
            progress_bar = tqdm(total=total_length, unit="B", unit_scale=True, desc=url)
            (path := fp.parent).mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path, delete=False) as f:
                while chunk := r.read(16384):
                    progress_bar.update(f.write(chunk))
                f.close()
                if (file_size := os.stat(f.name).st_size) < total_length:
                    raise RuntimeError(
                        f"fetch size incomplete, {file_size} < {total_length}"
                    )
                pathlib.Path(f.name).rename(fp)
    return fp


# *** Exec helpers


def cpu_time_execution(cb, enable):
    if enable:
        st = time.perf_counter()
    cb()
    if enable:
        return time.perf_counter() - st


# *** ctypes helpers


# TODO: make this work with read only memoryviews (if possible)
def from_mv(mv, to_type=ctypes.c_char):
    return ctypes.cast(
        ctypes.addressof(to_type.from_buffer(mv)), ctypes.POINTER(to_type)
    )


def to_char_p_p(options: List[bytes], to_type=ctypes.c_char):
    return (ctypes.POINTER(to_type) * len(options))(
        *[
            ctypes.cast(ctypes.create_string_buffer(o), ctypes.POINTER(to_type))
            for o in options
        ]
    )  # noqa: E501


@functools.lru_cache(maxsize=None)
def init_c_struct_t(fields: Tuple[Tuple[str, ctypes._SimpleCData], ...]):
    class CStruct(ctypes.Structure):
        _pack_, _fields_ = 1, fields

    return CStruct


def init_c_var(ctypes_var, creat_cb):
    return (creat_cb(ctypes_var), ctypes_var)[1]


def get_bytes(arg, get_sz, get_str, check) -> bytes:
    return (
        sz := init_c_var(
            ctypes.c_size_t(), lambda x: check(get_sz(arg, ctypes.byref(x)))
        ),
        ctypes.string_at(
            init_c_var(
                ctypes.create_string_buffer(sz.value), lambda x: check(get_str(arg, x))
            ),
            size=sz.value,
        ),
    )[
        1
    ]  # noqa: E501


def flat_mv(mv: memoryview):
    if len(mv) == 0:
        return mv
    return mv.cast("B", shape=(mv.nbytes,))


# *** Helpers for CUDA-like APIs.


def pretty_ptx(s):
    # all expressions match `<valid_before><expr><valid_after>` and replace it with `<valid_before>color(<expr>)<valid_after>`
    s = re.sub(
        r"([!@<\[\s,\+\-;\n])((?:[_%$][\w%\$_]+(?:\.[xyz])?\:?)|(?:buf\d+))([<>\]\s,\+\-;\n\)])",
        lambda m: m[1] + colored(m[2], "blue") + m[3],
        s,
        flags=re.M,
    )  # identifiers  # noqa: E501
    s = re.sub(
        r"(.)((?:b|s|u|f)(?:8|16|32|64)|pred)([\.\s])",
        lambda m: m[1] + colored(m[2], "green") + m[3],
        s,
        flags=re.M,
    )  # types
    s = re.sub(
        r"^(\s*)([\w]+)(.*?;$)",
        lambda m: m[1] + colored(m[2], "yellow") + m[3],
        s,
        flags=re.M,
    )  # instructions
    s = re.sub(
        r"([<>\[\]\s,\+\-;])((?:0[fF][0-9a-fA-F]{8})|(?:[0-9]+)|(?:0[xX][0-9a-fA-F]+))([<>\[\]\s,\+\-;])",
        lambda m: m[1] + colored(m[2], "yellow") + m[3],
        s,
        flags=re.M,
    )  # numbers  # noqa: E501
    s = re.sub(
        r"(\.)(param|reg|global)",
        lambda m: m[1] + colored(m[2], "magenta"),
        s,
        flags=re.M,
    )  # space
    s = re.sub(
        r"(\.)(version|target|address_size|visible|entry)",
        lambda m: m[1] + colored(m[2], "magenta"),
        s,
        flags=re.M,
    )  # derivatives
    return s


def compile_cuda_style(
    prg,
    compile_options,
    prog_t,
    create_prog,
    compile_prog,
    get_code,
    get_code_size,
    get_log,
    get_log_size,
    check,
) -> bytes:
    check(
        create_prog(
            ctypes.byref(prog := prog_t()),
            prg.encode(),
            "<null>".encode(),
            0,
            None,
            None,
        )
    )
    status = compile_prog(
        prog, len(compile_options), to_char_p_p([o.encode() for o in compile_options])
    )

    if status != 0:
        raise RuntimeError(
            f"compile failed: {get_bytes(prog, get_log_size, get_log, check).decode()}"
        )
    return get_bytes(prog, get_code_size, get_code, check)


def encode_args_cuda_style(
    bufs, vals, device_ptr_t, marks
) -> Tuple[ctypes.Array, ctypes.Structure]:
    c_args = init_c_struct_t(
        tuple(
            [(f"f{i}", device_ptr_t) for i in range(len(bufs))]
            + [(f"f{i}", ctypes.c_int) for i in range(len(bufs), len(bufs) + len(vals))]
        )
    )(
        *bufs, *vals
    )  # noqa: E501
    return (ctypes.c_void_p * 5)(
        ctypes.c_void_p(marks[0]),
        ctypes.cast(ctypes.pointer(c_args), ctypes.c_void_p),
        ctypes.c_void_p(marks[1]),
        ctypes.cast(
            ctypes.pointer(ctypes.c_size_t(ctypes.sizeof(c_args))), ctypes.c_void_p
        ),
        ctypes.c_void_p(marks[2]),
    ), c_args  # noqa: E501


def time_execution_cuda_style(
    cb, ev_t, evcreate, evrecord, evsync, evdestroy, evtime, enable=False
) -> Optional[float]:
    if not enable:
        return cb()
    evs = [init_c_var(ev_t(), lambda x: evcreate(ctypes.byref(x), 0)) for _ in range(2)]
    evrecord(evs[0], None)
    cb()
    evrecord(evs[1], None)
    evsync(evs[1])
    evtime(ctypes.byref(ret := ctypes.c_float()), evs[0], evs[1])
    for ev in evs:
        evdestroy(ev)
    return ret.value * 1e-3
