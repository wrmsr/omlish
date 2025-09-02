"""
TODO:
 - typed_lambda is really kinda just 'annotate'
 - TypedLambda / TypedPartial classes, picklable, reprs
  - probably need to gen types per inst
 - typed_factory
"""
import inspect
import typing as ta

from ..lite.wrappers import update_wrapper_no_annotations


Ty = ta.TypeVar('Ty', bound=type)

T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)
T_contra = ta.TypeVar('T_contra', contravariant=True)

# FIXME: remove? ducktyped by mypy (with memoryview)
BytesLike: ta.TypeAlias = bytes | bytearray


##


class static_check_isinstance(ta.Generic[T]):  # noqa
    def __init__(self, *o: T) -> None:
        pass

    def __call__(self, o: T) -> T:
        return o


class static_check_issubclass(ta.Generic[T]):  # noqa
    def __init__(self, *t: type[T]) -> None:
        pass

    def __call__(self, t: type[T]) -> type[T]:
        return t


def copy_type(o: T) -> ta.Callable[[ta.Any], T]:
    """https://github.com/python/typing/issues/769#issuecomment-903760354"""

    return lambda x: x


##


def protocol_check(proto: type) -> ta.Callable[[Ty], Ty]:
    def inner(cls):
        if not issubclass(cls, proto):
            raise TypeError(cls)
        return cls
    return inner


##


_MISSING = object()


def typed_lambda(ret=_MISSING, **kw):  # noqa
    def inner(fn):
        ns = {}
        ns['__fn'] = fn

        proto = ['def __lam(']
        call = ['return __fn(']

        pkw = dict(kw)
        for i, (n, t) in enumerate(pkw.items()):
            if i:
                call.append(', ')
            else:
                proto.append('*')

            ns['__ann_' + n] = t
            proto.append(f', {n}: __ann_{n}')
            call.append(f'{n}={n}')

        proto.append(')')

        if ret is not _MISSING:
            ns['__ann_return'] = ret
            proto.append(f' -> __ann_return')

        proto.append(':')
        call.append(')')

        src = f'{"".join(proto)} {"".join(call)}'
        exec(src, ns)

        lam = update_wrapper_no_annotations(ns['__lam'], fn)
        lam.__signature__ = inspect.signature(lam, follow_wrapped=False)
        return lam

    for k in kw:
        if k.startswith('__'):
            raise NameError(k)

    return inner


def typed_partial(obj, **kw):  # noqa
    for k in kw:
        if k.startswith('__'):
            raise NameError(k)

    sig = inspect.signature(obj)

    inner = update_wrapper_no_annotations(lambda **lkw: obj(**lkw, **kw), obj)

    ret = (
        obj if isinstance(obj, type) else
        sig.return_annotation if sig.return_annotation is not inspect.Signature.empty else
        _MISSING
    )

    lam = typed_lambda(
        ret,
        **{
            n: p.annotation
            for n, p in sig.parameters.items()
            if n not in kw
            and p.annotation is not inspect.Signature.empty
        },
    )(inner)

    return update_wrapper_no_annotations(lam, obj)


##


class SequenceNotStr(ta.Protocol[T_co]):
    """
    https://github.com/python/mypy/issues/11001
    https://github.com/python/typing/issues/256#issuecomment-1442633430
    https://github.com/hauntsaninja/useful_types/blob/735ef9dd0b55b35b118ef630d5a0f3618ecedbff/useful_types/__init__.py#L285
    """

    @ta.overload
    def __getitem__(self, index: ta.SupportsIndex, /) -> T_co: ...

    @ta.overload
    def __getitem__(self, index: slice, /) -> ta.Sequence[T_co]: ...  # noqa

    def __contains__(self, value: object, /) -> bool: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> ta.Iterator[T_co]: ...

    def index(self, value: ta.Any, start: int = 0, stop: int = ..., /) -> int: ...

    def count(self, value: ta.Any, /) -> int: ...

    def __reversed__(self) -> ta.Iterator[T_co]: ...
