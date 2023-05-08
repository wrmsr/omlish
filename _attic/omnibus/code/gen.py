"""
TODO:
 - posonly
"""
import contextlib
import dataclasses as dc
import io
import linecache
import textwrap
import threading
import types
import typing as ta

from .. import check
from .. import uuid
from .argspecs import ArgSpec
from .argspecs import render_arg_spec_def
from .names import NamespaceBuilder


class IndentWriter:

    DEFAULT_INDENT = ' ' * 4

    def __init__(
            self,
            *,
            buf: io.StringIO = None,
            indent: str = None,
    ) -> None:
        super().__init__()

        self._buf = buf if buf is not None else io.StringIO()
        self._indent = check.isinstance(indent, str) if indent is not None else self.DEFAULT_INDENT
        self._level = 0
        self._has_indented = False

    @contextlib.contextmanager
    def indent(self, num: int = 1) -> ta.Iterator[None]:
        self._level += num
        try:
            yield
        finally:
            self._level -= num

    def write(self, s: str) -> None:
        indent = self._indent * self._level
        s = textwrap.dedent(s)
        i = 0
        while i < len(s):
            if not self._has_indented:
                self._buf.write(indent)
                self._has_indented = True
            try:
                n = s.index('\n', i)
            except ValueError:
                self._buf.write(s[i:])
                break
            self._buf.write(s[i:n + 1])
            self._has_indented = False
            i = n + 2

    def getvalue(self) -> str:
        return self._buf.getvalue()


class CodeGen:

    def __init__(
            self,
            *,
            writer: IndentWriter = None,
            namer: NamespaceBuilder = None,
            names: ta.Iterable[str] = None,
    ) -> None:
        super().__init__()

        self._writer = writer if writer is not None else IndentWriter()
        if namer is not None:
            check.none(names)
            self._namer = namer
        else:
            self._namer = NamespaceBuilder(unavailable_names=names)

    @property
    def writer(self) -> IndentWriter:
        return self._writer

    @property
    def namer(self) -> NamespaceBuilder:
        return self._namer

    @contextlib.contextmanager
    def indent(self, num: int = 1) -> ta.Iterator[None]:
        with self._writer.indent(num):
            yield

    def write(self, s: str) -> None:
        self._writer.write(s)

    def put(
            self,
            value: ta.Any,
            name: str = None,
            *,
            exact: bool = False,
            dedupe: bool = False,
    ) -> str:
        return self._namer.put(
            value,
            name,
            exact=exact,
            dedupe=dedupe,
        )


@dc.dataclass()
class _ReservedFilenameEntry:
    unique_id: str
    seq: int = 0


_RESERVED_FILENAME_UUID_THREADLOCAL = threading.local()


def reserve_filename(prefix: str) -> str:
    try:
        e = _RESERVED_FILENAME_UUID_THREADLOCAL.unique_id
    except AttributeError:
        e = _RESERVED_FILENAME_UUID_THREADLOCAL.unique_id = _ReservedFilenameEntry(str(uuid.uuid4()))
    while True:
        unique_filename = f'<generated:{prefix}:{e.seq}>'
        cache_line = (1, None, (e.unique_id,), unique_filename)
        e.seq += 1
        if linecache.cache.setdefault(unique_filename, cache_line) == cache_line:
            return unique_filename


def create_function(
        name: str,
        arg_spec: ArgSpec,
        body: str,
        *,
        globals: ta.Mapping[str, ta.Any] = None,
        locals: ta.Mapping[str, ta.Any] = None,
) -> types.FunctionType:
    check.isinstance(body, str)
    locals = dict(locals or {})

    nsb = NamespaceBuilder(unavailable_names=set(locals) | set(globals or []))
    sig = render_arg_spec_def(arg_spec, nsb)
    for k, v in nsb.items():
        check.not_in(k, locals)
        locals[k] = v

    body = textwrap.indent(textwrap.dedent(body.strip()), '  ')
    txt = f'def {name}{sig}:\n{body}'
    local_vars = ', '.join(locals.keys())
    exectxt = f'def __create_fn__({local_vars}):\n{textwrap.indent(txt, "  ")}\n  return {name}'

    ns = {}
    filename = reserve_filename(name)
    bytecode = compile(exectxt, filename, 'exec')
    eval(bytecode, globals, ns)

    fn = ns['__create_fn__'](**locals)
    fn.__source__ = txt
    linecache.cache[filename] = (len(exectxt), None, exectxt.splitlines(True), filename)
    return fn


class FunctionGen(CodeGen):

    def __init__(
            self,
            name: str,
            argspec: ArgSpec,
            *,
            names: ta.Iterable[str] = None,
            **kwargs
    ):
        check.isinstance(name, str)
        check.not_empty(name)
        check.isinstance(argspec, ArgSpec)

        names = set(names if names else ())
        names.add(name)
        names.update(argspec.names)

        super().__init__(names=names, **kwargs)

        self._name = name
        self._argspec = argspec

    @property
    def name(self) -> str:
        return self._name

    @property
    def argspec(self) -> ArgSpec:
        return self._argspec

    def create(
            self,
            *,
            globals: ta.Mapping[str, ta.Any] = None,
            locals: ta.Mapping[str, ta.Any] = None,
    ) -> types.FunctionType:
        return create_function(
            self.name,
            self.argspec,
            self.writer.getvalue(),
            globals=globals,
            locals={**self._namer, **(locals or {})},
        )
