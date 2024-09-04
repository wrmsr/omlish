"""
TODO:
- MRO namespace walking? codec/encoder is a bad fit. optional?
- revisit contravariant injected settings here
- 'loader' contravariant that news from a file or some shit
 - with watching and ReloadRequest emission

FIXME:
- support newable.ref((A, B))
- this fucking shit should raise
  on_initialize:
    lifecycle_callback_request_filter:
      on_initialize: noisy_log_silencer

$:
  document$doc:
  sqlalchemy_model$review: Review
  sqlalchemy_model$business: Business
  sqlalchemy_model$user: User
elements:
- entities: [$doc, $review, $business, $user]
- bindings:
  - [$doc.id, $doc.f.review_id, $review.a.id]
  - [$doc.f.review_comment, $review.a.comment]
  - [$doc.f.business_id, $review.a.business_id, $business.a.id]
  - [$doc.f.business_name, $business.a.name]
  - [$doc.f.user_id, $review.a.user_id, $user.a.id]
  - [$doc.f.user_name, $user.a.name]
"""
import abc
import collections.abc
import logging
import sys
import weakref

from . import abstract
from . import dyn
from . import import_module_class
from . import record
from . import singleton
from . import typelib


LOG = logging.getLogger(__name__)


ROOT_NAMESPACE = {}
NAMESPACE = dyn.Var(ROOT_NAMESPACE)
KEYED_NAMESPACES = weakref.WeakKeyDictionary()

LOAD_TAGS = dyn.Var()
STORE_TAGS = dyn.Var()

NEWABLE_TYPES = weakref.WeakKeyDictionary()
CONTRAVARIANT_TYPES = weakref.WeakKeyDictionary()

SELF_TYPE = dyn.Var(None)


@abstract
class Att:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def install(self, args_builder):
        raise NotImplementedError()

    def install_with_name(self, name, args_builder):
        return self.install(args_builder)


class Arg(Att):

    def install_with_name(self, name, args_builder):
        args_builder.add_field(name, *self.args, **self.kwargs)


class Populate(Att):

    def install(self, args_builder):
        args_builder.add_populator(*self.args, **self.kwargs)


class Validate(Att):

    def install(self, args_builder):
        args_builder.add_validator(*self.args, **self.kwargs)


class EmptyClass:
    pass


