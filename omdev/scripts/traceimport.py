"""
todo:
 - create table paths(path varchar(1024); - norm, dedupe, index, etc (bonus points for 32bit key)
 - store lineno from stacktrace

http://www.logilab.org/856
http://www.python.org/dev/peps/pep-0302/

start / end / cumulative / exclusive time / vm_rss / vm_vms

jq '..?|.loaded_name?|select(.!=null)'
"""
import dataclasses as dc
import inspect
import logging
import operator
import os
import sys
import threading
import time
import types
import typing as ta

psutil: ta.Any
try:
    psutil = __import__('psutil')
except ImportError:
    psutil = None


log = logging.getLogger(__name__)


REQUIRED_PYTHON_VERSION = (3, 8)


@dc.dataclass()
class Stats:
    _ATTRS: ta.ClassVar[ta.Sequence[str]]

    time: float = 0.
    vm_rss: int = 0
    vm_vms: int = 0

    def _op(self, op, other):
        return Stats(*[op(getattr(self, a), getattr(other, a)) for a in Stats._ATTRS])

    def __add__(self, other):
        return self._op(operator.add, other)

    def __sub__(self, other):
        return self._op(operator.sub, other)


Stats._ATTRS = [f.name for f in dc.fields(Stats)]


class StatsFactory:

    def __init__(self, *, start_time: ta.Optional[float] = None) -> None:
        super().__init__()

        self._start_time = start_time if start_time is not None else time.time()

    def __call__(self) -> Stats:
        kw: dict = {}

        if psutil is not None:
            mem = psutil.Process().memory_info()
            kw.update(
                vm_rss=mem.rss,
                vm_vms=mem.vms,
            )

        return Stats(
            time=time.time() - self._start_time,
            **kw,
        )

    PROC_MEM_KEYS_BY_FIELD = {
        'vm_vms': 'VmSize',
        'vm_rss': 'VmRSS',
    }

    PROC_MEM_SCALE = {
        'kb': 1024.0,
        'mb': 1024.0 * 1024.0,
    }

    @classmethod
    def get_proc_status(cls) -> ta.Mapping[str, ta.Any]:
        with open('/proc/self/status', 'r') as status_file:
            status_block = status_file.read()

        status_fields = {
            field: value.strip()
            for line in status_block.split('\n')
            for field, _, value in [line.partition(':')]
        }

        status = {}

        for key, field in cls.PROC_MEM_KEYS_BY_FIELD.items():
            num, unit = status_fields[field].split()

            status[key] = int(float(num) * cls.PROC_MEM_SCALE[unit.lower()])

        return status


##


@dc.dataclass()
class StackTraceEntry:
    file: str
    line: int
    func: str


@dc.dataclass()
class Node:
    import_name: ta.Optional[str] = None
    import_fromlist: ta.Optional[ta.Iterable[str]] = None
    import_level: ta.Optional[int] = None

    pid: ta.Optional[int] = None
    tid: ta.Optional[int] = None

    stack_trace: ta.Optional[ta.Sequence[StackTraceEntry]] = None
    exception: ta.Optional[ta.Union[Exception, str]] = None

    children: ta.List['Node'] = dc.field(default_factory=list)

    cached_id: ta.Optional[int] = None

    loaded_name: ta.Optional[str] = None
    loaded_file: ta.Optional[str] = None
    loaded_id: ta.Optional[int] = None

    start_stats: ta.Optional[Stats] = None
    end_stats: ta.Optional[Stats] = None

    stats: ta.Optional[Stats] = None

    self_stats: ta.Optional[Stats] = None
    child_stats: ta.Optional[Stats] = None

    seq: ta.Optional[int] = None
    depth: int = 0


class ImportTracer:

    def __init__(self, *, stringify_fields: bool = False) -> None:
        super().__init__()

        self._stats_factory = StatsFactory()
        self._stringify_fields = stringify_fields

    def _stringify_value(self, o: ta.Any) -> ta.Any:
        if self._stringify_fields:
            return repr(o)
        else:
            return o

    def _fixup_node(self, node: Node, *, depth: int = 0, seq: int = 0) -> int:
        node.depth = depth
        node.seq = seq
        node.child_stats = Stats()

        for child in node.children:
            seq = self._fixup_node(child, depth=depth + 1, seq=seq + 1)
            node.child_stats += child.stats  # type: ignore

        node.self_stats = node.stats - node.child_stats  # type: ignore
        return seq

    def trace(self, root_module: str) -> Node:
        node_stack = [Node()]

        def new_import(name, globals=None, locals=None, fromlist=(), level=0):
            node = Node(
                import_name=name,
                import_fromlist=fromlist,
                import_level=level,
                pid=os.getpid(),
                tid=threading.current_thread().ident,
                stack_trace=[
                    StackTraceEntry(*s[1:4])
                    for s in inspect.stack()
                    if s[0].f_code.co_filename != __file__
                ],
                cached_id=id(sys.modules[name]) if name in sys.modules else None,
                start_stats=self._stats_factory(),
            )

            node_stack[-1].children.append(node)
            node_stack.append(node)

            try:
                loaded = old_import(name, globals, locals, fromlist, level)
                if not isinstance(loaded, types.ModuleType):
                    raise TypeError(loaded)
                node.loaded_name = loaded.__name__
                node.loaded_id = id(loaded)
                node.loaded_file = getattr(loaded, '__file__', None)
                return loaded

            except Exception as ex:
                node.exception = self._stringify_value(ex)
                raise

            finally:
                node.end_stats = self._stats_factory()
                node.stats = node.end_stats - node.start_stats
                if node_stack.pop() is not node:
                    raise RuntimeError(node_stack)

        old_import = __builtins__.__import__
        __builtins__.__import__ = new_import
        try:
            try:
                __import__(root_module, globals(), locals(), [], 0)
            except Exception:
                log.exception(f'root_module: {root_module}')
        finally:
            __builtins__.__import__ = old_import

        if len(node_stack) != 1 or len(node_stack[0].children) != 1:
            raise RuntimeError(node_stack)

        node = node_stack[0].children[0]
        self._fixup_node(node)
        return node


##


def main() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise EnvironmentError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa

    _, mod = sys.argv
    node = ImportTracer(stringify_fields=True).trace(mod)
    import json
    print(json.dumps(dc.asdict(node)))


if __name__ == '__main__':
    main()
