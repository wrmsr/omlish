import typing as ta


##


class ProtocolForbiddenAsBaseClass(ta.Protocol):
    pass


class ProtocolForbiddenAsBaseClassTypeError(TypeError):
    pass


def _ProtocolForbiddenAsBaseClass__init_subclass__(cls: ta.Any, **kwargs: ta.Any) -> None:  # noqa
    if ta.Protocol not in cls.__mro__:
        raise TypeError(f'Class {cls} must be a Protocol')

    super(ProtocolForbiddenAsBaseClass, cls).__init_subclass__(**kwargs)  # noqa

    # TODO: ta.Protocol not in cls.__bases__ ?
    if not cls.__dict__['_is_protocol']:
        raise ProtocolForbiddenAsBaseClassTypeError(cls)


setattr(ProtocolForbiddenAsBaseClass, '__init_subclass__', classmethod(_ProtocolForbiddenAsBaseClass__init_subclass__))