class NewableBuilder:

    def __init__(self):
        super().__init__()
        self.atts = []

    def add_att(self, att):
        self.atts.append(att)

    def register(self, cls, obj, module_globals=None):
        if obj is None:
            return
        if isinstance(obj, collections.abc.Mapping):
            ns, names = obj, [cls.__name__]
        else:
            fst = obj[0]
            if isinstance(fst, (list, tuple)):
                for item in obj:
                    self.register(cls, item, module_globals=module_globals)
                return
            ns = obj[0]
            names = obj[1:]
        if not isinstance(ns, collections.abc.Mapping):
            ns = KEYED_NAMESPACES.setdefault(ns, {})
        for name in names:
            if name in ns:
                if module_globals is not None or module_globals.get('__name__') == '__main__':
                    LOG.warn('Duplicate registration detected from __main__')
                raise NameError(name)
            ns[name] = cls

    def build(self, cls, abstract=False, module_globals=None, register=None, arg_equality=False, contravariant=False, no_pickling=False):
        dct = dict(cls.__dict__.items())
        for k in record.IGNORED_DICT_KEYS:
            if k in dct:
                del dct[k]

        args_builder = record.RecordBuilder()
        for base in cls.__bases__:
            if base in NEWABLE_TYPES:
                args_builder.add_base(base.Args)
        arg_order = []
        for att in self.atts:
            if isinstance(att, Arg):
                arg_order.append(att)
            else:
                att.install(args_builder)
        arg_names = {}
        for k in dir(cls):
            try:
                v = object.__getattribute__(cls, k)
            except AttributeError:
                continue
            if isinstance(v, Att):
                if isinstance(v, Arg):
                    if k in arg_names:
                        raise NameError('Duplicate names', v, k, arg_names[v])
                    arg_names[v] = k
                else:
                    v.install_with_name(k, args_builder)
        for arg in arg_order:
            name = arg_names.pop(arg)
            arg.install_with_name(name, args_builder)
        if arg_names:
            raise NameError(arg_names)

        if 'Args' in dct:
            if self.atts:
                raise TypeError('Cannot override Args with atts', self.atts)
        else:
            dct['Args'] = args_builder.build(
                'Args',
                pickle_path=None if no_pickling else cls.__name__,
                module_globals=module_globals)

        @classmethod
        def _new_args(cls, *args, **kwargs):
            if len(args) == 1 and not kwargs and isinstance(args[0], cls.Args):
                return args[0]
            else:
                return cls.Args(*args, **kwargs)
        dct['_new_args'] = _new_args

        def _init_args(self, *args, **kwargs):
            if hasattr(self, '_args'):
                if not isinstance(self._args, self.Args):
                    raise TypeError(self._args, self.Args)
            else:
                self._args = self._new_args(*args, **kwargs)
        dct['_init_args'] = _init_args

        if cls.__init__ == EmptyClass.__init__:
            def __init__(self, *args, **kwargs):
                self._init_args(*args, **kwargs)
                super(cls, self) .__init__()
            dct['__init__'] = __init__

        if cls.__repr__ == EmptyClass.__repr__:
            def __repr__(self):
                return record.build_attr_repr(self, ('_args',))
            dct['__repr__'] = __repr__

        for k, v in list(cls.__dict__.items()):
            if isinstance(v, Arg):
                def make_get(name):
                    def get(self):
                        return getattr(self._args, name)
                    return get
                get = make_get(k)
                get.__name__ = 'get_' + k
                dct[k] = property(get)

        if arg_equality:
            def __hash__(self):
                return hash(self._args)
            dct.setdefault('__hash__', __hash__)

            def __eq__(self, other):
                return type(other) is type(self) and self._args.__eq__(other._args)
            dct.setdefault('__eq__', __eq__)

            def __ne__(self, other):
                return type(other) is not type(self) or self._args.__ne__(other._args)
            dct.setdefault('__ne__', __ne__)

        mcls = abc.ABCMeta if abstract else type
        cls = mcls(cls.__name__, cls.__bases__, dct)
        if abstract:
            cls.__metaclass__ = abc.ABCMeta

        NEWABLE_TYPES[cls] = None

        if contravariant:
            CONTRAVARIANT_TYPES[cls] = None

        self.register(cls, register, module_globals=module_globals)

        return cls


def newable_(**kwargs):
    def inner(cls):
        module_globals = sys._getframe(1).f_globals
        try:
            builder = cls.__dict__['_builder']
        except KeyError:
            builder = NewableBuilder()
        return builder.build(cls, module_globals=module_globals, **kwargs)
    return inner


def newable_att(cls):
    def inner(*args, **kwargs):
        cls_dct = sys._getframe(1).f_locals
        try:
            builder = cls_dct['_builder']
        except KeyError:
            builder = cls_dct['_builder'] = NewableBuilder()
        att = cls(*args, **kwargs)
        builder.add_att(att)
        return att
    return inner


class SelfTypeSpecification(typelib.SimpleTypeSpecification):

    def __init__(self, default_type=None):
        if not isinstance(default_type, (type, type(None))):
            raise TypeError(_type)
        self.default_type = default_type

    @property
    def type(self):
        return SELF_TYPE() or self.default_type

    def __repr__(self):
        return 'SelfType(%r)' % (self.type,)

    @property
    def checker(self):
        def fn(obj):
            if self.type is None:
                return False
            return isinstance(obj, self.type)
        return fn

    def to_dict_item(self, obj, for_key=False):
        return obj.args._to_dict(for_key=for_key)

    def from_dict_item(self, obj):
        if self.type is None:
            raise TypeError('No self_type bound and no default')
        return new(self.type, self.type.Args._from_dict(obj))


class NewableTypeSpecification(typelib.TypeSpecification):

    def __init__(self, _type):
        super().__init__()
        if _type not in NEWABLE_TYPES:
            raise TypeError(_type)
        self.type = _type

    def __repr__(self):
        return 'Newable(%r)' % (self.type,)

    @property
    def checker(self):
        _type = self.type
        _isinstance = isinstance

        def fn(obj):
            return _isinstance(obj, _type)
        return fn

    def to_dict_item(self, obj, for_key=False):
        return obj.args._to_dict(for_key=for_key)

    def from_dict_item(self, obj):
        return new(self.type, self.type.Args._from_dict(obj))


