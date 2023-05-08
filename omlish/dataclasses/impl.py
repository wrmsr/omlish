"""
FIXME:
 - make_dataclass

TODO:
 - !! @dc.opaque_dataclass - mypy bypass, allow everything,
  - !!! NOPE: either won't understand __init__ args OR won't understand field accesses - need mcls :/
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
import inspect
import io
import typing as ta
import sys

from .. import collections as col
from .md import Check
from .md import Init
from .md import KwOnly
from .md import METADATA_KEY
from .md import Metadata
from .md import metadata


if sys.version_info[0] != 3:
    raise RuntimeError
IS_10 = sys.version_info[1] >= 10

VERBOSE = False


def field(
        *,
        default=dc.MISSING,
        default_factory=dc.MISSING,
        init=True,
        repr=True,
        hash=None,
        compare=True,
        metadata=None,

        kw_only=dc.MISSING,

        check: ta.Optional[ta.Callable[[ta.Any], bool]] = None,
):
    md = {**(metadata or {})}

    if check is not None:
        if Check in md:
            raise KeyError(md)
        if not callable(check):
            raise TypeError(check)
        md[Check] = check

    kwargs = {}

    if kw_only is not dc.MISSING:
        md[KwOnly] = kw_only
        if IS_10:
            kwargs['kw_only'] = kw_only

    fld = dc.field(  # type: ignore
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=md,

        **kwargs,
    )
    return fld


class Params(ta.NamedTuple):
    init: bool
    repr: bool
    eq: bool
    order: bool
    unsafe_hash: bool
    frozen: bool

    metadata: ta.Optional[Metadata]
    kw_only: bool


def fieldsmap(cls: ta.Any) -> ta.Mapping[str, dc.Field]:
    return {f.name: f for f in dc.fields(cls)}


class CheckException(Exception):
    pass


class NsGen:
    def __init__(self, reserved: ta.Optional[ta.Iterable[str]] = None, *, sep: str = '__') -> None:
        super().__init__()
        self._missing = missing = object()
        self._dct: ta.Dict[str, ta.Any] = {k: missing for k in (reserved or [])}
        self._sep = sep
        self._pnd: ta.Dict[str, int] = {}

    @property
    def dct(self) -> ta.Dict[str, ta.Any]:
        return self._dct

    @property
    def sep(self) -> str:
        return self._sep

    def new(self, v: ta.Any, pfx: str = '') -> str:
        p = self._sep
        if pfx:
            p += pfx + self._sep
        i = self._pnd.get(p, 0)
        while True:
            k = p + str(i)
            i += 1
            if k not in self._dct:
                break
        self._pnd[p] = i
        self._dct[k] = v
        return k

    def put(self, k: str, v: ta.Any) -> str:
        if k in self._dct:
            raise KeyError(k)
        self._dct[k] = v
        return k

    def update(
            self,
            *args: ta.Union[ta.Mapping[str, ta.Any], ta.Iterable[ta.Tuple[str, ta.Any]]],
            **kwargs: ta.Any,
    ) -> None:
        for k, v in col.yield_dict_init(*args, **kwargs):
            self.put(k, v)


def process_class(cls: type, params: Params) -> type:
    dckw = {}
    if IS_10:
        if params.kw_only:
            dckw['kw_only'] = params.kw_only

    dcls = dc.dataclass(  # type: ignore
        cls,
        init=params.init,
        repr=params.repr,
        eq=params.eq,
        order=params.order,
        unsafe_hash=params.unsafe_hash,
        frozen=params.frozen,

        **dckw,
    )

    if params.metadata:
        imd = getattr(dcls, METADATA_KEY, {})
        setattr(dcls, METADATA_KEY, {**imd, **params.metadata})

    flds = fieldsmap(dcls)
    self_name = '__dataclass_self__' if 'self' in flds else 'self'

    lines = []
    nsg = NsGen()
    nsg.update({
        '__dataclass_init__': dcls.__init__,
        '__CheckException': CheckException,
    })

    buf = io.StringIO()
    buf.write(f'def __init__({self_name}')
    if params.kw_only:
        buf.write(', *')
    for i, f in enumerate(flds.values()):
        buf.write(f', {f.name}')
        if f.type is not None:
            buf.write(': ')
            buf.write(nsg.put(f'__type__{f.name}', f.type))
        if f.default is not dc.MISSING:
            buf.write(' = ')
            buf.write(nsg.put(f'__default__{f.name}', f.default))
        if f.default_factory is not dc.MISSING:
            buf.write(' = ')
            buf.write(nsg.put(f'__default_factory__{f.name}', f.default_factory))
    buf.write(') -> None:')
    lines.append(buf.getvalue())
    buf.truncate(0)

    for f in flds.values():
        chk = f.metadata.get(Check)
        if chk is not None:
            cn = nsg.put(f'__check_' + f.name, chk)
            lines.append(f'    if not {cn}({f.name}): raise __CheckException')

    md = metadata(dcls)

    for i, fn in enumerate(md.get(Check, [])):
        if isinstance(fn, staticmethod):
            fn = fn.__func__
        cn = nsg.put(f'__check_{i}', fn)
        csig = inspect.signature(fn)
        cas = ', '.join(p.name for p in csig.parameters.values())
        lines.append(f'    if not {cn}({cas}): raise __CheckException')

    lines.append(f'    __dataclass_init__({self_name}, {", ".join(f"{f}={f}" for f in flds)})')

    for i, fn in enumerate(md.get(Init, [])):
        lines.append(f'    {nsg.put(f"__init_{i}", fn)}({self_name})')

    ns = nsg.dct

    src = '\n'.join(lines)
    if VERBOSE:
        print(src)
    exec(src, ns)

    dcls.__init__ = ns['__init__']

    return dcls


class Opaque:
    def __init__(self, *args, **kwargs):
        raise TypeError


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

        metadata=None,
        kw_only=False,
):
    def wrap(cls):
        return process_class(cls, Params(
            init=init,
            repr=repr,
            eq=eq,
            order=order,
            unsafe_hash=unsafe_hash,
            frozen=frozen,

            metadata=metadata,
            kw_only=kw_only,
        ))

    if cls is None:
        return wrap
    return wrap(cls)
