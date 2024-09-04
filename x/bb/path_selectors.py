"""
is required (raises MissingSignal)
ignore return value
immutable

update
rename
delete

all
name
idx

filter

ignore
nuke value
nuke to path
nuke chunk
reraise
"""

import copy
import functools


def parse_slice(s):
    return slice(*map(lambda i: int(i) if i else None, s.split(':')))


class BaseError(BaseException):
    pass


class InvalidOperationError(BaseError):
    pass


class NotFoundError(BaseError):
    pass


class MutateSignal(BaseException):
    pass


class SetSignal(MutateSignal):

    def __init__(self, new_value):
        self.new_value = new_value


class DeleteSignal(MutateSignal):
    pass


class MoveSignal(MutateSignal):

    def __init__(self, new_key, new_value):
        self.new_key = key
        self.new_value = value


class MutationWatcher(object):

    def __init__(self, fn):
        self.fn = fn
        self.is_dirty = False

    def __call__(self, *args, **kwargs):
        try:
            return self.fn(*args, **kwargs)

        except MutateSignal as sig:
            self.is_dirty = True

            raise sig


class Adapter(object):

    def copy(self, obj):
        return copy.copy(obj)

    @classmethod
    def select(cls, obj):
        if isinstance(obj, list):
            return ListAdapter()

        elif isinstance(obj, tuple):
            return TupleAdapter()

        elif isinstance(obj, dict):
            return DictAdapter()

        else:
            return ObjectAdapter()

    @classmethod
    def with_select(cls, fn):
        @functools.wraps(fn)
        def inner(obj, *args, **kwargs):
            adapter = cls.select(obj)

            return fn(adapter, obj, *args, **kwargs)

        return inner

    def handle_transform(self, fn, key, obj):
        try:
            fn()

        except SetSignal as sig:
            self.set(obj, key, sig.new_value)

        except DeleteSignal as sig:
            self.delete(obj, key)

        except MoveSignal as sig:
            self.move(obj, key, sig.new_key, sig.new_value)

        return obj

    def void_handle_transform(self, fn, key, obj):
        try:
            fn()

        except MutateSignal:
            raise InvalidOperationError()

    def immutable_handle_transform(self, fn, key, obj):
        try:
            fn()

        except SetSignal as sig:
            obj = self.copy(obj)

            self.set(obj, key, sig.new_value)

            raise SetSignal(obj)

        except DeleteSignal as sig:
            obj = self.copy(obj)

            self.delete(obj, key)

            raise SetSignal(obj)

        except MoveSignal as sig:
            obj = self.copy(obj)

            self.move(obj, key, sig.new_key, sig.new_value)

            raise SetSignal(obj)

        return obj

    def transform(self, handler, fn, key, obj):
        # ugliest part of code. rewrite this.

        if self.is_iter_key(key):
            watcher = MutationWatcher(fn)

            it = self.to_iter(obj, key)

            trans_it = self.handle_iter_transform(watcher, it)

            value = self.from_iter(trans_it)

            if watcher.is_dirty:
                raise SetSignal(value)

            return value

        else:
            inner = lambda: fn(self.get(obj, key) if key != '' else obj)

            return handler(inner, key, obj)


class NamedAdapter(Adapter):

    def parse_key(self, tok):
        if ',' in tok:
            return set(tok.split(','))

        return tok

    def is_iter_key(self, key):
        return isinstance(key, set) or key == '*'

    def move(self, obj, key, new_key, new_value):
        self.delete(obj, key)

        self.set(dct, new_key, new_value)

    def handle_iter_transform(self, fn, it):
        for name, value in it:
            try:
                fn((name, value))

                yield name, value

            except SetSignal as sig:
                yield name, sig.new_value

            except DeleteSignal as sig:
                pass

            except MoveSignal as sig:
                yield sig.new_name, sig.new_value


class DictAdapter(NamedAdapter):

    def has(self, dct, name):
        return name in dct

    def get(self, dct, name):
        return dct[name]

    def set(self, dct, name, value):
        dct[name] = value

    def delete(self, dct, name):
        del dct[name]

    def to_iter(self, dct, key):
        if key == '*':
            return dct.iteritems()

        if isinstance(key, set):
            return dict((name, self.get(dct, name)) for name in key).items()

        raise KeyError()

    def from_iter(self, it):
        return dict(it)

    def copy(self, dct):
        return dct.copy()


