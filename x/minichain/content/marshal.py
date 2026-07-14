import typing as ta

from omcore import lang
from omcore import marshal as msh
from omcore import typedvalues as tv


##


@ta.final
class DisableDynamicClassMarshaling(msh.Option, tv.UniqueTypedValue, lang.Final):
    pass


@ta.final
class EnableDynamicClassUnmarshaling(msh.Option, tv.UniqueTypedValue, lang.Final):
    pass


class DynamicClassForbiddenMarshalError(msh.MarshalError):
    pass
