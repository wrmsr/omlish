import dataclasses as dc
import inspect
import typing as ta

from .. import construction as csn
from ... import code
from ... import properties
from ..internals import FieldType
from ..internals import hash_action
from ..internals import PARAMS
from ..internals import POST_INIT_NAME
from ..internals import recursive_repr
from ..internals import tuple_str
from ..pickling import SimplePickle
from ..types import _Placeholder
from ..types import ExtraFieldParams
from ..types import PostInit
from .bootstrap import Fields
from .init import Init
from .types import Aspect
from .types import attach


class Repr(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    def process(self) -> ta.Sequence[csn.Action]:
        if not self.ctx.params.repr:
            return []

        lines = []
        nsb = code.NamespaceBuilder(unavailable_names=['self'])
        lines.append('l = []')
        for f in self.ctx.spec.fields.instance:
            if not f.repr:
                continue
            efp = f.metadata.get(ExtraFieldParams)
            b = []
            if efp is not None and efp.repr_fn is not None:
                fn = nsb.put(efp.repr_fn, f'_repr_fn_{f.name}')
                b.extend([
                    f's = {fn}(self.{f.name})',
                    f'if s is not None: l.append(f"{f.name}={{s}}")',
                ])
            else:
                b.append(f'l.append(f"{f.name}={{self.{f.name}!r}}")')
            if efp is not None and efp.repr_if is not None:
                fn = nsb.put(efp.repr_if, f'_repr_if_{f.name}')
                lines.append(f'if {fn}(self.{f.name}):')
                lines.extend('  ' + l for l in b)
            else:
                lines.extend(b)
        lines.append('return self.__class__.__qualname__ + "(" + ", ".join(l) + ")"')

        fn = code.create_function(
            '__repr__',
            code.ArgSpec(['self']),
            '\n'.join(lines),
            locals=dict(nsb),
            globals=self.ctx.spec.globals,
        )

        self.ctx.set_new_attribute(fn.__name__, recursive_repr(fn))

        return []


class Eq(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    def process(self) -> ta.Sequence[csn.Action]:
        if not self.ctx.params.eq:
            return []

        flds = [f for f in self.ctx.spec.fields.instance if f.compare]
        self_tuple = tuple_str('self', flds)
        other_tuple = tuple_str('other', flds)

        return [csn.SetAttr(
            '__eq__',
            csn.Function(
                '__eq__',
                code.ArgSpec(['self', 'other']),
                '\n'.join([
                    f'if other.__class__ is self.__class__: return {self_tuple} == {other_tuple}',
                    'raise TypeError(self, other)' if self.ctx.extra_params.strict_eq else 'return NotImplemented',
                ]),
            ),
        )]


class Order(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    def check(self) -> None:
        if self.ctx.params.order and not self.ctx.params.eq:
            raise ValueError('eq must be true if order is true')

    def process(self) -> ta.Sequence[csn.Action]:
        if not self.ctx.params.order:
            return []

        ret = []
        flds = [f for f in self.ctx.spec.fields.instance if f.compare]
        self_tuple = tuple_str('self', flds)
        other_tuple = tuple_str('other', flds)
        for name, op in [
            ('__lt__', '<'),
            ('__le__', '<='),
            ('__gt__', '>'),
            ('__ge__', '>='),
        ]:
            if name in self.ctx.cls.__dict__:
                raise TypeError(
                    f'Cannot overwrite attribute {name} in class {self.ctx.cls.__name__}. '
                    f'Consider using functools.total_ordering')

            ret.append(csn.SetAttr(
                name,
                csn.Function(
                    name,
                    code.ArgSpec(['self', 'other']),
                    '\n'.join([
                        f'if other.__class__ is self.__class__: return {self_tuple} {op} {other_tuple}',
                        'return NotImplemented',
                    ]),
                ),
            ))

        return ret


class Hash(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    DEFAULT_CACHE_ATTR = '___hash'

    @properties.cached
    def cache_attr(self) -> ta.Optional[str]:
        if isinstance(self.ctx.spec.extra_params.cache_hash, str):
            return self.ctx.spec.extra_params.cache_hash
        elif self.ctx.spec.extra_params.cache_hash:
            return self.DEFAULT_CACHE_ATTR
        else:
            return None

    @property
    def slots(self) -> ta.AbstractSet[str]:
        return {self.cache_attr} if self.cache_attr is not None else set()

    def check(self) -> None:
        if self.cache_attr in self.ctx.spec.fields.by_name:
            raise AttributeError(self.cache_attr)

    def process(self) -> ta.Sequence[csn.Action]:
        # Was this class defined with an explicit __hash__?  Note that if __eq__ is defined in this class, then python
        # will automatically set __hash__ to None.  This is a heuristic, as it's possible that such a __hash__ == None
        # was not auto-generated, but it close enough.
        class_hash = self.ctx.cls.__dict__.get('__hash__', dc.MISSING)
        has_explicit_hash = not (class_hash is dc.MISSING or (class_hash is None and '__eq__' in self.ctx.cls.__dict__))
        ha = hash_action[(
            bool(self.ctx.params.unsafe_hash),
            bool(self.ctx.params.eq),
            bool(self.ctx.params.frozen),
            has_explicit_hash,
        )]
        if not ha:
            return []
        fn = ha(self.ctx.cls, self.ctx.spec.fields.instance, self.ctx.spec.globals)

        if self.ctx.spec.extra_params.cache_hash:
            attr = self.cache_attr
            self.ctx.set_new_attribute(attr, None)
            ofn = fn

            def fn(obj):
                hsh = getattr(obj, attr)
                if hsh is None:
                    hsh = ofn(obj)
                    object.__setattr__(obj, attr, hsh)
                return hsh

        self.ctx.cls.__hash__ = fn

        return []


class Doc(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Init]

    def process(self) -> ta.Sequence[csn.Action]:
        if not getattr(self.ctx.cls, '__doc__'):
            sig = inspect.signature(self.ctx.cls)
            self.ctx.cls.__doc__ = self.ctx.cls.__name__ + str(sig).replace(' -> None', '')

        return []


class PostInitAspect(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    @attach('init')
    class Init(Aspect.Function['PostInitAspect']):

        @attach(Aspect.Function.Phase.POST)
        def build_post_init_lines(self) -> ta.List[str]:
            if not self.fctx.ctx.spec.params.init:
                return []

            ret = []
            if hasattr(self.fctx.ctx.cls, POST_INIT_NAME):
                params_str = ','.join(f.name for f in self.fctx.ctx.spec.fields.by_field_type.get(FieldType.INIT, []))
                ret.append(f'{self.fctx.self_name}.{POST_INIT_NAME}({params_str})')
            return ret

        @attach(Aspect.Function.Phase.POST)
        def build_extra_post_init_lines(self) -> ta.List[str]:
            if not self.fctx.ctx.spec.params.init:
                return []

            ret = []
            for pi in self.fctx.ctx.spec.rmro_extras_by_cls[PostInit]:
                if isinstance(pi.fn, (property, properties.Property)):
                    ret.append(f'{self.fctx.nsb.put(pi.fn)}.__get__({self.fctx.self_name}, {self.fctx.self_name}.__class__)')  # noqa
                else:
                    ret.append(f'{self.fctx.nsb.put(pi.fn)}({self.fctx.self_name})')
            return ret


class Pickle(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    def process(self) -> ta.Sequence[csn.Action]:
        if self.ctx.extra_params.pickle and self.ctx.cls.__reduce__ is object.__reduce__:
            setattr(self.ctx.cls, '__reduce__', SimplePickle.__reduce__)

        return []


class Placeholders(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Init]

    def check(self) -> None:
        for a, v in self.ctx.cls.__dict__.items():
            if v is _Placeholder:
                raise TypeError(f'Processed class contains placeholder: {a}')


class Frozen(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    def check(self) -> None:
        dc_rmro = [b for b in self.ctx.spec.rmro[:-1] if dc.is_dataclass(b)]
        if dc_rmro:
            any_frozen_base = any(getattr(b, PARAMS).frozen for b in dc_rmro)
            if any_frozen_base:
                if not self.ctx.params.frozen:
                    raise TypeError('cannot inherit non-frozen dataclass from a frozen one')
            elif self.ctx.params.frozen:
                raise TypeError('cannot inherit frozen dataclass from a non-frozen one')

    def process(self) -> ta.Sequence[csn.Action]:
        if not self.ctx.params.frozen:
            return []

        locals = {}

        attr_predicate = None
        allow_setattr = self.ctx.extra_params.allow_setattr
        if isinstance(allow_setattr, str):
            allow_setattr = [allow_setattr]
        if isinstance(allow_setattr, ta.Iterable):
            allow_setattr = set(allow_setattr)
            aas = set()
            has_underscore = False
            for a in allow_setattr:
                if a == '_':
                    has_underscore = True
                elif isinstance(a, str) and a:
                    aas.add(a)
                else:
                    raise ValueError(a)
            aps = []
            if has_underscore:
                aps.append("name.startswith('_')")
            if aas:
                aps.append(f'name in allowed_attr_names')
                locals['allowed_attr_names'] = frozenset(aas)
            attr_predicate = ' or '.join(aps)
        elif isinstance(allow_setattr, bool):
            if allow_setattr:
                return []
        else:
            raise TypeError(allow_setattr)

        slots = [s for a in self.ctx.aspects for s in a.slots]
        locals.update({
            'cls': self.ctx.cls,
            'FrozenInstanceError': dc.FrozenInstanceError,
            'attr_names': frozenset(self.ctx.spec.fields.by_name) | frozenset(slots),
        })

        for fnname in ['__setattr__', '__delattr__']:
            args = ['name'] + (['value'] if fnname == '__setattr__' else [])
            pred = 'type(self) is cls or name in attr_names'
            if attr_predicate:
                pred = f'not ({attr_predicate}) and ({pred})'
            fn = code.create_function(
                fnname,
                code.ArgSpec(['self'] + args),
                '\n'.join([
                    f'if {pred}:',
                    f'    raise FrozenInstanceError(f"cannot assign to field {{name!r}}")',
                    f'object.{fnname}(self, {", ".join(args)})',
                ]),
                locals=locals,
                globals=self.ctx.spec.globals,
            )
            self.ctx.set_new_attribute(fn.__name__, fn, raise_=True)

        return []


class Iterable(Aspect):

    @property
    def deps(self) -> ta.Collection[ta.Type[Aspect]]:
        return [Fields]

    def process(self) -> ta.Sequence[csn.Action]:
        if not self.ctx.extra_params.iterable:
            return []

        atts = [f.name for f in self.ctx.spec.fields.instance]

        def __iter__(obj) -> ta.Iterator[ta.Any]:
            return iter(getattr(obj, a) for a in atts)

        self.ctx.set_new_attribute('__iter__', __iter__, raise_=True)

        return []
