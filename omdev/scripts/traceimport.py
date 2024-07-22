#!/usr/bin/env python3
"""
TODO:
 - no psutil on lin / togglable on mac
 - create table paths(path varchar(1024); - norm, dedupe, index, etc (bonus points for 32bit key)
 - store lineno from stacktrace
 - gviz

http://www.logilab.org/856
http://www.python.org/dev/peps/pep-0302/

start / end / cumulative / exclusive time / vm_rss / vm_vms

jq '..?|.loaded_name?|select(.!=null)'
"""
import dataclasses as dc
import functools
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
    ATTRS: ta.ClassVar[ta.Sequence[str]]

    time: float = 0.
    vm_rss: int = 0
    vm_vms: int = 0

    def _op(self, op, other):
        return Stats(*[op(getattr(self, a), getattr(other, a)) for a in Stats.ATTRS])

    def __add__(self, other):
        return self._op(operator.add, other)

    def __sub__(self, other):
        return self._op(operator.sub, other)


Stats.ATTRS = [f.name for f in dc.fields(Stats)]


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
    seq: ta.Optional[int] = None
    depth: int = 0

    children: ta.List['Node'] = dc.field(default_factory=list)

    import_name: ta.Optional[str] = None
    import_fromlist: ta.Optional[ta.Iterable[str]] = None
    import_level: ta.Optional[int] = None

    pid: ta.Optional[int] = None
    tid: ta.Optional[int] = None

    stack_trace: ta.Optional[ta.Sequence[StackTraceEntry]] = None
    exception: ta.Optional[ta.Union[Exception, str]] = None

    cached_id: ta.Optional[int] = None

    loaded_name: ta.Optional[str] = None
    loaded_file: ta.Optional[str] = None
    loaded_id: ta.Optional[int] = None

    start_stats: ta.Optional[Stats] = None
    end_stats: ta.Optional[Stats] = None

    stats: ta.Optional[Stats] = None

    self_stats: ta.Optional[Stats] = None
    child_stats: ta.Optional[Stats] = None


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


_sqlite3: ta.Any = None


def sqlite3() -> ta.Any:
    global _sqlite3
    if _sqlite3 is None:
        _sqlite3 = __import__('sqlite3')
    return _sqlite3


def sqlite_retrying(max_retries: int = 10):
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            n = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except sqlite3().OperationalError:
                    if n >= max_retries:
                        raise
                    n += 1
                    log.exception('Sqlite error')
        return inner
    return outer


class SqliteWriter:

    def __init__(self, db_path: str) -> None:
        super().__init__()

        self._db_path = db_path

        self._table = self._DEFAULT_TABLE
        self._columns = self._build_columns(self._DEFAULT_COLUMNS)
        self._indexes = self._DEFAULT_INDEXES

    _conn: ta.Any

    _DEFAULT_TABLE = 'nodes'

    _DEFAULT_COLUMNS = [
        ('root_id', 'int'),
        ('parent_id', 'int'),

        ('has_exception', 'int not null'),
    ]

    _DEFAULT_INDEXES = [
        'root_id',
        'parent_id',

        'has_exception',

        'import_name',

        'loaded_name',
        'loaded_file',
    ]

    def _build_columns(self, base: ta.Iterable[ta.Tuple[str, str]]) -> ta.Sequence[ta.Tuple[str, str]]:
        cols = list(base)
        for f in dc.fields(Node):
            if f.type in (str, ta.Optional[str]):
                cols.append((f.name, 'text'))
            elif f.type in (int, ta.Optional[int]):
                cols.append((f.name, 'int'))
            elif f.name == 'children':
                continue
            elif f.type in (Stats, ta.Optional[Stats]):
                pfx = f.name[:-5] if f.name != 'stats' else ''
                cols.extend([
                    (pfx + 'time', 'real'),
                    (pfx + 'vm_rss', 'int'),
                    (pfx + 'vm_vms', 'int'),
                ])
            else:
                cols.append((f.name, 'text'))  # json
        return cols

    @sqlite_retrying()
    def _init_db(self, cursor):
        cols = ', '.join(f'{n} {t}' for n, t in self._columns)
        stmt = f'create table if not exists {self._table} ({cols});'
        cursor.execute(stmt)

        for c in self._indexes:
            cursor.execute(f'create index if not exists {self._table}_by_{c} on {self._table} ({c});')

#     def _insert_node(self, cursor, node, root_id=None, parent_id=None):
#         stmt = 'insert into nodes (%s) values (%s);' % (
#             ', '.join(col for col, spec in self.COLUMNS),
#             ','.join('?' for _ in self.COLUMNS))
#
#         vals = (
#             root_id,
#             parent_id,
#             node['depth'],
#             node['seq'],
#             node['module'],
#             node['start_time'],
#             node['end_time'],
#             node['cumulative_time'],
#             node['exclusive_time'],
#             node['start_vm_size'],
#             node['end_vm_size'],
#             node['cumulative_vm_size'],
#             node['exclusive_vm_size'],
#             node['start_vm_rss'],
#             node['end_vm_rss'],
#             node['cumulative_vm_rss'],
#             node['exclusive_vm_rss'],
#             node.get('cached_id'),
#             node.get('loaded_id'),
#             node.get('loaded_file'),
#             1 if 'exception' in node else 0,
#             node.get('exception'))
#
#         cursor.execute(stmt, vals)
#         row_id = cursor.lastrowid
#
#         if root_id is None:
#             root_id = row_id
#             cursor.execute('update nodes set root_id = ? where rowid = ?;', (root_id, root_id))
#
#         return 1 + sum(
#             self._insert_node(cursor, child, root_id, row_id)
#             for child in node.get('children', []))
#
#     @sqlite_retrying()
#     def _write_node(self, node: Node) -> None:
#         assert node['seq'] == 0
#
#         log.info('%s: beginning write' % (node['module']))
#
#         cursor = self._conn.cursor()
#         try:
#             node_count = self._insert_node(cursor, node)
#
#             cursor.execute('select count(*) from nodes;')
#             total_node_count, = cursor.fetchone()
#
#             cursor.execute('select count(*) from nodes where parent_id is null;')
#             total_root_count, = cursor.fetchone()
#
#             self._conn.commit()
#
#             log.info(
#                 '%s: %d import trace nodes (db: %d roots, %d total)' % (
#                     node['module'], node_count, total_root_count, total_node_count))
#
#         finally:
#             cursor.close()

    @sqlite_retrying()
    def __enter__(self: 'SqliteWriter') -> 'SqliteWriter':
        log.info('initializing database %s' % (self._db_path))

        try:
            self._conn = sqlite3().connect(self._db_path, isolation_level='immediate', timeout=20)

            cursor = self._conn.cursor()
            try:
                self._init_db(cursor)
                self._conn.commit()
            finally:
                cursor.close()

            return self

        except Exception:
            del self._conn
            raise

    def __exit__(self, *exc_info) -> None:
        self._conn = None

        log.info('done with database %s' % (self._db_path))

    def write(self, node: Node) -> None:
        return self._write_node(node)


##


def _main() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise EnvironmentError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--sqlite')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('mod')
    args = parser.parse_args()

    node = ImportTracer(stringify_fields=True).trace(args.mod)

    if args.sqlite:
        with SqliteWriter(args.sqlite) as sw:
            sw.write(node)

    else:
        import json

        kw = {}
        if args.pretty:
            kw.update(indent=2, separators=(', ', ': '))
        else:
            kw.update(indent=None, separators=(',', ':'))

        print(json.dumps(dc.asdict(node), **kw))


if __name__ == '__main__':
    _main()
