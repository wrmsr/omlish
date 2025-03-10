import abc
import collections.abc
import typing as ta


##


class AttrOps(abc.ABC):
    class NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    @abc.abstractmethod
    def getattr(self, obj: ta.Any, name: str, default: ta.Any = NOT_SET) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def setattr(self, obj: ta.Any, name: str, value: ta.Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def delattr(self, obj: ta.Any, name: str) -> None:
        raise NotImplementedError


##


class StdAttrOps(AttrOps):
    def getattr(self, obj: ta.Any, name: str, default: ta.Any = AttrOps.NOT_SET) -> ta.Any:
        if default is AttrOps.NOT_SET:
            return getattr(obj, name)
        else:
            return getattr(obj, name, default)

    def setattr(self, obj: ta.Any, name: str, value: ta.Any) -> None:
        setattr(obj, name, value)

    def delattr(self, obj: ta.Any, name: str) -> None:
        delattr(obj, name)


STD_ATTR_OPS = StdAttrOps()


##


class DictAttrOps(AttrOps):
    def __init__(self, dct: ta.MutableMapping[str, ta.Any] | None = None) -> None:
        super().__init__()

        if dct is None:
            dct = {}
        self._dct = dct

    def getattr(self, obj: ta.Any, name: str, default: ta.Any = AttrOps.NOT_SET) -> ta.Any:
        try:
            return self._dct[name]
        except KeyError:
            if default is not AttrOps.NOT_SET:
                return default
            raise AttributeError(name) from None

    def setattr(self, obj: ta.Any, name: str, value: ta.Any) -> None:
        self._dct[name] = value

    def delattr(self, obj: ta.Any, name: str) -> None:
        try:
            del self._dct[name]
        except KeyError:
            raise AttributeError(name) from None


##


class TransientDict(collections.abc.MutableMapping):
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict = {}

    def __reduce__(self):
        return (TransientDict, ())

    def __getitem__(self, item):
        return self._dct[item]

    def __setitem__(self, key, value):
        self._dct[key] = value

    def __delitem__(self, key):
        del self._dct[key]

    def __len__(self):
        return len(self._dct)

    def __iter__(self):
        return iter(self._dct)

    def clear(self):
        self._dct.clear()

    def items(self):
        return self._dct.items()

    def keys(self):
        return self._dct.keys()

    def values(self):
        return self._dct.values()

    def __contains__(self, key, /):
        return super().__contains__(key)

    def __eq__(self, other, /):
        raise TypeError(self)


#


_TRANSIENT_DICT_ATTR = '__transient_dict__'


def _get_object_transient_dict(obj: ta.Any) -> TransientDict:
    try:
        return obj.__dict__[_TRANSIENT_DICT_ATTR]
    except KeyError:
        return obj.__dict__.setdefault(_TRANSIENT_DICT_ATTR, TransientDict())


class TransientAttrOps(AttrOps):
    def getattr(self, obj: ta.Any, name: str, default: ta.Any = AttrOps.NOT_SET) -> ta.Any:
        td = _get_object_transient_dict(obj)
        try:
            return td[name]
        except KeyError:
            if default is not AttrOps.NOT_SET:
                return default
            raise AttributeError(name) from None

    def setattr(self, obj: ta.Any, name: str, value: ta.Any) -> None:
        td = _get_object_transient_dict(obj)
        td[name] = value

    def delattr(self, obj: ta.Any, name: str) -> None:
        td = _get_object_transient_dict(obj)
        try:
            del td[name]
        except KeyError:
            raise AttributeError(name) from None


TRANSIENT_ATTR_OPS = TransientAttrOps()

transient_getattr = TRANSIENT_ATTR_OPS.getattr
transient_setattr = TRANSIENT_ATTR_OPS.setattr
transient_delattr = TRANSIENT_ATTR_OPS.delattr
