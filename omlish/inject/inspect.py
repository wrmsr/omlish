import inspect
import typing as ta
import weakref


_signature_cache: ta.MutableMapping[ta.Any, inspect.Signature] = weakref.WeakKeyDictionary()


def signature(obj: ta.Any) -> inspect.Signature:
    try:
        return _signature_cache[obj]
    except TypeError:
        return inspect.signature(obj)
    except KeyError:
        pass
    sig = inspect.signature(obj)
    _signature_cache[obj] = sig
    return sig
