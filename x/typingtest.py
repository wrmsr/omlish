import functools
import inspect
import typing as ta


##


_ANN_ATTRS: ta.AbstractSet[str] = {
    '__annotations__',
    '__annotate__',
}

_UPDATE_WRAPPER_ASSIGNED_NO_ANNS = list(set(functools.WRAPPER_ASSIGNMENTS) - _ANN_ATTRS)  # noqa


def _update_wrapper_no_anns(wrapper, wrapped):
    functools.update_wrapper(wrapper, wrapped, assigned=_UPDATE_WRAPPER_ASSIGNED_NO_ANNS)
    return wrapper


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


if __name__ == '__main__':
    l = typed_lambda(x=int, y=int)(lambda x, y: x + y)
    assert l(x=3, y=4) == 7
    assert ta.get_type_hints(l) == {'x': int, 'y': int}

    p = typed_partial(l, x=5)
    assert p(y=4) == 9
    assert ta.get_type_hints(p) == {'y': int}
