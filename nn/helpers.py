from __future__ import annotations

import cProfile
import contextlib
import functools
import hashlib
import multiprocessing
import operator
import os
import pathlib
import pickle
import platform
import pstats
import re
import sqlite3
import subprocess
import tempfile
import time
import typing as ta
import urllib.request

from omlish import check
from omlish import typing as ota
import tqdm

if ta.TYPE_CHECKING:  # TODO: remove this and import TypeGuard from typing once minimum python supported version is 3.10
    from typing_extensions import TypeGuard

    from .tensor import Tensor


T = ta.TypeVar("T")
U = ta.TypeVar("U")


# NOTE: it returns int 1 if x is empty regardless of the type of x
def prod(x: ta.Iterable[T]) -> ta.Union[T, int]:
    return functools.reduce(operator.__mul__, x, 1)


# NOTE: helpers is not allowed to import from anything else in tinygrad
OSX = platform.system() == "Darwin"


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


def colored(st: str, color: ta.Optional[str], background=False) -> str:
    return (
        f"\u001b[{10*background+60*(color.upper() == color)+30+['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'].index(color.lower())}m{st}\u001b[0m"  # noqa
        if color is not None
        else st
    )  # replace the termcolor library with one line


def ansistrip(s: str) -> str:
    return re.sub('\x1b\\[(K|.*?m)', '', s)


def ansilen(s: str) -> int:
    return len(ansistrip(s))


def make_pair(x: ta.Union[int, tuple[int, ...]], cnt=2) -> tuple[int, ...]:
    return (x,) * cnt if isinstance(x, int) else x


def flatten(l: ta.Iterable):
    return [item for sublist in l for item in sublist]


def fromimport(mod, frm):
    return getattr(__import__(mod, fromlist=[frm]), frm)


def strip_parens(fst: str) -> str:
    return (
        fst[1:-1]
        if fst[0] == "("
        and fst[-1] == ")"
        and fst[1:-1].find("(") <= fst[1:-1].find(")")
        else fst
    )


def round_up(num, amt: int):
    return (num + amt - 1) // amt * amt


def merge_dicts(ds: ta.Iterable[dict[T, U]]) -> dict[T, U]:
    assert len(kvs := set([(k, v) for d in ds for k, v in d.items()])) == len(
        set(kv[0] for kv in kvs)
    ), f"cannot merge, {kvs} contains different values for the same key"
    return {k: v for d in ds for k, v in d.items()}


def unwrap(x: ta.Optional[T]) -> T:
    assert x is not None
    return x


def get_child(obj, key):
    for k in key.split('.'):
        if k.isnumeric():
            obj = obj[int(k)]
        elif isinstance(obj, dict):
            obj = obj[k]
        else:
            obj = getattr(obj, k)
    return obj


@functools.lru_cache(maxsize=None)
def getenv(key: str, default=0):
    return type(default)(os.getenv(key, default))


class Context(contextlib.ContextDecorator):
    stack: ta.ClassVar[list[dict[str, int]]] = [{}]

    def __init__(self, **kwargs) -> None:
        super().__init__()
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
            ContextVar._cache[k].value = Context.stack[-1].get(k, ContextVar._cache[k].value)


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


DEBUG = ContextVar("DEBUG", 0)
IMAGE = ContextVar("IMAGE", 0)
BEAM = ContextVar("BEAM", 0)
NOOPT = ContextVar("NOOPT", 0)

GRAPH = getenv("GRAPH", 0)


class Timing(contextlib.ContextDecorator):
    def __init__(self, prefix="", on_exit=None, enabled=True) -> None:
        super().__init__()
        self.prefix = prefix
        self.on_exit = on_exit
        self.enabled = enabled

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
    def __init__(self, enabled=True, sort='cumtime', frac=0.2) -> None:
        super().__init__()
        self.enabled = enabled
        self.sort = sort
        self.frac = frac

    def __enter__(self):
        self.pr = cProfile.Profile(timer=lambda: int(time.time() * 1e9), timeunit=1e-6)
        if self.enabled:
            self.pr.enable()

    def __exit__(self, *exc):
        if self.enabled:
            self.pr.disable()
            pstats.Stats(self.pr).strip_dirs().sort_stats(self.sort).print_stats(self.frac)


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


