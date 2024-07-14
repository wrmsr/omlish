import contextlib
import functools
import logging
import os
import sys
import time
import typing as ta
import weakref

import pkg_resources
import sqlalchemy as sa
import sqlalchemy.engine  # noqa
import sqlalchemy.event  # noqa

from ... import configs as cfg
from ... import dataclasses as dc
from ... import dynamic as dyn
from ... import lang
from .dialect import DialectInstrumentation


log = logging.getLogger(__name__)


_STATEMENT_OVERRIDE = dyn.Var(None)


Tags = ta.Mapping[str, str]
TagsCallback = ta.Callable[[ta.Any, ta.Optional[sa.engine.Connection]], Tags]
TagsOrCallback = ta.Union[Tags, TagsCallback]


TAGS: ta.List[TagsOrCallback] = []
_DYN_TAGS: dyn.Var[TagsOrCallback] = dyn.Var()


@dyn.contextmanager
def tags_context(tags: TagsOrCallback):
    with _DYN_TAGS(tags):  # type: ignore
        yield


def tags_callback(fn):
    TAGS.append(fn)
    return fn


@tags_callback
def tag_pid(*_):
    return {'pid': str(os.getpid())}


SPECIAL_IGNORED_SOURCE_FILES: ta.Set[str] = {
    '<string>',
}

IGNORED_SOURCE_IMPORTS: ta.Set[str] = {
    'contextlib',
}

_PACKAGE = __package__.partition('.')[0]

IGNORED_SOURCE_ROOTS: ta.Set[ta.Tuple[str, str]] = {
    ('sqlalchemy', '.'),
}


@lang.cached_nullary
def ignored_source_files() -> ta.AbstractSet[str]:
    ignored = set(SPECIAL_IGNORED_SOURCE_FILES)

    for imp in IGNORED_SOURCE_IMPORTS:
        try:
            mod = __import__(imp)
        except ImportError:
            pass
        else:
            ignored.add(os.path.abspath(mod.__file__))

    for pkg, root in IGNORED_SOURCE_ROOTS:
        root_path = pkg_resources.resource_filename(pkg, root)
        for dirpath, dirnames, filenames in os.walk(root_path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                if os.path.isfile(full_path) and filename.endswith('.py'):
                    ignored.add(os.path.abspath(os.path.realpath(full_path)))

    return ignored


def get_caller() -> ta.Optional[str]:
    ignored = ignored_source_files()
    frame = sys._getframe(1)  # noqa
    while frame:
        filename = frame.f_code.co_filename
        if filename not in ignored:
            return f'{filename}:{frame.f_lineno}:{frame.f_code.co_name}'
        frame = frame.f_back
    return None


@tags_callback
def tag_caller(*_):
    caller = get_caller()
    return {'caller': caller} if caller is not None else {}


@dyn.contextmanager
def statement_override_context(statement: str) -> ta.Iterator[None]:
    with _STATEMENT_OVERRIDE(statement):  # type: ignore
        yield


def get_statement_override() -> ta.Optional[str]:
    return _STATEMENT_OVERRIDE()


class StandardInstrumentation(DialectInstrumentation, cfg.Configurable):

    class Config(cfg.Config):
        tag_queries: bool = True
        query_duration_warn_threshold_s: ta.Optional[float] = 2.
        txn_duration_warn_threshold_s: ta.Optional[float] = 5.

    def __init__(self, *, config: Config = Config()) -> None:
        super().__init__(config)

        self._txn_states: ta.MutableMapping[sa.engine.Connection, StandardInstrumentation.TxnState] = weakref.WeakKeyDictionary()  # noqa
        self._tags: ta.List[TagsCallback] = [
            self._tag_conn,
            self._tag_txn,
        ]

    @property
    def tags(self) -> ta.List[TagsCallback]:
        return self._tags

    class TxnState(dc.Data):
        start_time: ta.Optional[float] = None
        caller: ta.Optional[str] = None
        query_seq: int = 0

    def _on_txn_begin(self, conn: sa.engine.Connection) -> None:
        state = self._txn_states[conn] = self.TxnState()
        state.start_time = time.time()
        state.caller = get_caller()

    def _on_txn_end(self, conn: sa.engine.Connection, *, reason: str = None) -> None:
        state = self._txn_states.pop(conn, None)
        if state is not None:
            elapsed_s = time.time() - state.start_time
            if self._config.txn_duration_warn_threshold_s is not None and \
                    elapsed_s >= self._config.txn_duration_warn_threshold_s:
                tags = ' '.join(f'{k}={v}' for k, v in self.build_tags(None, conn).items())
                log.warning(f'Transaction duration exceeded threshold: reason={reason} elapsed_s={elapsed_s} '
                            f'conn={conn!r} caller={state.caller} {tags}')

    def engine_created(self, engine: sa.engine.Engine) -> None:
        sa.event.listen(engine, 'begin', self._on_txn_begin)
        for end_reason in ['commit', 'rollback']:
            sa.event.listen(engine, end_reason, functools.partial(self._on_txn_end, reason=end_reason))

    def _tag_conn(self, cursor, conn):
        if conn is None:
            return {}
        return {'conn': hex(id(conn))[2:]}

    def _tag_txn(self, cursor, conn):
        if conn is None:
            return {}
        state = self._txn_states.get(conn)
        if state is None:
            return None
        return {
            'txn_duration': f'{time.time() - state.start_time:.2f}',
            'txn_seq': str(state.query_seq),
        }

    def build_tags(self, *args, **kwargs) -> ta.Mapping[str, str]:
        def update(dct, tcbs, strict):
            for tcb in tcbs:
                if callable(tcb):
                    d = tcb(*args, **kwargs) or {}
                else:
                    d = tcb
                for k, v in d.items():
                    if k in dct:
                        if strict:
                            raise KeyError(k)
                    else:
                        dct[k] = v

        dct: ta.Dict[str, str] = {}
        update(dct, TAGS, True)
        update(dct, self._tags, True)
        dyndct: ta.Dict[str, str] = {}
        update(dyndct, reversed(list(_DYN_TAGS)), False)
        update(dct, [dyndct], True)
        return dct

    @contextlib.contextmanager
    def instrument_statement(self, mode, cursor, statement, parameters, context=None) -> ta.Iterator[str]:
        if context is not None:
            conn = context.root_connection
            state = self._txn_states.get(conn)
            if state is not None:
                state.query_seq += 1
        else:
            conn = None

        if self._config.tag_queries:
            tags = self.build_tags(cursor, conn)
            if tags:
                statement += '  --  ' + ' '.join(f'{k}={v}' for k, v in tags.items())

        start_time = time.time()
        yield statement
        elapsed_s = time.time() - start_time

        if (
                self._config.query_duration_warn_threshold_s is not None and
                elapsed_s >= self._config.query_duration_warn_threshold_s
        ):
            log.warning(f'Query duration exceeded threshold: statement={repr(statement).replace(chr(10), " ")} '
                        f'parameters={parameters!r} elapsed_s={elapsed_s} conn={conn!r} cursor={cursor!r}')
