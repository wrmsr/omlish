"""
A self-awarely unpythonic set of helpers for defining common boilerplate methods (repr, hash_eq, delegates, etc) in
class definitions. Should be used sparingly for methods not directly used by humans (like repr) - @property's should
remain @property's for type annotation, tool assistance, debugging, and otherwise, but these are still nice to have in
certain circumstances (the real-world alternative usually being simply not adding them).
"""
import abc
import functools
import operator
import threading

from . import lang


_repr = repr

BASICS = {}


def _basic(fn):
    if fn.__name__ in BASICS:
        raise NameError(fn.__name__)
    BASICS[fn.__name__] = fn
    return fn


@lang.cls_dct_fn()
def basic(cls_dct, *attrs, basics=None):
    if basics is None:
        basics = BASICS.keys()
    for k in basics:
        fn = BASICS[k]
        fn(*attrs, cls_dct=cls_dct)


_REPR_SEEN = threading.local()


def _repr_guard(fn):
    @functools.wraps(fn)
    def inner(obj, *args, **kwargs):
        try:
            ids = _REPR_SEEN.ids
        except AttributeError:
            ids = _REPR_SEEN.ids = set()
            try:
                ids.add(id(obj))
                return fn(obj, *args, **kwargs)
            finally:
                del _REPR_SEEN.ids
        else:
            if id(obj) in ids:
                return f'<seen:{type(obj).__name__}@{hex(id(obj))[2:]}>'
            ids.add(id(obj))
            return fn(obj, *args, **kwargs)

    return inner


@_repr_guard
def build_attr_repr(obj, *, mro=False):
    if mro:
        attrs = [
            attr
            for ty in sorted(reversed(type(obj).__mro__), key=lambda _ty: _ty.__dict__.get('__repr_priority__', 0))
            for attr in ty.__dict__.get('__repr_attrs__', [])]
    else:
        attrs = obj.__repr_attrs__
    return '%s@%s(%s)' % (
        type(obj).__name__,
        hex(id(obj))[2:],
        ', '.join('%s=%s' % (attr, '<self>' if value is obj else _repr(value))
                  for attr in attrs for value in [getattr(obj, attr)]))


@_repr_guard
def build_repr(obj, *attrs):
    return '%s@%s(%s)' % (
        type(obj).__name__,
        hex(id(obj))[2:],
        ', '.join('%s=%r' % (attr, getattr(obj, attr)) for attr in attrs))


@_basic
@lang.cls_dct_fn()
def repr(cls_dct, *attrs, mro=False, priority=None):
    def __repr__(self):
        return build_attr_repr(self, mro=mro)

    cls_dct['__repr_attrs__'] = attrs
    if priority is not None:
        cls_dct['__repr_priority__'] = priority
    cls_dct['__repr__'] = __repr__


@lang.cls_dct_fn()
def bare_repr(cls_dct, *attrs):
    def __repr__(self):
        return lang.attr_repr(self, *attrs)

    cls_dct['__repr__'] = __repr__


@lang.cls_dct_fn()
def name_repr(cls_dct):
    def __repr__(self):
        return self.__name__

    cls_dct['__repr__'] = __repr__


@lang.cls_dct_fn()
def ne(cls_dct):
    def __ne__(self, other):
        return not (self == other)

    cls_dct['__ne__'] = __ne__


@lang.cls_dct_fn()
def no_order(cls_dct, *, raise_=None):
    def fn(self, other):
        if raise_ is None:
            return NotImplemented
        else:
            raise raise_

    for att in [
        '__lt__',
        '__le__',
        '__gt__',
        '__ge__',
    ]:
        cls_dct[att] = fn


@_basic
@lang.cls_dct_fn()
def hash_eq(cls_dct, *attrs):
    def __hash__(self):
        return hash(tuple(getattr(self, attr) for attr in attrs))

    cls_dct['__hash__'] = __hash__

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        for attr in attrs:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    cls_dct['__eq__'] = __eq__

    ne(cls_dct=cls_dct)


@lang.cls_dct_fn()
def getter(cls_dct, *attrs):
    for attr in attrs:
        cls_dct[attr] = property(operator.attrgetter('_' + attr))


@lang.cls_dct_fn()
def not_implemented(cls_dct, *names, **kwargs):
    wrapper = kwargs.pop('wrapper', lambda _: _)
    if kwargs:
        raise TypeError(kwargs)
    ret = []
    for name in names:
        @wrapper
        def not_implemented(self, *args, **kwargs):
            raise NotImplementedError

        not_implemented.__name__ = name
        cls_dct[name] = not_implemented
        ret.append(not_implemented)
    return tuple(ret)


@lang.cls_dct_fn()
def abstract_method(cls_dct, *names):
    return not_implemented(cls_dct, *names, wrapper=abc.abstractmethod)


@lang.cls_dct_fn()
def abstract_property(cls_dct, *names):
    return not_implemented(cls_dct, *names, wrapper=abc.abstractmethod)


@lang.cls_dct_fn()
def abstract_hash_eq(cls_dct):
    return not_implemented(cls_dct, '__hash__', '__eq__', '__ne__', wrapper=abc.abstractmethod)
