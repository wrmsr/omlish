import abc
import dataclasses as dc
import functools
import types
import typing as ta
import weakref

from .. import construction as csn
from ... import check
from ... import code
from ... import collections as ocol
from ... import lang
from ... import properties
from ..confer import confer_params
from ..internals import DataclassParams
from ..reflect import DataSpec
from ..reflect import get_cls_spec
from ..types import _Placeholder
from ..types import ExtraParams
from ..types import MetaclassParams


T = ta.TypeVar('T')
U = ta.TypeVar('U')
TypeT = ta.TypeVar('TypeT', bound=type, covariant=True)
AspectT = ta.TypeVar('AspectT', bound='Aspect', covariant=True)
Aspectable = ta.Union['Aspect', ta.Type['Aspect'], ta.Callable[..., 'Aspect']]


class AspectCollection(ta.Generic[AspectT], lang.Abstract):

    def __init__(
            self,
            aspects: ta.Iterable[ta.Union[AspectT, ta.Callable[..., AspectT]]],
            aspect_cls: ta.Type[AspectT],
    ) -> None:
        super().__init__()

        self._aspect_cls = aspect_cls
        self._aspects = [a if isinstance(a, aspect_cls) else a(self) for a in aspects]
        self._aspects.sort(key=lambda a: (type(a).__qualname__, id(a)))
        for a in self._aspects:
            check.isinstance(a, aspect_cls)

    @property
    def aspects(self) -> ta.Sequence[AspectT]:
        return self._aspects

    @property
    def aspect_cls(self) -> ta.Type[AspectT]:
        return self._aspect_cls

    def get_aspects(self, cls: ta.Type[U]) -> ta.Sequence[U]:
        return [a for a in self._aspects if isinstance(a, cls)]

    def get_aspect(self, cls: ta.Type[U]) -> U:
        return check.single(self.get_aspects(cls))


class Context(AspectCollection['Aspect'], ta.Generic[TypeT]):

    def __init__(
            self,
            cls: TypeT,
            params: DataclassParams,
            extra_params: ExtraParams,
            *,
            metaclass_params: ta.Optional[MetaclassParams] = None,
            aspects: ta.Optional[ta.Iterable[ta.Union['Aspect', ta.Callable[..., 'AspectT']]]] = None,
            inspecting: bool = False,
    ) -> None:
        self._original_params = check.isinstance(params, DataclassParams)
        self._original_extra_params = check.isinstance(extra_params, ExtraParams)
        self._original_metaclass_params = check.isinstance(metaclass_params, (MetaclassParams, type(None)))
        params, extra_params, metaclass_params = confer_params(cls.__bases__, params, extra_params, metaclass_params)

        if aspects is None:
            aspects = extra_params.aspects
            if aspects is None:
                from .driver import DEFAULT_ASPECTS
                aspects = DEFAULT_ASPECTS

        super().__init__(aspects, Aspect)

        self._cls = check.isinstance(cls, type)
        self._params = params
        self._extra_params = extra_params
        self._metaclass_params = metaclass_params
        self._inspecting = inspecting

    @property
    def cls(self) -> TypeT:
        return self._cls

    @property
    def params(self) -> DataclassParams:
        return self._params

    @property
    def extra_params(self) -> ExtraParams:
        return self._extra_params

    @property
    def metaclass_params(self) -> ta.Optional[MetaclassParams]:
        return self._metaclass_params

    @property
    def inspecting(self) -> bool:
        return self._inspecting

    @property
    def original_params(self) -> DataclassParams:
        return self._original_params

    @property
    def original_extra_params(self) -> ExtraParams:
        return self._original_extra_params

    @property
    def original_metaclass_params(self) -> ta.Optional[MetaclassParams]:
        return self._original_metaclass_params

    @properties.cached
    @property
    def aspect_plan(self) -> ta.Sequence[ta.Sequence['Aspect']]:
        dct = {}
        for a in self.aspects:
            ds = set()
            for dep in a.deps:
                da = None
                for dac in self.aspects:
                    if isinstance(dac, dep):
                        if da is None:
                            da = dac
                        else:
                            raise Exception(f'Ambiguous dependency {dep} in aspect {a} resolved to {da} and {dac}')
                if da is None:
                    raise Exception(f'Unresolved dependency {dep} in aspect {a}')
                ds.add(da)
            dct[a] = ds
        lst = list(ocol.toposort(dct))
        return [sorted(al, key=lambda la: type(la).__name__) for al in lst]

    @properties.stateful_cached
    @property
    def spec(self) -> DataSpec:
        return get_cls_spec(self._cls)

    def set_new_attribute(self, name: str, value: ta.Any, *, raise_: bool = False) -> bool:
        if name in self.cls.__dict__:
            ev = self.cls.__dict__[name]
            if ev is not _Placeholder:
                if raise_:
                    raise TypeError(f'Cannot overwrite attribute {name}')
                return False
        setattr(self.cls, name, value)
        return True

    class Function(AspectCollection['Aspect.Function'], ta.Generic[TypeT]):

        def __init__(
                self,
                ctx: 'Context[TypeT]',
                aspects: ta.Iterable[ta.Union['Aspect.Function', ta.Callable[..., 'Aspect.Function']]],
                *,
                field: ta.Optional[dc.Field] = None,
        ) -> None:
            super().__init__(aspects, Aspect.Function)

            self._ctx = check.isinstance(ctx, Context)
            self._field = check.isinstance(field, (dc.Field, type(None)))

        @property
        def ctx(self) -> 'Context[TypeT]':
            return self._ctx

        @property
        def has_field(self) -> bool:
            return self._field is not None

        @property
        def field(self) -> dc.Field:
            if self._field is None:
                raise TypeError
            return self._field

        @properties.cached
        @property
        def nsb(self) -> code.NamespaceBuilder:
            return code.NamespaceBuilder(unavailable_names=self.ctx.spec.fields.by_name)

        @properties.cached
        def self_name(self) -> str:
            return self.nsb.put(None, 'self')

    def function(self, attachment_keys: ta.Iterable[ta.Any] = (), **kwargs) -> Function[TypeT]:
        check.arg(not isinstance(attachment_keys, str))
        attachment_keys = list(attachment_keys)
        if Aspect.Function not in attachment_keys:
            attachment_keys.append(Aspect.Function)
        attachments = []
        seen = set()
        for aspect in self.aspects:
            for key in attachment_keys:
                for attachment in aspect.attachment_lists_by_key.get(key, []):
                    if attachment is None or attachment in seen:
                        continue
                    attachments.append(functools.partial(attachment, aspect))
                    seen.add(attachment)
        return Context.Function(self, attachments, **kwargs)


