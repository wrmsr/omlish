"""
TODO:
 - typed_lambda is really kinda just 'annotate'
 - TypedLambda / TypedPartial classes, picklable, reprs
  - probably need to gen types per inst
 - typed_factory
"""
import dataclasses as dc
import functools
import inspect
import typing as ta


Ty = ta.TypeVar('Ty', bound=type)

T = ta.TypeVar('T')
A0 = ta.TypeVar('A0')
A1 = ta.TypeVar('A1')
A2 = ta.TypeVar('A2')


BytesLike: ta.TypeAlias = bytes | bytearray


##


def protocol_check(proto: type) -> ta.Callable[[Ty], Ty]:
    def inner(cls):
        if not issubclass(cls, proto):
            raise TypeError(cls)
        return cls
    return inner


##


_MISSING = object()


def _update_wrapper_no_anns(wrapper, wrapped):
    functools.update_wrapper(wrapper, wrapped, assigned=list(set(functools.WRAPPER_ASSIGNMENTS) - {'__annotations__'}))
    return wrapper


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
        lam = _update_wrapper_no_anns(ns['__lam'], fn)
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
    inner = _update_wrapper_no_anns(lambda **lkw: obj(**lkw, **kw), obj)
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
    return _update_wrapper_no_anns(lam, obj)


##
# A workaround for typing deficiencies (like `Argument 2 to NewType(...) must be subclassable`).


@dc.dataclass(frozen=True)
class Func0(ta.Generic[T]):
    fn: ta.Callable[[], T]

    def __call__(self) -> T:
        return self.fn()


@dc.dataclass(frozen=True)
class Func1(ta.Generic[A0, T]):
    fn: ta.Callable[[A0], T]

    def __call__(self, a0: A0) -> T:
        return self.fn(a0)


@dc.dataclass(frozen=True)
class Func2(ta.Generic[A0, A1, T]):
    fn: ta.Callable[[A0, A1], T]

    def __call__(self, a0: A0, a1: A1) -> T:
        return self.fn(a0, a1)


@dc.dataclass(frozen=True)
class Func3(ta.Generic[A0, A1, A2, T]):
    fn: ta.Callable[[A0, A1, A2], T]

    def __call__(self, a0: A0, a1: A1, a2: A2) -> T:
        return self.fn(a0, a1, a2)
