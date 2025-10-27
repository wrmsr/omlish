import dataclasses as dc
import linecache
import textwrap
import threading
import types
import typing as ta
import uuid

from omlish import check
from omlish import lang

from .names import NamespaceBuilder
from .params import render_param_spec_call
from .params import render_param_spec_def


##


@dc.dataclass()
class _ReservedFilenameEntry:
    unique_id: str
    seq: int = 0


_RESERVED_FILENAME_UUID_TLS = threading.local()


def reserve_linecache_filename(prefix: str) -> str:
    try:
        e = _RESERVED_FILENAME_UUID_TLS.unique_id
    except AttributeError:
        e = _RESERVED_FILENAME_UUID_TLS.unique_id = _ReservedFilenameEntry(str(uuid.uuid4()))
    while True:
        unique_filename = f'<generated:{prefix}:{e.seq}>'
        cache_line = (1, None, (e.unique_id,), unique_filename)
        e.seq += 1
        if linecache.cache.setdefault(unique_filename, cache_line) == cache_line:  # type: ignore
            return unique_filename


##


def create_function(
        name: str,
        params: lang.ParamSpec,
        body: str,
        *,
        globals: ta.Mapping[str, ta.Any] | None = None,  # noqa
        locals: ta.Mapping[str, ta.Any] | None = None,  # noqa
) -> types.FunctionType:
    check.isinstance(body, str)
    locals = dict(locals or {})  # noqa

    nsb = NamespaceBuilder(reserved_names=set(locals) | set(globals or []))
    sig = render_param_spec_def(params, nsb)
    for k, v in nsb.items():
        check.not_in(k, locals)
        locals[k] = v

    body = textwrap.indent(textwrap.dedent(body.strip()), '  ')
    txt = f'def {name}{sig}:\n{body}'
    local_vars = ', '.join(locals.keys())
    exec_txt = f'def __create_fn__({local_vars}):\n{textwrap.indent(txt, "  ")}\n  return {name}'

    ns: dict = {}
    filename = reserve_linecache_filename(name)
    bytecode = compile(exec_txt, filename, 'exec')
    eval(bytecode, globals or {}, ns)  # type: ignore  # noqa

    fn = ns['__create_fn__'](**locals)
    fn.__source__ = txt
    linecache.cache[filename] = (len(exec_txt), None, exec_txt.splitlines(True), filename)
    return fn


##


def create_detour(params: lang.ParamSpec, target: ta.Callable) -> types.CodeType:
    check.callable(target)

    gfn = create_function('_', params, f'return 1{render_param_spec_call(params)}')
    check.state(gfn.__code__.co_consts == (None, 1))

    return gfn.__code__.replace(co_consts=(None, target))
