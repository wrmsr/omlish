"""
TODO:
 - the point of these is that there are ~many~ tools that only properly inspect real, honest functions - no args/kwargs
   proxies, no method binding, no descriptors, nothing. we need a function with a custom pickler.
  - generate a class? speed is no concern, but it doesn't get all the way there - now we have pickling, and a def
    __call__ with a proper signature, but it either has to have `self` *or* be a static/classmethod, both of which are
    unacceptable.
  - can we subclass types.FunctionType? no lol, but can we get close?
 - alright, well, try a method
  - can distinguish between types.FunctionType and types.MethodType, do that more
  - exec a class Foo(_TypedLambda):

==

In [6]: %timeit exec('def foo(*a, x=0, **k): return (a, x, k)')
7.77 μs ± 117 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)

In [7]: %timeit exec('\n'.join(['class C:', '  def foo(self, *a, x=0, **k): return (a, x, k)']))
12.9 μs ± 48.9 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
"""
import functools
import inspect
import typing as ta


P = ta.ParamSpec('P')
T = ta.TypeVar('T')


##


def _update_wrapper_no_anns(wrapper, wrapped):
    functools.update_wrapper(
        wrapper,
        wrapped,
        assigned=list(set(functools.WRAPPER_ASSIGNMENTS) - {'__annotations__'}),
    )
    return wrapper


#


_MISSING = object()


class _RenderedTypedLambda(ta.NamedTuple):
    proto: str
    call: str
    ns: dict[str, ta.Any]


def _render_typed_lambda(fn: ta.Any, *pps: str, **kw: ta.Any) -> _RenderedTypedLambda:
    ret = kw.pop('return', _MISSING)
    for k in kw:
        if k.startswith('__'):
            raise NameError(k)

    ns = {}
    ns['__fn'] = fn

    proto = [f'def __call__(']
    call = ['return __fn(']

    if pps:
        for i, pp in enumerate(pps):
            if i:
                proto.append(', ')
            proto.append(pp)
        proto.append(', /')

    if kw:
        if pps:
            proto.append(', ')
        proto.append('*')

    for i, (n, t) in enumerate(kw.items()):
        if i:
            call.append(', ')
        ns['__ann_' + n] = t
        proto.append(f', {n}: __ann_{n}')
        call.append(f'{n}={n}')

    proto.append(')')

    if ret is not _MISSING:
        ns['__ann_return'] = ret
        proto.append(f' -> __ann_return')

    proto.append(':')
    call.append(')')

    return _RenderedTypedLambda(
        ''.join(proto),
        ''.join(call),
        ns,
    )


def _make_typed_lambda_fn(fn, *pps, **kw):
    rtl = _render_typed_lambda(fn, *pps, **kw)
    src = f'{rtl.proto} {rtl.call}'
    exec(src, rtl.ns)
    return rtl.ns['__call__']


_TYPED_LAMBDA_SELF_ARG = '__self'


class _TypedLambda:
    __typed_lambda_fn__: ta.ClassVar[ta.Any]
    __typed_lambda_kw__: ta.ClassVar[ta.Mapping[str, ta.Any]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

        fn = cls.__dict__['__typed_lambda_fn__']
        cls.__call__ = _make_typed_lambda_fn(fn, _TYPED_LAMBDA_SELF_ARG, **cls.__typed_lambda_kw__)
        _update_wrapper_no_anns(cls.__call__, fn)

        # update_wrapper sets __call__.__name__, and method unpickling machinery getattr's by __name__ after
        # instantiating __self__, so that needs to return the proxy. this might blow up with bad names, but we'll burn
        # that bridge if we come to it.
        setattr(cls, cls.__call__.__name__, cls.__call__)

    def __reduce__(self):
        cls = self.__class__
        fn = cls.__dict__['__typed_lambda_fn__']
        return (_make_typed_lambda_cls_inst, (fn, cls.__typed_lambda_kw__))


def _make_typed_lambda_cls(fn, kw):
    return type(
        '$_TypedLambdaInstance',  # TODO: mangle fn/kw into class name
        (_TypedLambda,),
        dict(
            __typed_lambda_fn__=fn,
            __typed_lambda_kw__=kw,
        ),
    )


def _make_typed_lambda_cls_inst(fn, kw):
    return _make_typed_lambda_cls(fn, kw)()


def _make_typed_lambda_cls_fn(fn, kw):
    cls = _make_typed_lambda_cls(fn, kw)
    return cls().__call__


def typed_lambda(
        return_: ta.Any = _MISSING,
        **kw: ta.Any,
) -> ta.Callable[[ta.Callable[P, T]], ta.Callable[P, T]]:  # noqa
    def inner(fn):
        return _make_typed_lambda_cls_fn(
            fn,
            {
                **({'return': return_} if return_ is not _MISSING else {}),
                **kw,
            },
        )

    for k in kw:
        if k.startswith('__'):
            raise NameError(k)

    return inner  # type: ignore


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
        self._lam = _make_typed_lambda_fn(
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
    return _TypedPartial(obj, kw)


##


class _Foo:
    def __init__(self, z):
        self.z = z

    def __call__(self, x, y):
        return x + y + self.z


def _foo(x, y):
    return x + y


def _main() -> None:
    import pickle
    f = _Foo(3).__call__
    assert f(1, 2) == 6
    fp = pickle.dumps(f)
    f2 = pickle.loads(fp)
    assert f2(1, 2) == 6

    l = typed_lambda(x=int, y=int)(_foo)
    assert l(x=3, y=4) == 7
    assert ta.get_type_hints(l) == {'x': int, 'y': int}

    import pickle
    lp = pickle._dumps(l)
    l2 = pickle._loads(lp)
    assert l2(x=3, y=4) == 7
    assert ta.get_type_hints(l2) == {'x': int, 'y': int}

    p = typed_partial(l, x=5)
    assert p(y=4) == 9
    assert ta.get_type_hints(p) == {'y': int}


if __name__ == '__main__':
    _main()
