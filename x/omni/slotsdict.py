"""
$ python slots_dict.py 30 1000000
AdaptiveSlotsDict, z=30, n=1000000... 386,095,488B, 50s
$ python slots_dict.py 30 1000000 -d
dict, z=30, n=1000000... 3,478,788,480B, 15s


from operator import attrgetter
from sqlalchemy.orm.instrumentation import ClassManager
import slots_dict

class SlotsClassManager(ClassManager):

    def __init__(self, class_):
        super().__init__(class_)
        self._dict_type = slots_dict.AdaptiveSlotsDict()

    def new_instance(self, state=None):
        obj = super().new_instance(state)
        setattr(obj, '_sa_dict', self._dict_type())
        return obj

    def dict_getter(self):
        return attrgetter('_sa_dict')
"""
import collections.abc

from omlish import lang


ILLEGAL_KEYS = {'__class__'}


def SlotsDict(keys, name='SlotsDict'):
    _AttributeError = AttributeError
    _KeyError = KeyError
    _Mapping = collections.abc.Mapping
    _TypeError = TypeError
    _delattr = delattr
    _getattr = getattr
    _hasattr = hasattr
    _illegal_keys = ILLEGAL_KEYS
    _isinstance = isinstance
    _len = len
    _setattr = setattr

    class SlotsDictBase(collections.abc.MutableMapping):
        __slots__ = ('_container', '_len')

        def __init__(self, *args, **kwargs):
            if _len(args) > 1:
                raise _TypeError
            container_type = self._container_type
            container = container_type.__new__(container_type)
            self._container = container
            self._len = 0
            setitem = self.__setitem__
            if args:
                src, = args
                if _isinstance(src, _Mapping):
                    getitem = src.__getitem__
                    for k in src:
                        setitem(k, getitem(k))
                else:
                    for k, v in src:
                        setitem(k, v)
            for k, v in kwargs.items():
                setitem(k, v)

        def __getitem__(self, k):
            try:
                return _getattr(self._container, k)
            except _AttributeError:
                raise _KeyError(k)

        def __setitem__(self, k, v):
            if k in _illegal_keys:
                raise _KeyError(k)
            container = self._container
            if not _hasattr(container, k):
                self._len += 1
            _setattr(self._container, k, v)

        def __delitem__(self, k):
            if k in self._illegal_keys:
                raise _KeyError(k)
            try:
                _delattr(self._container, k)
            except _AttributeError:
                raise _KeyError(k)
            else:
                self._len -= 1

        def __iter__(self):
            container = self._container
            return (k for k in self._container_type.__slots__ if _hasattr(container, k))

        def __len__(self):
            return self._len

    container_type = lang.new_type(name + '_Container', (object,), {'__slots__': tuple(keys)})
    dict_type = lang.new_type(name, (SlotsDictBase,), {'__slots__': (), '_container_type': container_type})
    return dict_type