def fetch(
        url: str,
        name: ta.Optional[str] = None,
        allow_caching=not getenv("DISABLE_HTTP_CACHE"),
) -> pathlib.Path:
    fp = pathlib.Path(DiskCache.DEFAULT_DIR) / "tinygrad" / "downloads" / (name if name else hashlib.md5(url.encode('utf-8')).hexdigest())
    if not fp.is_file() or not allow_caching:
        with urllib.request.urlopen(url, timeout=10) as r:
            assert r.status == 200
            total_length = int(r.headers.get('content-length', 0))
            progress_bar = tqdm.tqdm(total=total_length, unit='B', unit_scale=True, desc=url)
            (path := fp.parent).mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path, delete=False) as f:
                while chunk := r.read(16384):
                    progress_bar.update(f.write(chunk))
                f.close()
                if (file_size := os.stat(f.name).st_size) < total_length:
                    raise RuntimeError(f"fetch size incomplete, {file_size} < {total_length}")
                pathlib.Path(f.name).rename(fp)
    return fp


# *** universal database cache ***


CACHELEVEL = getenv("CACHELEVEL", 2)


class DiskCache:

    DEFAULT_DIR: str = getenv("XDG_CACHE_HOME", os.path.expanduser("~/Library/Caches" if OSX else "~/.cache"))
    DEFAULT_PATH: str = getenv("CACHEDB", os.path.abspath(os.path.join(DEFAULT_DIR, "tinygrad", "cache.db")))

    VERSION = 10

    def __init__(
            self,
            path: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        if path is None:
            path = self.DEFAULT_PATH

        self._path = check.non_empty_str(path)

        self._conn: ta.Optional[ota.DBAPIConnection] = None
        self._tables: ta.Set[str] = set()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def conn(self):
        if self._conn is not None:
            return self._conn

        os.makedirs(self._path.rsplit(os.sep, 1)[0], exist_ok=True)

        self._conn = sqlite3.connect(self._path)
        if DEBUG >= 7:
            self._conn.set_trace_callback(print)

        if self.get("meta", "version") != self.VERSION:
            print("cache is out of date, clearing it")
            self._conn.close()
            os.unlink(self._path)

            self._conn = sqlite3.connect(self._path)
            if DEBUG >= 7:
                self._conn.set_trace_callback(print)

            self.put("meta", "version", self.VERSION)

        return self._conn

    def get(self, table: str, key: ta.Union[dict, str, int]) -> ta.Any:
        if CACHELEVEL == 0:
            return None

        if isinstance(key, (str, int)):
            key = {"key": key}

        conn = self.conn()
        cur = conn.cursor()
        try:
            res = cur.execute(
                f"SELECT val FROM {table} WHERE {' AND '.join([f'{x}=?' for x in key.keys()])}",
                tuple(key.values()),
            )
        except sqlite3.OperationalError:
            return None  # table doesn't exist

        if (val := res.fetchone()) is not None:
            return pickle.loads(val[0])

        return None

    _TYPES: ta.Final[ta.Mapping[type, str]] = {
        str: "text",
        bool: "integer",
        int: "integer",
        float: "numeric",
        bytes: "blob",
    }

    def put(self, table: str, key: ta.Union[dict, str, int], val: T) -> T:
        if CACHELEVEL == 0:
            return val

        if isinstance(key, (str, int)):
            key = {"key": key}

        conn = self.conn()
        cur = conn.cursor()

        if table not in self._tables:
            ltypes = ', '.join(f"{k} {self._TYPES[type(key[k])]}" for k in key.keys())
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {table} ("
                f"    {ltypes}, "
                f"    val blob, "
                f"    PRIMARY KEY ({', '.join(key.keys())})"
                f")"
            )
            self._tables.add(table)

        cur.execute(
            f"REPLACE INTO {table} "
            f"({', '.join(key.keys())}, val) "
            f"VALUES ({', '.join(['?'] * len(key.keys()))}, ?)",
            tuple(key.values()) + (pickle.dumps(val),),
        )

        conn.commit()
        cur.close()
        return val


_DISK_CACHE = DiskCache()

diskcache_get = _DISK_CACHE.get
diskcache_put = _DISK_CACHE.put


def diskcache(func):
    def wrapper(*args, **kwargs) -> bytes:
        table, key = f"cache_{func.__name__}", hashlib.sha256(pickle.dumps((args, kwargs))).hexdigest()
        if (ret := diskcache_get(table, key)):
            return ret
        return diskcache_put(table, key, func(*args, **kwargs))

    setattr(wrapper, "__wrapped__", func)
    return wrapper


##


def _early_exec_process(qin, qout):
    while True:
        path, inp = qin.get()
        try:
            qout.put(subprocess.check_output(path, input=inp))
        except Exception as e:
            qout.put(e)


def enable_early_exec():
    qin: multiprocessing.Queue = multiprocessing.Queue()
    qout: multiprocessing.Queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=_early_exec_process, args=(qin, qout))
    p.daemon = True
    p.start()

    def early_exec(x):
        qin.put(x)
        ret = qout.get()
        if isinstance(ret, Exception):
            raise ret
        else:
            return ret

    return early_exec