class RefNewableTypeSpecification(typelib.TypeSpecification):

    def __init__(self, type_spec, key=None, namespace=None):
        super().__init__()
        if not isinstance(type_spec, typelib.TypeSpecification):
            raise TypeError(type_spec)
        if namespace is not None and not isinstance(namespace, collections.abc.Mapping):
            raise TypeError(namespace)
        self.type_spec = type_spec
        self.namespace = namespace
        self.key = key

    def __repr__(self):
        return 'RefNewable(%r)' % (self.type_spec,)

    @property
    def checker(self):
        return self.type_spec.checker

    def from_dict_item(self, obj):
        if self.checker(obj):
            return obj
        elif isinstance(obj, collections.abc.Mapping) and len(obj) == 1:
            [[type_ref, args]] = obj.items()
        # elif isinstance(obj, (tuple, list)) and len(obj) == 2:
        #     type_ref, args = obj
        elif isinstance(obj, str):
            if obj.startswith(TAG_SIGIL):
                tag, _, attr_path = obj[1:].partition('.')
                for tags in LOAD_TAGS:
                    try:
                        obj = LOAD_TAGS()[tag]
                    except KeyError:
                        continue
                    while attr_path:
                        attr, _, attr_path = attr_path.partition('.')
                        obj = getattr(obj, attr)
                    break
                else:
                    raise KeyError(tag)
                return obj
            else:
                type_ref, args = obj, {}
        else:
            # return super().from_dict_item(obj)
            raise TypeError(self, obj)
        local_namespace = None
        contravariant_target = None
        if self.key is not None:
            local_namespace = KEYED_NAMESPACES.get(self.key)
        if isinstance(self.type_spec, (record.SimpleTypeSpecification, NewableTypeSpecification)):
            contravariant_target = self.type_spec.type
            if local_namespace is None:
                local_namespace = KEYED_NAMESPACES.get(self.type_spec.type)
        with NAMESPACE(self.namespace or {}):
            with SELF_TYPE(None):
                return new(type_ref, args, local_namespace=local_namespace, contravariant_target=contravariant_target)


class TypeSpecificationBuilders:

    def __new__(*args, **kwargs):
        raise TypeError()

    @typelib.TypeSpecification.builder(lambda obj: isinstance(obj, type) and obj in NEWABLE_TYPES, first=True)
    def newable_builder(obj):
        return NewableTypeSpecification(obj)


def newable_ref(obj=object, **kwargs):
    return RefNewableTypeSpecification(typelib.TypeSpecification.build(obj), **kwargs)


TAG_SIGIL = '$'


class TypeRefError(TypeError):
    pass


def resolve_type_ref(type_ref, already_keyed=False):
    if isinstance(type_ref, type) and type_ref in NEWABLE_TYPES:
        return type_ref
    if not already_keyed and type_ref in KEYED_NAMESPACES:
        with NAMESPACE(KEYED_NAMESPACES[type_ref]):
            return resolve_type_ref(type_ref, already_keyed=True)
    if isinstance(type_ref, str):
        if TAG_SIGIL in type_ref:
            raise TypeError(type_ref)
        for ns in NAMESPACE:
            if type_ref in ns:
                return resolve_type_ref(ns[type_ref])
        if hasattr(__builtins__, type_ref):
            return resolve_type_ref(getattr(__builtins__, type_ref))
        if '.' in type_ref:
            return resolve_type_ref(import_module_class(type_ref))
    raise TypeRefError(type_ref)


