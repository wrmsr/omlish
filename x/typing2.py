import functools
import inspect
import typing as ta


##


_MISSING = object()


def _update_wrapper_no_anns(wrapper, wrapped):
    functools.update_wrapper(wrapper, wrapped, assigned=list(set(functools.WRAPPER_ASSIGNMENTS) - {'__annotations__'}))
    return wrapper


#


def _make_typed_lambda(fn, **kw):  # noqa
    ret = kw.pop('return', _MISSING)
    for k in kw:
        if k.startswith('__'):
            raise NameError(k)

    ns = {}
    ns['__fn'] = fn

    proto = ['def __lam(']
    call = ['return __fn(']

    for i, (n, t) in enumerate(kw.items()):
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

    return ns['__lam']


class _TypedLambda:
    def __init_(self, fn, kw):
        super().__init__()

        self._fn = fn
        self._kw = kw

        self._lam = _make_typed_lambda(fn, **kw)

        _update_wrapper_no_anns(self, fn)
        self.__signature__ = inspect.signature(self._lam, follow_wrapped=False)

    def __reduce__(self):
        return (_TypedLambda, (self._fn, self._kw))

    def __call__(self, *args, **kwargs):
        return self._lam(*args, **kwargs)


def typed_lambda(return_=_MISSING, **kw):  # noqa
    def inner(fn):
        return _TypedLambda(fn, {'return': return_, **kw})
    for k in kw:
        if k.startswith('__'):
            raise NameError(k)
    return inner


#


class _TypedPartial:
    def __init__(self, obj, kw):
        super().__init__()

        self._obj = obj
        self._kw = kw

        sig = inspect.signature(obj)
        ret: ta.Any
        if isinstance(obj, type):
            ret = obj
        elif sig.return_annotation is not inspect.Signature.empty:
            ret = sig.return_annotation
        else:
            ret = _MISSING

        inner = _update_wrapper_no_anns(lambda **lkw: obj(**lkw, **kw), obj)
        self._lam = _make_typed_lambda(
            inner,
            **{'return': ret},
            **{
                n: p.annotation
                for n, p in sig.parameters.items()
                if n not in kw
                   and p.annotation is not inspect.Signature.empty
            },
        )

        _update_wrapper_no_anns(self, obj)
        self.__signature__ = inspect.signature(self._lam, follow_wrapped=False)

    def __reduce__(self):
        return (_TypedPartial, (self._obj, self._kw))

    def __call__(self, *args, **kwargs):
        return self._lam(*args, **kwargs)


def typed_partial(obj, **kw):  # noqa
    for k in kw:
        if k.startswith('__'):
            raise NameError(k)
