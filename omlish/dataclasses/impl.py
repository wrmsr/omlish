"""
FIXME:
 - make_dataclass

TODO:
 - default_fn
  - toposort
 - type_check
 - coerce
 - Optional/Sequence/AbstractSet/Mapping unpacking
 - init/check/validate
 - reorder? tools hate it
  - x: int = dc.field(default=dc.REQUIRED) - kwonly but better than nothing

Backport:
 - dc:
  - match_args=True
  - kw_only=False
  - slots=False
  - weakref_slot=False
 - field:
  - kw_only=MISSING
"""
import dataclasses as dc
import io
import typing as ta

from .. import lang


class Check(lang.Marker):
    pass


def field(
        *,
        default=dc.MISSING,
        default_factory=dc.MISSING,
        init=True,
        repr=True,
        hash=None,
        compare=True,
        metadata=None,

        kw_only=False,

        check: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
):
    md = {**(metadata or {})}

    if check is not None:
        if Check in md:
            raise KeyError(md)
        if not callable(check):
            raise TypeError(check)
        md[Check] = check

    fld = dc.field(  # type: ignore
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=md,
    )
    return fld


class Params(ta.NamedTuple):
    init: bool
    repr: bool
    eq: bool
    order: bool
    unsafe_hash: bool
    frozen: bool


def fieldsmap(cls: ta.Any) -> ta.Mapping[str, dc.Field]:
    return {f.name: f for f in dc.fields(cls)}


class CheckException(Exception):
    pass


class Ns:
    def __init__(self, reserved: ta.Optional[ta.Iterable[str]]) -> None:
        super().__init__()
        self._missing = missing = object()
        self._dct: ta.Dict[str, ta.Any] = {k: missing for k in (reserved or [])}

    def new(self, v: ta.Any, pfx: str = '') -> str:
        k = self._new_name()


def process_class(cls: type, params: Params) -> type:
    dcls = dc.dataclass(  # type: ignore
        cls,
        init=params.init,
        repr=params.repr,
        eq=params.eq,
        order=params.order,
        unsafe_hash=params.unsafe_hash,
        frozen=params.frozen,
    )

    flds = fieldsmap(dcls)
    self_name = '__dataclass_self__' if 'self' in flds else 'self'

    lines = []
    ns = {
        '__dataclass_init__': dcls.__init__,
        '_CheckException': CheckException,
    }

    buf = io.StringIO()
    buf.write(f'def __init__({self_name}')
    for i, fn in enumerate(flds):
        buf.write(', ')
        buf.write(fn)
    buf.write('):')
    lines.append(buf.getvalue())
    buf.truncate(0)

    for f in flds.values():
        chk = f.metadata.get(Check)
        if chk is not None:
            cn = f'_check_' + f.name
            ns[cn] = chk
            lines.append(f'    if not {cn}({f.name}): raise _CheckException')

    lines.append(f'    return __dataclass_init__({self_name}, {", ".join(flds)})')

    exec('\n'.join(lines), ns)

    dcls.__init__ = ns['__init__']

    return dcls


def dataclass(
        cls=None,
        /,
        *,
        init=True,
        repr=True,
        eq=True,
        order=False,
        unsafe_hash=False,
        frozen=False,
):
    def wrap(cls):
        return process_class(cls, Params(
            init=init,
            repr=repr,
            eq=eq,
            order=order,
            unsafe_hash=unsafe_hash,
            frozen=frozen,
        ))

    if cls is None:
        return wrap
    return wrap(cls)