def new(type_ref, args=None, namespace=None, tags=None, local_namespace=None, contravariant_target=None):
    if namespace is not None:
        with NAMESPACE(namespace):
            return new(
                type_ref,
                args,
                tags=tags,
                local_namespace=local_namespace,
                contravariant_target=contravariant_target)
    if tags is not None:
        with LOAD_TAGS(tags):
            with STORE_TAGS(tags):
                return new(
                    type_ref,
                    args,
                    local_namespace=local_namespace,
                    contravariant_target=contravariant_target)
    try:
        LOAD_TAGS()
        STORE_TAGS()
    except dyn.UnboundVarError:
        return new(
            type_ref,
            args,
            local_namespace=local_namespace,
            tags={},
            contravariant_target=contravariant_target)

    if isinstance(type_ref, collections.abc.Mapping):
        if args is not None:
            raise TypeError(type_ref)
        elif len(type_ref) == 1:
            [[type_ref, args]] = type_ref.items()
        elif len(type_ref) == 2 and TAG_SIGIL in type_ref:
            tag_block = type_ref.pop(TAG_SIGIL)
            if not isinstance(tag_block, collections.abc.Mapping):
                raise TypeError(tag_block)
            tags = {}
            with STORE_TAGS(tags):
                def rec(tag_block):
                    if TAG_SIGIL in tag_block:
                        rec(tag_block[TAG_SIGIL])
                    for obj_type_ref, obj_args in tag_block.items():
                        if obj_type_ref != TAG_SIGIL:
                            new(
                                obj_type_ref,
                                obj_args,
                                namespace=namespace,
                                local_namespace=local_namespace,
                                contravariant_target=contravariant_target)
                rec(tag_block)
            with LOAD_TAGS(tags):
                return new(
                    type_ref,
                    args,
                    local_namespace=local_namespace,
                    contravariant_target=contravariant_target)
        else:
            raise TypeError(type_ref)

    tag = None
    if isinstance(type_ref, str):
        if type_ref == TAG_SIGIL:
            if not isinstance(args, str):
                raise TypeError(args)
            tag, _, attr_path = args.partition('.')
            for tags in LOAD_TAGS:
                try:
                    obj = tags[tag]
                except KeyError:
                    continue
                while attr_path:
                    attr, _, attr_path = attr_path.partition('.')
                    obj = getattr(obj, attr)
                break
            else:
                raise KeyError(tag)
            return obj
        elif TAG_SIGIL in type_ref:
            type_ref, tag = type_ref.split(TAG_SIGIL)
            if '.' in tag:
                raise NameError(tag)

    with NAMESPACE(local_namespace or {}):
        try:
            cls = resolve_type_ref(type_ref)
        except TypeRefError:
            if not contravariant_target:
                raise
            for scls in contravariant_target.__mro__[1:]:
                scls_local_namespace = KEYED_NAMESPACES.get(scls)
                if not scls_local_namespace:
                    continue
                try:
                    with NAMESPACE(scls_local_namespace):
                        cls = resolve_type_ref(type_ref)
                except TypeRefError:
                    continue
                if cls in CONTRAVARIANT_TYPES:
                    break
            else:
                raise TypeRefError(type_ref)

    if cls not in NEWABLE_TYPES:
        raise TypeError(cls)
    if contravariant_target is not None and not issubclass(cls, contravariant_target) and cls in CONTRAVARIANT_TYPES:
        # EXPERIMENTAL
        cls = NewableBuilder().build(
            type(cls.__name__ + '$' + contravariant_target.__name__, (cls, contravariant_target), {}),
            no_pickling=True)
        self_type = contravariant_target
    else:
        self_type = None

    with SELF_TYPE(self_type):
        if isinstance(args, cls.Args):
            pass
        elif isinstance(args, collections.abc.Mapping):
            args = cls.Args._from_dict(args)
        elif args is None:
            args = cls.Args._from_dict({})
        elif len(cls.Args._args) == 1:
            arg_name = cls.Args._args[0]
            arg_field = cls.Args._builder.get_field(arg_name)
            arg_val = arg_field.type_specification.from_dict_item(args)
            args = cls.Args(**{arg_name: arg_val})
        else:
            raise TypeError(args)

    with SELF_TYPE(None):
        obj = cls(args)
    if tag is not None:
        tags = STORE_TAGS()
        if tag in tags:
            raise KeyError(tag)
        tags[tag] = obj

    return obj


@singleton()
class newable:

    __call__ = staticmethod(newable_)
    arg = staticmethod(newable_att(Arg))
    populate = staticmethod(newable_att(Populate))
    validate = staticmethod(newable_att(Validate))
    ref = staticmethod(newable_ref)
    new = staticmethod(new)
    Self = SelfTypeSpecification