ATTACHMENTS = weakref.WeakKeyDictionary()


def attach(key):
    # FIXME: steal a better word from aop than 'attach'
    def inner(obj):
        ATTACHMENTS.setdefault(obj, []).append(key)
        return obj
    return inner


CLS_ATTACHMENT_KEYS = weakref.WeakKeyDictionary()


def get_keys_by_attachment_name(obj: ta.Any) -> ta.Mapping[ta.Any, ta.Any]:
    if isinstance(obj, type):
        rmro = reversed(obj.__mro__[1:])
    else:
        rmro = reversed(type(obj).__mro__)
    keys_by_name = {}
    for c in rmro:
        try:
            nks = CLS_ATTACHMENT_KEYS[c]
        except KeyError:
            nks = {}
            for n, v in c.__dict__.items():
                try:
                    ks = ATTACHMENTS[v]
                except (KeyError, TypeError):
                    continue
                nks[n] = ks
            CLS_ATTACHMENT_KEYS[c] = nks
        for n, ks in nks.items():
            for k in ks:
                keys_by_name[n] = k
    for n, v in obj.__dict__.items():
        try:
            ks = ATTACHMENTS[v]
        except (KeyError, TypeError):
            continue
        for k in ks:
            keys_by_name[n] = k
    return keys_by_name


def get_attachment_lists_by_key(obj: ta.Any) -> ta.Mapping[ta.Any, ta.Sequence[ta.Any]]:
    ret = {}
    for attachment_name, key in get_keys_by_attachment_name(obj).items():
        ret.setdefault(key, []).append(getattr(obj, attachment_name))
    return ret


class AttachmentCollection(lang.Abstract):

    @properties.cached
    def attachment_lists_by_key(self) -> ta.Mapping[ta.Any, ta.Sequence[ta.Any]]:
        return get_attachment_lists_by_key(self)


class Aspect(AttachmentCollection, lang.Abstract):

    def __init__(self, ctx: Context[TypeT]) -> None:
        super().__init__()

        self._ctx = check.isinstance(ctx, Context)

    @property
    def ctx(self) -> Context:
        return self._ctx

    @abc.abstractproperty
    def deps(self) -> ta.Collection[ta.Type['Aspect']]:
        raise NotImplementedError

    @property
    def slots(self) -> ta.AbstractSet[str]:
        return frozenset()

    def check(self) -> None:
        pass

    def process(self) -> ta.Sequence[csn.Action]:
        return []

    class Function(AttachmentCollection, lang.Abstract, ta.Generic[AspectT]):

        def __init__(self, aspect: AspectT, fctx: Context.Function) -> None:
            super().__init__()

            self._aspect = check.isinstance(aspect, Aspect)
            self._fctx = check.isinstance(fctx, Context.Function)

        @property
        def aspect(self) -> AspectT:
            return self._aspect

        @property
        def fctx(self) -> Context.Function:
            return self._fctx

        @property
        def argspec(self) -> code.ArgSpec:
            raise TypeError

        class Phase(lang.AutoEnum):
            BOOTSTRAP = ...
            COERCE = ...
            DEFAULT = ...
            VALIDATE = ...
            SET_ATTRS = ...
            POST = ...
            RETURN = ...

            @classmethod
            def all(cls) -> ta.List['Aspect.Function.Phase']:
                return list(cls.__members__.values())

        def build(
                self,
                name: str,
                *,
                phases: ta.Optional[ta.Iterable[Phase]] = None,
                optional: bool = False,
                optional_phases: ta.Optional[ta.Iterable[Phase]] = (),
        ) -> ta.Optional[types.FunctionType]:
            lines = []
            if phases is None:
                phases = self.Phase.all()
            has_req_lines = False
            for phase in phases:
                for aspect in self.fctx.aspects:
                    for attachment in aspect.attachment_lists_by_key.get(phase, []):
                        alines = list(check.not_isinstance(attachment(), str))
                        if not alines:
                            continue
                        if phase not in optional_phases:
                            has_req_lines = True
                        lines.extend(alines)
            if optional and not has_req_lines:
                return None
            if not lines:
                lines = ['pass']
            return code.create_function(
                name,
                self.argspec,
                '\n'.join(lines),
                locals=dict(self.fctx.nsb),
                globals=self.fctx.ctx.spec.globals,
            )


def replace_aspects(
        aspects: ta.Iterable[Aspectable],
        replacements_by_cls: ta.Mapping[ta.Type[Aspect], Aspectable],
) -> ta.Sequence[Aspectable]:
    da = []
    for a in aspects:
        for rc, rv in replacements_by_cls.items():
            if (isinstance(a, type) and issubclass(a, rc)) or (isinstance(a, Aspect) and issubclass(type(a), rc)):
                a = rv
        da.append(a)
    return da