class ObjectAdapter(NamedAdapter):

    def has(self, obj, name):
        hasattr(obj, name)

    def get(self, obj, name):
        getattr(obj, name)

    def set(self, obj, name, value):
        setattr(obj, name, value)

    def delete(self, obj, name):
        delattr(obj, name)

    def to_iter(self, obj, key=None):
        if key == '*':
            return dir(obj)

        if isinstance(key, set):
            return dict((name, self.get(dct, name)) for name in key).items()

        raise KeyError()


class IndexedAdapter(Adapter):

    def parse_key(self, tok):
        if ':' in tok:
            return parse_slice(tok)

        if tok == '*':
            return slice(None)

        return int(tok)

    def is_iter_key(self, key):
        return isinstance(key, slice)

    def has(self, seq, idx):
        return len(obj) > idx > -len(obj)

    def get(self, seq, idx):
        return seq[idx]

    def to_iter(keyf, obj, key=None):
        if key is not None:
            return obj[key]

        return iter(obj)

    def handle_iter_transform(self, fn, it):
        for item in it:
            try:
                fn(item)

                yield item

            except SetSignal as sig:
                yield sig.new_value

            except DeleteSignal as sig:
                pass

            except MoveSignal as sig:
                raise InvalidOperationError()


class ListAdapter(IndexedAdapter):

    def set(self, lst, idx, value):
        lst[idx] = value

    def delete(self, lst, idx):
        del lst[idx]

    def from_iter(self, it):
        return list(it)

    def copy(self, lst):
        return list(lst)


class TupleAdapter(IndexedAdapter):

    def from_iter(self, it):
        return tuple(it)

    def copy(adapter, tpl):
        return tuple(tpl)


def transform_gate(fn, value):
    try:
        return fn(value)

    except SetSignal as sig:
        return sig.new_value

    except DeleteSignal as sig:
        return None

    except MoveSignal as sig:
        return sig.new_value


def with_transform_gate(fn):
    return functools.partial(transform_gate, fn)


def transform_endpoint(fn, value):
    new_value = fn(value)

    if new_value != value:
        raise SetSignal(new_value)


def name_transform_endpoint(fn, name, value):
    new_name, new_value = fn(name, value)

    if new_name != name:
        raise MoveSignal(new_name, new_value)

    elif new_value != value:
        raise SetSignal(name, new_value)

    return new_value


def delete_transform_endpoint(value):
    raise DeleteSignal()


def with_tok_transform(tok, handler_prefix=''):
    handler_fn_name = handler_prefix + 'handle_transform'

    def outer(fn):
        @Adapter.with_select
        def inner(adapter, obj):
            handler = getattr(adapter, handler_fn_name)

            key = adapter.parse_key(tok)

            return adapter.transform(handler, fn, key, obj)

        return inner

    return outer


def build_path_transform(fn, path, transform_type='', with_name=False):
    if with_name:
        endpoint = name_transform_endpoint
    else:
        endpoint = transform_endpoint

    if transform_type == '':
        handler_prefix = ''
        transform = functools.partial(endpoint, fn)

    elif transform_type == 'void':
        handler_prefix = 'void_'
        transform = fn

    elif transform_type == 'immutable':
        handler_prefix = 'immutable_'
        transform = functools.partial(endpoint, fn)

    else:
        raise ValueError()

    for tok in path.split('.')[::-1]:
        transform = with_tok_transform(tok, handler_prefix)(transform)

    return with_transform_gate(transform)


def with_path_transform(*args, **kwargs):
    def inner(fn):
        return functools.wraps(fn)(build_path_transform(fn, *args, **kwargs))

    return inner


def build_path_select(path):
    def outer(obj):
        matches = []

        @with_path_transform(path, transform_type='void')
        def inner(match):
            matches.append(match)

        inner(obj)

        return matches

    return outer


def path_select(obj, path):
    build_path_select(path)(obj)


def build_fused_path_transforms(*fn_path_pairs):
    raise NotImplemented()


if __name__ == '__main__':
    @with_path_transform('animals.*.color')
    def kindafy_animal_colors(color):
        return color + '.. kinda'


    print(
        kindafy_animal_colors(
            {'animals': [{'name': 'bob', 'color': 'red'}, {'name': 'alice', 'color': 'blue'}]}))


    @with_path_transform('animals.*.color', transform_type='immutable')
    def kindafy_animal_colors_immut(color):
        return color + '.. kinda'


    o = {'animals': [{'name': 'bob', 'color': 'red'}, {'name': 'alice', 'color': 'blue'}]}

    print(kindafy_animal_colors_immut(o))
    print(o)
