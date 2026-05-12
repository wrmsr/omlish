import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish import typedvalues as tv


##


@ta.final
class DisableDynamicClassMarshaling(msh.Option, tv.UniqueTypedValue, lang.Final):
    pass


@ta.final
class EnableDynamicClassUnmarshaling(msh.Option, tv.UniqueTypedValue, lang.Final):
    pass


class DynamicClassForbiddenMarshalError(msh.MarshalError):
    pass
