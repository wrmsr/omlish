# ruff: noqa: UP006
# @omlish-lite
import abc
import typing as ta


##


_ABSTRACT_METHODS_ATTR = '__abstractmethods__'
_IS_ABSTRACT_METHOD_ATTR = '__isabstractmethod__'
_FORCE_ABSTRACT_ATTR = '__forceabstract__'


def update_abstracts(cls, *, force=False):
    if not force and not hasattr(cls, _ABSTRACT_METHODS_ATTR):
        # Per stdlib: We check for __abstractmethods__ here because cls might by a C implementation or a python
        # implementation (especially during testing), and we want to handle both cases.
        return cls

    abstracts: ta.Set[str] = set()

    for scls in cls.__bases__:
        for name in getattr(scls, _ABSTRACT_METHODS_ATTR, ()):
            value = getattr(cls, name, None)
            if getattr(value, _IS_ABSTRACT_METHOD_ATTR, False):
                abstracts.add(name)

    for name, value in cls.__dict__.items():
        if getattr(value, _IS_ABSTRACT_METHOD_ATTR, False):
            abstracts.add(name)

    setattr(cls, _ABSTRACT_METHODS_ATTR, frozenset(abstracts))
    return cls


#


class AbstractTypeError(TypeError):
    pass


class Abstract:
    """
    Different from, but interoperable with, abc.ABC / abc.ABCMeta:

     - This raises AbstractTypeError during class creation, not instance instantiation.
     - This is a mixin, not a metaclass.
     - As it is not an ABCMeta, this does not support virtual base classes. As a result, operations like `isinstance`
       and `issubclass` are ~7x faster.

    If not mixed-in with an ABCMeta, it will update __abstractmethods__ itself.
    """

    __slots__ = ()

    __abstractmethods__: ta.ClassVar[ta.FrozenSet[str]] = frozenset()

    #

    def __forceabstract__(self):
        raise TypeError

    # This is done manually, rather than through @abc.abstractmethod, to mask it from static analysis.
    setattr(__forceabstract__, _IS_ABSTRACT_METHOD_ATTR, True)

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        setattr(
            cls, _FORCE_ABSTRACT_ATTR,
            getattr(Abstract, _FORCE_ABSTRACT_ATTR) if Abstract in cls.__bases__ else False,
        )

        super().__init_subclass__(**kwargs)

        if not (Abstract in cls.__bases__ or abc.ABC in cls.__bases__):
            ams = {a: cls for a, o in cls.__dict__.items() if is_abstract_method(o)}

            seen = set(cls.__dict__)
            for b in cls.__bases__:
                ams.update({a: b for a in set(getattr(b, _ABSTRACT_METHODS_ATTR, [])) - seen})  # noqa
                seen.update(dir(b))

            if ams:
                raise AbstractTypeError(
                    f'Cannot subclass abstract class {cls.__name__} with abstract methods: ' +
                    ', '.join(sorted([
                        '.'.join([
                            *([m] if (m := getattr(c, '__module__')) else []),
                            getattr(c, '__qualname__', getattr(c, '__name__')),
                            a,
                        ])
                        for a, c in ams.items()
                    ])),
                )

        if not isinstance(cls, abc.ABCMeta):
            update_abstracts(cls, force=True)


def is_abstract_method(obj: ta.Any) -> bool:
    return bool(getattr(obj, _IS_ABSTRACT_METHOD_ATTR, False))
