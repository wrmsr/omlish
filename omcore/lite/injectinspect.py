# @om-lite
import functools
import inspect
import typing as ta
import weakref


##


class InjectionInspection(ta.NamedTuple):
    obj: ta.Any
    unwrapped: ta.Any
    target: ta.Any

    signature: inspect.Signature
    type_hints: ta.Mapping[str, ta.Any]
    args_offset: int


class InjectionInspectionError(Exception):
    pass


##


_INJECTION_INSPECTION_CACHE: ta.MutableMapping[ta.Any, InjectionInspection] = weakref.WeakKeyDictionary()


def _do_injection_inspect(obj: ta.Any) -> InjectionInspection:
    tgt = obj

    # inspect.signature(eval_str=True) was added in 3.10 and we have to support 3.8, so we have to get_type_hints to
    # eval str annotations *in addition to* getting the signature for parameter information.
    uw = tgt
    has_partial = False
    while True:
        if isinstance(uw, functools.partial):
            uw = uw.func
            has_partial = True
        else:
            if (uw2 := inspect.unwrap(uw)) is uw:
                break
            uw = uw2

    has_args_offset = False

    if isinstance(tgt, type) and tgt.__new__ is not object.__new__:
        # Python 3.8's inspect.signature can't handle subclasses overriding __new__, always generating *args/**kwargs.
        #  - https://bugs.python.org/issue40897
        #  - https://github.com/python/cpython/commit/df7c62980d15acd3125dfbd81546dad359f7add7
        tgt = tgt.__init__  # type: ignore[misc]
        has_args_offset = True

    if tgt in (object.__init__, object.__new__):
        # inspect strips self for types but not the underlying methods.
        def dummy(self):
            pass
        tgt = dummy
        has_args_offset = True

    if has_partial and has_args_offset:
        # TODO: unwrap partials masking parameters like modern python
        raise InjectionInspectionError(
            'Injector inspection does not currently support both an args offset and a functools.partial: '
            f'{obj}',
        )

    return InjectionInspection(
        obj,
        uw,
        tgt,

        inspect.signature(tgt),
        ta.get_type_hints(uw),
        1 if has_args_offset else 0,
    )


def injection_inspect(obj: ta.Any) -> InjectionInspection:
    try:
        return _INJECTION_INSPECTION_CACHE[obj]
    except TypeError:
        return _do_injection_inspect(obj)
    except KeyError:
        pass

    insp = _do_injection_inspect(obj)
    _INJECTION_INSPECTION_CACHE[obj] = insp
    return insp
