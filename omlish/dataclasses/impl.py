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
import collections.abc
import dataclasses as dc
import io
import typing as ta

from .. import lang


METADATA_KEY = '__dataclass_metadata__'


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


class NsGen:
    def __init__(self, reserved: ta.Optional[ta.Iterable[str]] = None) -> None:
        super().__init__()
        self._missing = missing = object()
        self._dct: ta.Dict[str, ta.Any] = {k: missing for k in (reserved or [])}
        self._pnd: ta.Dict[str, int] = {}

    @property
    def dct(self) -> ta.Dict[str, ta.Any]:
        return self._dct

    def new(self, v: ta.Any, pfx: str = '') -> str:
        p = '__'
        if pfx:
            p += pfx + '__'
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

    def update(self, *args: ta.Union[ta.Mapping[str, ta.Any], ta.Iterable[ta.Tuple[str, ta.Any]]],
               **kwargs: ta.Any) -> None:
        for a in args:
            if isinstance(a, collections.abc.Mapping):
                for k in a:
                    self.put(k, a[k])
            else:
                for k, v in a:
                    self.put(k, v)
        for k, v in kwargs.items():
            self.put(k, v)


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
    nsg = NsGen()
    nsg.update({
        '__dataclass_init__': dcls.__init__,
        '__CheckException': CheckException,
    })

    buf = io.StringIO()
    buf.write(f'def __init__({self_name}')
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

    lines.append(f'    return __dataclass_init__({self_name}, {", ".join(flds)})')

    ns = nsg.dct

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


def check(fn: ta.Callable[..., bool]) -> None:
    lang.get_caller_cls_dct().setdefault(METADATA_KEY, {}).setdefault(Check, []).append(fn)