def AdaptiveSlotsDict(keys=(), name='AdaptiveSlotsDict'):
    _AttributeError = AttributeError
    _KeyError = KeyError
    _Mapping = collections.abc.Mapping
    _delattr = delattr
    _getattr = getattr
    _hasattr = hasattr
    _illegal_keys = ILLEGAL_KEYS
    _isinstance = isinstance
    _setattr = setattr

    def create_container_type(keys):
        return type(
            name + '_Container',
            (object,),
            {'__slots__': tuple(set(keys))})

    class AdaptiveSlotsDictBase(collections.abc.MutableMapping):
        __slots__ = ('_container', '_len')

        def __init__(self, *args, **kwargs):
            container_type = self._container_type
            container = container_type.__new__(container_type)
            self._container = container
            self._len = 0
            setitem = self.__setitem__
            if args:
                src, = args
                if _isinstance(src, _Mapping):
                    getitem = src.__getitem__
                    for k in src:
                        setitem(k, getitem(k))
                else:
                    for k, v in src:
                        setitem(k, v)
            for k, v in kwargs.items():
                setitem(k, v)

        def __getitem__(self, k):
            try:
                return _getattr(self._container, k)
            except _AttributeError:
                raise _KeyError(k)

        def __setitem__(self, k, v):
            if k in _illegal_keys:
                raise _KeyError(k)
            container = self._container
            if not _hasattr(container, k):
                self._len += 1
            try:
                _setattr(container, k, v)
            except _AttributeError:
                slots = self._container_type.__slots__
                if k in slots:
                    new_container_type = self._container_type
                else:
                    new_container_type = create_container_type(slots + (k,))
                new_container = new_container_type.__new__(new_container_type)
                getitem = self.__getitem__
                for _k in self:
                    _setattr(new_container, _k, getitem(_k))
                _setattr(new_container, k, v)
                self._container = new_container
                type(self)._container_type = new_container_type

        def __delitem__(self, k):
            if k in _illegal_keys:
                raise _KeyError(k)
            container = self._container
            try:
                _delattr(container, k)
            except _AttributeError:
                raise _KeyError(k)
            else:
                self._len -= 1

        def __iter__(self):
            container = self._container
            return (k for k in self._container_type.__slots__ if _hasattr(container, k))

        def __len__(self):
            return self._len

    container_type = create_container_type(keys)
    dict_type = lang.new_type(
        name,
        (AdaptiveSlotsDictBase,),
        {'__slots__': (), '_container_type': container_type})
    return dict_type


def AutoSlot(default_slots=()):
    dict_type = AdaptiveSlotsDict(default_slots)
    _getitem = dict_type.__getitem__
    _setitem = dict_type.__setitem__
    _delitem = dict_type.__delitem__
    _contains = dict_type.__contains__
    _KeyError = KeyError
    _AttributeError = AttributeError
    dict_key = '__slots_dict__'
    _getattribute = object.__getattribute__

    def inner(cls):
        if not hasattr(cls, '__slots__'):
            raise TypeError

        class Wrapper(cls):
            __slots__ = (dict_key)

            def __new__(cls, *args, **kwargs):
                obj = super().__new__(cls)
                object.__setattr__(obj, dict_key, dict_type())
                return obj

            def __getattribute__(self, k):
                try:
                    return _getitem(_getattribute(self, dict_key), k)
                except _KeyError:
                    return _getattribute(self, k)

            def __setattr__(self, k, v):
                _setitem(_getattribute(self, dict_key), k, v)

            def __delattr__(self, k):
                try:
                    _delitem(_getattribute(self, dict_key), k)
                except _KeyError:
                    raise _AttributeError(k)

            def __hasattr__(self, k):
                return _contains(_getattribute(self, dict_key), k)

        Wrapper.__name__ = cls.__name__
        return Wrapper

    return inner


if __name__ == '__main__':
    import optparse
    op = optparse.OptionParser()
    op.add_option('-d', '--dict', dest='use_dict', action='store_true')
    opts, args = op.parse_args()

    import sys
    z, n = map(int, args)
    sys.stderr.write('%s, z=%d, n=%d... ' % ('dict' if opts.use_dict else 'AdaptiveSlotsDict', z, n))

    import time
    base_time = time.time()

    def get_mem():
        import os
        import psutil
        return psutil.Process(os.getpid()).memory_info().rss
    base_mem = get_mem()

    kvs = [('_' + str(i), i) for i in range(z)]

    T = dict if opts.use_dict else AdaptiveSlotsDict()
    l = [T(kvs) for _ in range(n)]

    used_time = time.time() - base_time
    used_mem = get_mem() - sys.getsizeof(l) - base_mem

    def comma_digit(n):
        s = str(n)[::-1]
        return ','.join(s[i:i + 3] for i in range(0, len(s), 3))[::-1]

    sys.stderr.write('%sB, %0.2fs\n' % (comma_digit(used_mem), used_time))
